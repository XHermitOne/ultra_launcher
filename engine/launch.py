# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль содержит функции непосредственного
исполнения комманд из файла cmd_filename.
"""

import os
import os.path
import stat
import time
import threading

from .util import config
from .util import log_func
from . import global_data

__version__ = (0, 0, 3, 1)

# Конфигурационный файл по умолчанию
DEFAULT_CFG_FILENAME = os.path.join(os.path.dirname(__file__), 'default.cfg')

# Признак запущенного цикла
IS_LOOP_RUN = False

# Задержка в секундах
# ВНИМАНИЕ! Раньше этот параметр стоял как 0.1,
# но после того как в многокоммандном файле перестали выполняться последние
# команды, я увеличил время задержки до 3.
SLEEP_LOOP_RUN = 0.1

# Таймаут чтения коммандного файла
READ_CMD_FILE_TIMEOUT = 0.1

# Флаг разрешения смены иконки в трее
CAN_CHANGE_TRAY_ICONS = False


# Реализация в виде функций
def isLoopRun():
    """
    Цикл прослушки запущен?
    """
    global IS_LOOP_RUN
    return IS_LOOP_RUN


def startLoop(cfg_filename=DEFAULT_CFG_FILENAME):
    """
    Запустить цикл.

    @param cfg_filename: Полное имя конфигурационного файла.
    """
    global IS_LOOP_RUN
    IS_LOOP_RUN = True

    try:
        threading.Thread(target=listenLoopCfg, args=(cfg_filename, )).start()
    except:
        log_func.fatal('Ошибка запуска цикла прослушивания')


def stopLoop():
    """
    Остановить цикл.
    """
    global IS_LOOP_RUN
    IS_LOOP_RUN = False


def isLockedFile(filename):
    """
    Проверка заблокирован ли файл на запись.
    @param filename: Полное имя файла.
    """
    file = None
    try:
        file = os.open(filename, os.O_RDWR | os.O_EXCL,
                       mode=stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        result = False
    except OSError:
        time.sleep(SLEEP_LOOP_RUN)
        # Файл заблокирован
        result = True
    else:
        if file:
            os.close(file)
    return result


def listenLoopCfg(cfg_filenames=DEFAULT_CFG_FILENAME):
    """
    Запуск цикла прослушки и исполнения коммандного фaйла
    согласно конфигурационному файлу.

    @param cfg_filenames: Полное имя конфигурационного файла.
    """
    if os.path.exists(cfg_filenames):
        cfg = config.UltraConfig()
        cfg.parseConfig(cfg_filenames)

        cmd_dir = os.path.dirname(cfg.cmd_filename)
        if not os.path.exists(cmd_dir):
            log_func.warning('Command directory %s not found!' % cmd_dir)
            os.makedirs(cmd_dir)
            log_func.info('Create directory %s' % cmd_dir)

        return listenLoopCmdFile(cfg.cmd_filename, cfg.replaces)
    else:
        log_func.warning('Config file %s not found!' % cfg_filenames)


def listenLoopCmdFile(cmd_filename, replaces=None):
    """
    Запуск цикла прослушки и исполнения коммандного фaйла.

    @param cmd_filename: Полное имя коммандного файла.
    @param replaces: Словарь автозамен.
    """
    log_func.info('Enter listen loop')
    while isLoopRun():
        time.sleep(SLEEP_LOOP_RUN)
        # Если коммандный файл существует и он не заблокирован,
        # то выполнить его
        if os.path.exists(cmd_filename) and not isLockedFile(cmd_filename):
            runCommandFile(cmd_filename, replaces)
    log_func.info('Exit listen loop')


def runCommandFile(cmd_filename, replaces=None, encoding='utf-8'):
    """
    Исполнение командного файла и удаление его по завершении.

    @param cmd_filename: Полное имя командного файла.
    @param replaces: Словарь/список автозамен.
    @param encoding: Кодовая страница коммандной строки.
    """
    log_func.info('Run file: %s' % cmd_filename)
    if os.path.exists(cmd_filename) and os.path.getsize(cmd_filename):
        cmd_file = None
        try:
            cmd_file = open(cmd_filename, 'r')
            cmd_lines = cmd_file.readlines()
            # ВНИМАНИЕ! Здесь небходимо сразу закрыть и
            # удалить файл. Иначе ресурс остается заблокированным!
            cmd_file.close()
            cmd_file = None
            # Удалить файл
            os.remove(cmd_filename)
            log_func.info(u'Штатное удаление файла <%s>' % cmd_filename)

            if encoding not in ('utf-8', 'utf8'):
                for i, cmd_line in enumerate(cmd_lines):
                    cmd_lines[i] = str(cmd_line)    #, encoding).encode('utf-8')

            try:
                for i, cmd_line in enumerate(cmd_lines):
                    log_func.info('%d. CMD line: %s' % (i, cmd_line.strip()))
            except:
                log_func.fatal(u'Ошибка Кодирования-Декодирования Unicode')

            if global_data.getGlobal('REMOVE_DOUBLE_COMMANDS'):
                # Убрать дублирующие команды (беруться только последние команды)
                result_cmd_lines = list()
                for i, cmd_line in enumerate(cmd_lines):
                    if cmd_line not in cmd_lines[i+1:]:
                        result_cmd_lines.append(cmd_line)
                cmd_lines = result_cmd_lines

            for cmd_line in cmd_lines:
                if cmd_line:
                    _runCommand(cmd_line, replaces)

            return True
        except:
            if cmd_file:
                cmd_file.close()
            log_func.fatal(u'Error in function runCommandFile')
            raise
    else:
        log_func.warning('Command file <%s> not correct' % cmd_filename)
        time.sleep(READ_CMD_FILE_TIMEOUT)
        # Если файл после задержки по прежнему пуст,
        # то необходимо удалить его
        if not os.path.getsize(cmd_filename):
            os.remove(cmd_filename)
            log_func.info(u'Удаление не корректного коммандного файла <%s>' % cmd_filename)

    return False


def _runCommand(command, replaces=None):
    """
    Выполнение одной комманды/строки коммандного файла.

    @param command: Текст комманды.
    @param replaces: Словарь/список автозамен.
    """
    new_command = _autoReplace(command, replaces)
    log_func.info('Run command: %s' % new_command)
    try:
        os.system(new_command)
    except:
        # log_func.error('Run: %s' % new_command)
        log_func.error('Command: %s' % command)
        raise


def _autoReplace(text, replaces=None):
    """
    Произвести автозамены в тексте.
    @param text: Текст.
    @param replaces: Словарь/список автозамен.
    @return: Возвращает отредактированный текст.
    """
    # Убрать все переводы каретки и пробелы
    text = text.strip()
    # Обязательно заменить слеши в путях
    text = text.replace('\\', '/')
    
    if isinstance(replaces, dict):
        # Замены могут задаваться словарем или списком
        replaces = replaces.items()
    elif type(replaces) in (list, tuple):
        replaces = replaces
    else:
        log_func.warning('Auto replace. Not support replaces type <%s>' % type(replaces))
        return text
    
    if replaces:
        for replace_src, replace_dst in replaces:
            try:
                # log_func.debug('Text <%s> replace <%s> -> <%s>' % (text, replace_src, replace_dst))
                if replace_src in text:
                    text = text.replace(replace_src, replace_dst)
                    # ВНИМАНИЕ! Если текст замены заканчивается на кавычку
                    # то подразумевается что весь текст, следующий за надо заменяемым
                    # необходимо обрамить этими кавычками
                    if replace_dst[-1] in ('\'', '\"'):
                        text += replace_dst[-1]
            except:
                log_func.error('Replace %s to %s in text %s' % (replace_src,
                                                                replace_dst, text))
                raise
    # Возможно неправильное оформление параметров коммандной строки
    text = text.replace('= ', '=')
    return text


def runCommandCfg(cfg_filename=DEFAULT_CFG_FILENAME):
    """
    Запуск на исполнение файла в соответствии с конфигурационным файлом.
    @param cfg_filename: Полное имя конфигурационного файла.
    """
    if os.path.exists(cfg_filename):
        cfg = config.UltraConfig()
        cfg.parseConfig(cfg_filename)

        if not os.path.exists(cfg.cmd_filename):
            log_func.warning('Command file %s not found!' % cfg.cmd_filename)
        return runCommandFile(cfg.cmd_filename, cfg.replaces_list, encoding=cfg.shell_encode)
    else:
        log_func.warning('Config file %s not found!' % cfg_filename)
    return False


class UltraLaunchManager:
    """
    Менеджер управления исполнением файла.
    Реализация в виде класса менеджера.
    """
    def __init__(self, task_bar=None):
        """
        Конструктор.

        @param task_bar: Панель задач для отображения состояния исполнения.
        """
        self.task_bar = task_bar

        self.is_loop_run = False

        # Счетчики периодов
        self.period_counter = {}

    def isLoopRun(self):
        """
        Цикл прослушки запущен?
        """
        return self.is_loop_run

    def startLoop(self, cfg_filename=DEFAULT_CFG_FILENAME):
        """
        Запустить цикл.

        @param cfg_filename: Полное имя конфигурационного файла.
        """
        self.is_loop_run = True

        try:
            threading.Thread(target=listenLoopCfg, args=(cfg_filename, )).start()
        except:
            log_func.fatal('Ошибка запуска цикла прослушивания')

    def stopLoop(self):
        """
        Остановить цикл.
        """
        self.is_loop_run = False

    def listenLoopCfg(self, cfg_filename=DEFAULT_CFG_FILENAME):
        """
        Запуск цикла прослушки и исполнения командного фaйла
        согласно конфигурационному файлу.

        @param cfg_filename: Полное имя конфигурационного файла.
        """
        if os.path.exists(cfg_filename):
            cfg = config.UltraConfig()
            cfg.parseConfig(cfg_filename)

            cmd_dir = os.path.dirname(cfg.cmd_filename)
            if not os.path.exists(cmd_dir):
                log_func.warning('Command directory %s not found!' % cmd_dir)
                os.makedirs(cmd_dir)
                log_func.info('Create directory %s' % cmd_dir)

            return self.listenLoop(cfg.cmd_filename,
                                   cfg.replaces, cfg.cmd_period,
                                   encoding=cfg.shell_encode)
        else:
            log_func.warning('Config file %s not found!' % cfg_filename)

    def listenLoopCmdFile(self, cmd_filename, replaces=None, encoding='utf-8'):
        """
        Запуск цикла прослушки и исполнения командного фaйла.

        @param cmd_filename: Полное имя командного файла.
        @param replaces: Словарь автозамен.
        @param encoding: Кодовая страница командной строки.
        """
        log_func.info('Enter listen loop')
        while self.isLoopRun():
            time.sleep(SLEEP_LOOP_RUN)
            # Если командный файл существует и он не заблокирован,
            # то выполнить его
            if os.path.exists(cmd_filename) and not isLockedFile(cmd_filename):

                if self.task_bar and CAN_CHANGE_TRAY_ICONS:
                    self.task_bar.changeIcon('run')

                try:
                    runCommandFile(cmd_filename, replaces, encoding)
                except:
                    log_func.fatal(u'Ошибка выполнения коммандного файла <%s>' % cmd_filename)

                if self.task_bar and CAN_CHANGE_TRAY_ICONS:
                    self.task_bar.changeIcon('loop')

        log_func.info('Exit listen loop')

    def listenLoop(self, cmd_filename, replaces=None, period_commands=None, encoding='utf-8'):
        """
        Запуск цикла прослушки и исполнения.

        @param cmd_filename: Полное имя командного файла.
        @param replaces: Словарь автозамен.
        @param period_commands: Словарь периодического автозапуска команд.
        @param encoding: Кодовая страница командной строки.
        """
        log_func.info('Enter listen loop')

        # Инициализировать счетчики периодов
        self.initPeriodCounter(period_commands)

        while self.isLoopRun():
            time.sleep(SLEEP_LOOP_RUN)
            # Если коммандный файл существует и он не заблокирован,
            # то выполнить его
            if os.path.exists(cmd_filename) and not isLockedFile(cmd_filename):

                if self.task_bar and CAN_CHANGE_TRAY_ICONS:
                    self.task_bar.changeIcon('run')

                try:
                    runCommandFile(cmd_filename, replaces, encoding)
                except:
                    log_func.fatal(u'Ошибка выполнения командного файла <%s>' % cmd_filename)

                if self.task_bar and CAN_CHANGE_TRAY_ICONS:
                    self.task_bar.changeIcon('loop')

            else:
                # Если не исполняется коммандный файл, то
                # исполнять команды периодического автозапуска
                if period_commands:
                    self.runPeriodCommands(period_commands, replaces)

        log_func.info('Exit listen loop')

    def runPeriodCommands(self, period_commands=None, replaces=None):
        """
        Запуск исполнения команд периодического автозапуска.

        @param period_commands: Словарь периодического автозапуска комманд.
        @param replaces: Словарь автозамен.
        """
        # Прочитать текущее время
        cur_time = time.time()

        for interval, count_time in self.period_counter.values():
            # Посмотреть по счетчику не пора ли выполнить комманды
            if (cur_time-count_time) >= interval:

                if self.task_bar and CAN_CHANGE_TRAY_ICONS:
                    self.task_bar.changeIcon('run')

                try:
                    for cmd in period_commands[interval]:
                        _runCommand(cmd, replaces)
                    # Сохранить значение в счетчике
                    self.period_counter[interval] = cur_time
                except:
                    log_func.fatal(u'Ошибка исполнения команд периодического автозапуска')

                if self.task_bar and CAN_CHANGE_TRAY_ICONS:
                    self.task_bar.changeIcon('loop')

    def initPeriodCounter(self, period_commands=None):
        """
        Инициализация счетчиков для всех периодов.

        @param period_commands: Словарь периодического автозапуска комманд.
        """
        self.period_counter = {}
        if period_commands:
            # Сначала проверить существуют ли счетчики для всех периодов
            for interval in period_commands.keys():
                if interval not in self.period_counter:
                    # Надо не забывать что time.time()
                    # возвращает значение в миллисекундах
                    self.period_counter[interval] = time.time()
        return self.period_counter

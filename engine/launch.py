# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль содержит функции непосредственного
исполнения комманд из файла CommandFile_.
"""

import os
import os.path
import time
import thread

import config
from services.ic_std.log import log

__version__ = (0, 0, 1, 1)

# Конфигурационный файл по умолчанию
DEFAULT_CFG_FILE_NAME = os.path.join(os.path.dirname(__file__), 'default.cfg')

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


def startLoop(CfgFileName_=DEFAULT_CFG_FILE_NAME):
    """
    Запустить цикл.
    @param CfgFileName_: Полное имя конфигурационного файла.
    """
    global IS_LOOP_RUN
    IS_LOOP_RUN = True

    thread.start_new_thread(listen_loop_cfg, (CfgFileName_,))


def stopLoop():
    """
    Остановить цикл.
    """
    global IS_LOOP_RUN
    IS_LOOP_RUN = False


def is_locked_file(FileName_):
    """
    Проверка заблокирован ли файл на запись.
    @param FileName_: Полное имя файла.
    """
    file = None
    try:
        file = os.open(FileName_, os.O_RDWR | os.O_EXCL, 0777)
        result = False
    except OSError:
        time.sleep(SLEEP_LOOP_RUN)
        # Файл заблокирован
        result = True
    else:
        if file:
            os.close(file)
    return result


def listen_loop_cfg(CfgFileName_=DEFAULT_CFG_FILE_NAME):
    """
    Запуск цикла прослушки и исполнения коммандного фaйла
    согласно конфигурационному файлу.
    @param CfgFileName_: Полное имя конфигурационного файла.
    """
    if os.path.exists(CfgFileName_):
        cfg = config.CConfig()
        cfg.parseConfig(CfgFileName_)

        cmd_dir = os.path.dirname(cfg.cmd_filename)
        if not os.path.exists(cmd_dir):
            log.warning('Command directory %s not found!' % cmd_dir)
            os.makedirs(cmd_dir)
            log.info('Create directory %s' % cmd_dir)

        return listen_loop_file(cfg.cmd_filename, cfg.replaces)
    else:
        log.warning('Config file %s not found!' % CfgFileName_)


def listen_loop_file(CommandFile_, Replaces_=None):
    """
    Запуск цикла прослушки и исполнения коммандного фaйла.
    @param CommandFile_: Полное имя коммандного файла.
    @param Replaces_: Словарь автозамен.
    """
    log.info('Enter listen loop')
    while isLoopRun():
        time.sleep(SLEEP_LOOP_RUN)
        # Если коммандный файл существует и он не заблокирован,
        # то выполнить его
        if os.path.exists(CommandFile_) and not is_locked_file(CommandFile_):
            run_cmd_file(CommandFile_, Replaces_)
    log.info('Exit listen loop')


def run_cmd_file(CommandFile_, Replaces_=None, CP='utf-8'):
    """
    Исполнение коммандного файла и удаление его по завершении.
    @param CommandFile_: Полное имя коммандного файла.
    @param Replaces_: Словарь/список автозамен.
    @param CP: Кодовая страница коммандной строки.
    """
    log.info('Run file: %s' % CommandFile_)
    if os.path.exists(CommandFile_) and os.path.getsize(CommandFile_):
        cmd_file = None
        try:
            cmd_file = open(CommandFile_, 'r')
            cmd_lines = cmd_file.readlines()
            # ВНИМАНИЕ! Здесь небходимо сразу закрыть и
            # удалить файл. Иначе ресурс остается заблокированным!
            cmd_file.close()
            cmd_file = None
            # Удалить файл
            os.remove(CommandFile_)
            log.info(u'Штатное удаление файла <%s>' % CommandFile_)
            # Если после удаления файл все равно существует,
            # то это ошибка
            #while os.path.exists(CommandFile_):
            #    log.warning(u'Коммандный файл <%s> все равно существует после чтения для обработки. Повторное удаление' % CommandFile_)
            #    time.sleep(READ_CMD_FILE_TIMEOUT)
            #    os.remove(CommandFile_)
            #    time.sleep(READ_CMD_FILE_TIMEOUT)

            if CP not in ('utf-8', 'utf8'):
                for i, cmd_line in enumerate(cmd_lines):
                    cmd_lines[i] = unicode(cmd_line, CP).encode('utf-8')

            try:
                for i, cmd_line in enumerate(cmd_lines):
                    log.info('%d. CMD line: %s' % (i, cmd_line.strip()))
            except:
                log.fatal(u'Ошибка Кодирования-Декодирования Unicode')

            if config.REMOVE_DOUBLE_COMMANDS:
                # Убрать дублирующие команды (беруться только последние команды)
                result_cmd_lines = list()
                for i, cmd_line in enumerate(cmd_lines):
                    if cmd_line not in cmd_lines[i+1:]:
                        result_cmd_lines.append(cmd_line)
                cmd_lines = result_cmd_lines

            for cmd_line in cmd_lines:
                if cmd_line:
                    _run_cmd(cmd_line, Replaces_)

            return True
        except:
            if cmd_file:
                cmd_file.close()
            log.fatal(u'Error in function run_cmd_file')
            raise
    else:
        log.warning('Command file <%s> not correct' % CommandFile_)
        time.sleep(READ_CMD_FILE_TIMEOUT)
        # Если файл после задержки по прежнему пуст,
        # то необходимо удалить его
        if not os.path.getsize(CommandFile_):
            os.remove(CommandFile_)
            log.info(u'Удаление не корректного коммандного файла <%s>' % CommandFile_)


    return False


def _run_cmd(Command_, Replaces_=None):
    """
    Выполнение одной комманды/строки коммандного файла.
    @param Command_: Текст комманды.
    @param Replaces_: Словарь/список автозамен.
    """
    new_command = _auto_replace(Command_, Replaces_)
    log.info('Run command: %s' % new_command)
    try:
        os.system(new_command)
    except:
        # log.error('Run: %s' % new_command)
        log.error('Command: %s' % Command_)
        raise


def _auto_replace(Txt_, Replaces_=None):
    """
    Произвести автозамены в тексте.
    @param Txt_: Текст.
    @param Replaces_: Словарь/список автозамен.
    @return: Возвращает отредактированный текст.
    """
    # Убрать все переводы каретки и пробелы
    Txt_ = Txt_.strip()
    # Обязательно заменить слеши в путях
    Txt_ = Txt_.replace('\\', '/')
    
    if isinstance(Replaces_, dict):
        # Замены могут задаваться словарем или списком
        replaces = Replaces_.items()
    elif type(Replaces_) in (list, tuple):
        replaces = Replaces_
    else:
        log.warning('Auto replace. Not support replaces type <%s>' % type(Replaces_))
        return Txt_
    
    if replaces:
        for replace_src, replace_dst in replaces:
            if type(replace_src) == unicode:
                replace_src = replace_src.encode('utf-8')
            if type(replace_dst) == unicode:
                replace_dst = replace_dst.encode('utf-8')
            try:
                # log.debug('Text <%s> replace <%s> -> <%s>' % (Txt_, replace_src, replace_dst))
                if replace_src in Txt_:
                    Txt_ = Txt_.replace(replace_src, replace_dst)
                    # ВНИМАНИЕ! Если текст замены заканчивается на кавычку
                    # то подразумевается что весь текст, следующий за надо заменяемым
                    # необходимо обрамить этими кавычками
                    if replace_dst[-1] in ('\'', '\"'):
                        Txt_ += replace_dst[-1]
            except:
                log.error('Replace %s to %s in text %s' % (replace_src,
                                                           replace_dst, Txt_))
                raise

    # Возможно неправильное оформление параметров коммандной строки
    Txt_ = Txt_.replace('= ', '=')
    return Txt_


def run_cmd_cfg(CfgFileName_=DEFAULT_CFG_FILE_NAME):
    """
    Запуск на исполнение файла в соответствии с конфигурационным файлом.
    @param CfgFileName_: Полное имя конфигурационного файла.
    """
    if os.path.exists(CfgFileName_):
        cfg = config.CConfig()
        cfg.parseConfig(CfgFileName_)

        if not os.path.exists(cfg.cmd_filename):
            log.warning('Command file %s not found!' % cfg.cmd_filename)
        return run_cmd_file(cfg.cmd_filename, cfg.replaces_list, CP=cfg.shell_encode)
    else:
        log.warning('Config file %s not found!' % CfgFileName_)
    return False

# Функции тестирования


def test_run_cmd_file():
    """
    Тестирование функции run_cmd_file.
    """
    cmd_file_name = os.getcwd()+'/test/cmd_file.run'

    log.info('START test_run_cmd_file... %s' % cmd_file_name)
    start_time = time.time()
    result = run_cmd_file(cmd_file_name)
    log.info('STOP test_run_cmd_file... %s' % (time.time()-start_time))
    log.info('Test result = %s' % result)


def test_run_cmd_cfg():
    """
    Тестирование функции run_cmd_cfg.
    """
    cfg_file_name = os.getcwd()+'/default.cfg'

    log.info('START test_run_cmd_cfg... %s' % cfg_file_name)
    start_time = time.time()
    result = run_cmd_cfg(cfg_file_name)
    log.info('STOP test_run_cmd_cfg... %s' % time.time()-start_time)
    log.info('Test result = %s' % result)

# Реализация в виде класса менеджера


class icLaunchManager:
    """
    Менеджер управления исполнением файла.
    """
    def __init__(self, TaskBar_=None):
        """
        Конструктор.
        @param TaskBar_: Панель задач для отображения состояния исполнения.
        """
        self.task_bar = TaskBar_

        self.is_loop_run = False

        # Счетчики периодов
        self.period_counter = {}

    def isLoopRun(self):
        """
        Цикл прослушки запущен?
        """
        return self.is_loop_run

    def startLoop(self, CfgFileName_=DEFAULT_CFG_FILE_NAME):
        """
        Запустить цикл.
        @param CfgFileName_: Полное имя конфигурационного файла.
        """
        self.is_loop_run = True

        thread.start_new_thread(self.listen_loop_cfg, (CfgFileName_,))

    def stopLoop(self):
        """
        Остановить цикл.
        """
        self.is_loop_run = False

    def listen_loop_cfg(self, CfgFileName_=DEFAULT_CFG_FILE_NAME):
        """
        Запуск цикла прослушки и исполнения коммандного фaйла
        согласно конфигурационному файлу.
        @param CfgFileName_: Полное имя конфигурационного файла.
        """
        if os.path.exists(CfgFileName_):
            cfg = config.CConfig()
            cfg.parseConfig(CfgFileName_)

            cmd_dir = os.path.dirname(cfg.cmd_filename)
            if not os.path.exists(cmd_dir):
                log.warning('Command directory %s not found!' % cmd_dir)
                os.makedirs(cmd_dir)
                log.info('Create directory %s' % cmd_dir)

            return self.listen_loop(cfg.cmd_filename,
                                    cfg.replaces, cfg.cmd_period,
                                    CP=cfg.shell_encode)
        else:
            log.warning('Config file %s not found!' % CfgFileName_)

    def listen_loop_file(self, CommandFile_, Replaces_=None, CP='utf-8'):
        """
        Запуск цикла прослушки и исполнения коммандного фaйла.
        @param CommandFile_: Полное имя коммандного файла.
        @param Replaces_: Словарь автозамен.
        @param CP: Кодовая страница коммандной строки.
        """
        log.info('Enter listen loop')
        while self.isLoopRun():
            time.sleep(SLEEP_LOOP_RUN)
            # Если коммандный файл существует и он не заблокирован,
            # то выполнить его
            if os.path.exists(CommandFile_) and not is_locked_file(CommandFile_):

                if self.task_bar and CAN_CHANGE_TRAY_ICONS:
                    self.task_bar.changeIcon('run')

                try:
                    run_cmd_file(CommandFile_, Replaces_, CP)
                except:
                    log.fatal(u'Ошибка выполнения коммандного файла <%s>' % CommandFile_)

                if self.task_bar and CAN_CHANGE_TRAY_ICONS:
                    self.task_bar.changeIcon('loop')

        log.info('Exit listen loop')

    def listen_loop(self, CommandFile_, Replaces_=None,
                    PeriodCmd_=None, CP='utf-8'):
        """
        Запуск цикла прослушки и исполнения.
        @param CommandFile_: Полное имя коммандного файла.
        @param Replaces_: Словарь автозамен.
        @param PeriodCmd_: Словарь периодического автозапуска комманд.
        @param CP: Кодовая страница коммандной строки.
        """
        log.info('Enter listen loop')

        # Инициализировать счетчики периодов
        self.init_period_counter(PeriodCmd_)

        while self.isLoopRun():
            time.sleep(SLEEP_LOOP_RUN)
            # Если коммандный файл существует и он не заблокирован,
            # то выполнить его
            if os.path.exists(CommandFile_) and not is_locked_file(CommandFile_):

                if self.task_bar and CAN_CHANGE_TRAY_ICONS:
                    self.task_bar.changeIcon('run')

                try:
                    run_cmd_file(CommandFile_, Replaces_, CP)
                except:
                    log.fatal(u'Ошибка выполнения командного файла <%s>' % CommandFile_)

                if self.task_bar and CAN_CHANGE_TRAY_ICONS:
                    self.task_bar.changeIcon('loop')

            else:
                # Если не исполняется коммандный файл, то
                # исполнять команды периодического автозапуска
                if PeriodCmd_:
                    self.run_period_cmd(PeriodCmd_, Replaces_)

        log.info('Exit listen loop')

    def run_period_cmd(self, PeriodCmd_=None, Replaces_=None):
        """
        Запуск исполнения команд периодического автозапуска.
        @param PeriodCmd_: Словарь периодического автозапуска комманд.
        @param Replaces_: Словарь автозамен.
        """
        # Прочитать текущее время
        cur_time = time.time()

        for interval, count_time in self.period_counter.values():
            # Посмотреть по счетчику не пора ли выполнить комманды
            if (cur_time-count_time) >= interval:

                if self.task_bar and CAN_CHANGE_TRAY_ICONS:
                    self.task_bar.changeIcon('run')

                try:
                    for cmd in PeriodCmd_[interval]:
                        _run_cmd(cmd, Replaces_)
                    # Сохранить значение в счетчике
                    self.period_counter[interval] = cur_time
                except:
                    log.fatal(u'Ошибка исполнения команд периодического автозапуска')

                if self.task_bar and CAN_CHANGE_TRAY_ICONS:
                    self.task_bar.changeIcon('loop')

    def init_period_counter(self, PeriodCmd_=None):
        """
        Инициализация счетчиков для всех периодов.
        @param PeriodCmd_: Словарь периодического автозапуска комманд.
        """
        self.period_counter = {}
        if PeriodCmd_:
            # Сначала проверить существуют ли счетчики для всех периодов
            for interval in PeriodCmd_.keys():
                if interval not in self.period_counter:
                    # Надо не забывать что time.time()
                    # возвращает значение в миллисекундах
                    self.period_counter[interval] = time.time()
        return self.period_counter


if __name__ == '__main__':
    test_run_cmd_cfg()

# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль поддержки файла конфигурации.
"""

import os
import os.path

from . import log_func
from . import global_func
from .. import global_data


class UltraConfig(object):
    """
    Конфигурация парсера.
    """
    def __init__(self, encode=None):
        """
        Конструктор
        """
        self.encode = encode if encode else global_func.getDefaultEncoding()

        # Полное имя коммандного файла
        self.cmd_filename = None

        # Полное имя файла дополнительной высвечиваемой информации
        self.info_filename = global_data.getGlobal('DEFAULT_INFO_FILENAME')

        # Кодовая страница коммандной строки
        self.shell_encode = global_func.getDefaultShellEncoding()

        # Замена
        self.replaces = {}
        self.replaces_list = []

        # Периодический запуск комманды
        self.cmd_period = {}    # Время периода задается в секундах

    def parseConfig(self, cfg_filename):
        """
        Разбор конфигурационного файла.

        @param cfg_filename: Полное имя конфигурационного файла.
        @return: True/False.
        """
        if not os.path.isfile(cfg_filename):
            log_func.warning(u'Ошибка открытия файл конфигурации: <%s>' % cfg_filename)
            return False

        f = None
        try:
            f = open(cfg_filename, 'r')
            for r in f:
                rd = r[:]

                m_buff = [el.strip() for el in rd.split('\"')]
                m_buff_orig = [el for el in rd.split('\"')]

                if len(m_buff) > 0:
                    key_tag = m_buff[0].upper()
                    if key_tag:
                        if key_tag.startswith('CMD_FILE_NAME'):
                            self.cmd_filename = m_buff[1]
                        elif key_tag.startswith('INFO_FILE_NAME'):
                            self.info_filename = m_buff[1]
                        elif key_tag.startswith('CODE_PAGE'):
                            self.shell_encode = m_buff[1]
                        elif key_tag.startswith('REPLACE'):
                            # Замена путей
                            self.replaces[m_buff_orig[1]] = m_buff_orig[3]
                            self.replaces_list.append((m_buff_orig[1], m_buff_orig[3]))

                        elif key_tag.startswith('CMD_PERIOD'):
                            # Словарь комманд периодического запуска
                            # представляет собой:
                            # { период в секундах : [список комманд
                            #                        на исполнение, ...], ...
                            #                        }
                            interval = -1
                            if m_buff[1]:
                                interval = int(m_buff[1])
                            if interval > 0:
                                if interval not in self.cmd_period:
                                    self.cmd_period[interval] = [m_buff[3]]
                                else:
                                    self.cmd_period[interval].append(m_buff[3])

            return True
        except:
            if f is not None:
                f.close()
            log_func.fatal('Ошибка чтения конфигурационного файла <%s>' % cfg_filename)
        return False

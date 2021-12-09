#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ultra_launcher - Программа автоматического запуска команды ОС из командного файла.

Command line parameters:

        python3 ultra_launcher.py [Launch parameters]

Launch parameters:

    [Help and debugging]
        --help|-h|-?        Print help lines
        --version|-v        Print version of the program
        --debug|-d          Enable debug mode
        --log|-l            Enable logging mode

    [Options]
        --start             Start
        --engine=           Engine type (WX, GTK)
"""

import sys
import getopt
import subprocess

from engine.utils import config
from engine.utils import log_func
from engine.utils import global_func
from engine import global_data

__version__ = (0, 0, 3, 1)


def isRunProgram():
    """
    Проверка на уже запущенный экземпляр программы.

    @return: True/False.
    """
    out = subprocess.getoutput('ps ax | grep \'ultra_launcher.py\'')
    lines = out.split('\n')
    if len(lines) > 3:
        log_func.warning(u'Программа UltraLauncher уже запущена')
        return True
    return False


def main(*argv):
    """
    Основная запускаемая функция.

    @param argv: Параметры коммандной строки.
    """
    log_func.init(config)

    # Parse command line arguments
    try:
        options, args = getopt.getopt(argv, 'h?vdl',
                                      ['help', 'version', 'debug', 'log',
                                       'start', 'engine='])
    except getopt.error as msg:
        log_func.warning(str(msg), is_force_print=True)
        log_func.printColourText(global_data.LOGO_TXT, color=log_func.GREEN_COLOR_TEXT)
        log_func.printColourText(__doc__, color=log_func.GREEN_COLOR_TEXT)
        sys.exit(2)

    do_start = False
    for option, arg in options:
        if option in ('-h', '--help', '-?'):
            log_func.printColourText(global_data.LOGO_TXT, color=log_func.GREEN_COLOR_TEXT)
            log_func.printColourText(__doc__, color=log_func.GREEN_COLOR_TEXT)
            sys.exit(0)
        elif option in ('-v', '--version'):
            str_version = 'Ultra Launcher %s' % '.'.join([str(sign) for sign in global_data.VERSION])
            log_func.printColourText(global_data.LOGO_TXT, color=log_func.GREEN_COLOR_TEXT)
            log_func.printColourText(str_version, color=log_func.GREEN_COLOR_TEXT)
            sys.exit(0)
        elif option in ('-d', '--debug'):
            global_func.setDebugMode()
        elif option in ('-l', '--log'):
            global_func.setLogMode()
            log_func.init()
        elif option in ('--engine',):
            global_func.setEngineType(arg.upper())
        elif option in ('--start', ):
            # Выбран режим автоматического запуска прослушивания
            do_start = True

    if not isRunProgram():
        if global_func.isWXEngine():
            from engine.wx import wx_app
            app = wx_app.UltraLaunchApp()
            if do_start:
                app.start()
            app.MainLoop()
        elif global_func.isGTKEngine():
            from engine.gtk import taskbar_indicator
            indicator = taskbar_indicator.GtkTaskBarIndicator()
            if do_start:
                indicator.start()
            indicator.runMainLoop()
        else:
            log_func.warning(u'Не определен тип движка')
    else:
        log_func.warning('Ultra Launcher already run!')
    
    
if __name__ == '__main__':
    main(*sys.argv[1:])

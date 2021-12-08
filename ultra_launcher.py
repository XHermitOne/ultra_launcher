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

from engine.utils import config
from engine.utils import log_func
from engine.utils import global_func
from engine import global_data


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
        elif option in ('--start', ):
            # Выбран режим автоматического запуска прослушивания
            app = icCtrlApp(0)
            app.start()

    if not app.isRun():

        app.MainLoop()
    else:
        log_func.warning('Ultra Launcher already run!')
    
    
if __name__ == '__main__':
    main(*sys.argv[1:])

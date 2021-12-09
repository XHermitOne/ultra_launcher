#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global variables and objects iqFramework.
"""

import sys
import locale
import os.path
import datetime

VERSION = (0, 0, 3, 1)

DEBUG_MODE = False
LOG_MODE = False

RUNTIME_MODE = False

PROJECT_NAME = None

# Program profile folder name
PROFILE_DIRNAME = '.ultra_launcher'

DEFAULT_ENCODING = 'utf-8'

# Default shell encoding
DEFAULT_SHELL_ENCODING = sys.stdout.encoding if sys.platform.startswith('win') else locale.getpreferredencoding()

# Home path
HOME_PATH = os.environ['HOME'] if 'HOME' in os.environ else (os.environ.get('HOMEDRIVE',
                                                                            '') + os.environ.get('HOMEPATH', ''))
# Log file name
LOG_PATH = HOME_PATH if HOME_PATH else os.path.join(os.path.dirname(__file__), 'log')
LOG_FILENAME = os.path.join(LOG_PATH,
                            PROFILE_DIRNAME,
                            'ultra_launcher_%s.log' % datetime.date.today().isoformat())

# Path to profile folder
PROFILE_PATH = os.path.join(HOME_PATH, PROFILE_DIRNAME)

# Engine type. wx, qt or cui
WX_ENGINE_TYPE = 'WX'
GTK_ENGINE_TYPE = 'GTK'

# Set default engine type
DEFAULT_ENGINE_TYPE = WX_ENGINE_TYPE

ENGINE_TYPE = DEFAULT_ENGINE_TYPE

# Application object
APPLICATION = None

# Main window object
MAIN_WINDOW = None

LOGO_TXT = u'''
        ___ __   _          _            _      ___ __  
 / / )   )  )_) /_)    )   /_) / / )\ ) / ` )_) )_  )_) 
(_/ (__ (  / \ / /    (__ / / (_/ (  ( (_. ( ( (__ / \  
'''


DEFAULT_STR_DATE_FMT = '%Y-%m-%d'
DEFAULT_STR_DATETIME_FMT = '%Y-%m-%d %H:%M:%S'


# Имя файла по умолчанию дополнительной высвечиваемой информации
DEFAULT_INFO_FILENAME = os.path.join(os.environ.get('HOME', os.path.dirname(__file__)),
                                     '.ultra_launch', 'tray_info.txt')


# Убрать из командного файла дублирующие команды?
REMOVE_DOUBLE_COMMANDS = False


def getGlobal(name):
    """
    Read the global parameter value.

    :type name: C{string}
    :param name: Parameter name.
    """
    return globals()[name]


def setGlobal(name, value):
    """
    Set global parameter value.

    :type name: C{string}
    :param name: Parameter name.
    :param value: Parameter value.
    """
    globals()[name] = value

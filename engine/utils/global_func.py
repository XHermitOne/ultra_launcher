#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global functions module.
"""

from .. import global_data

__version__ = (0, 0, 0, 1)


def isDebugMode():
    """
    Is debug mode?
    """
    return global_data.getGlobal('DEBUG_MODE')


def setDebugMode(debug_mode=True):
    """
    Set debug mode.
    """
    global_data.setGlobal('DEBUG_MODE', debug_mode)


def isLogMode():
    """
    Is logging mode?
    """
    return global_data.getGlobal('LOG_MODE')


def setLogMode(log_mode=True):
    """
    Set logging mode.
    """
    global_data.setGlobal('LOG_MODE', log_mode)


def getLogFilename():
    """
    Get log filename.
    """
    return global_data.getGlobal('LOG_FILENAME')


def setLogFilename(log_filename):
    """
    Set log filename.

    :param log_filename: Log file name.
    """
    global_data.setGlobal('LOG_FILENAME', log_filename)


def getEngineType():
    """
    Get engine type (wx, gtk and etc).
    """
    return global_data.getGlobal('ENGINE_TYPE')


def setEngineType(engine_type):
    """
    Set engine type.

    :param engine_type: Engine type (wx, gtk and etc).
    """
    return global_data.setGlobal('ENGINE_TYPE', engine_type)


def isWXEngine():
    """
    Set engine as WX.

    :return: True/False.
    """
    return global_data.getGlobal('ENGINE_TYPE') == global_data.WX_ENGINE_TYPE


def isGTKEngine():
    """
    Set engine as GTK.

    :return: True/False.
    """
    return global_data.getGlobal('ENGINE_TYPE') == global_data.GTK_ENGINE_TYPE


def getDefaultShellEncoding():
    """
    Determine the current encoding for text output.

    :return: Actual text encoding.
    """
    return global_data.getGlobal('DEFAULT_SHELL_ENCODING')


def getDefaultEncoding():
    """
    Get default encoding for text output.

    :return: Default text encoding.
    """
    return global_data.getGlobal('DEFAULT_ENCODING')


def getApplication():
    """
    Get application object.
    """
    app = global_data.getGlobal('APPLICATION')
    return app


def getMainWin():
    """
    Main window object.
    """
    main_win = global_data.getGlobal('MAIN_WINDOW')
    if main_win is None:
        if isWXEngine():
            app = getApplication()
            main_win = app.GetTopWindow() if app else None
        elif isQTEngine():
            main_win = None
        elif isCUIEngine():
            main_win = None

        if main_win:
            global_data.setGlobal('MAIN_WINDOW', main_win)
    return main_win


def getDefaultStrDateFmt():
    """
    Get default string date format.
    """
    return global_data.getGlobal('DEFAULT_STR_DATE_FMT')


def getDefaultStrDatetimeFmt():
    """
    Get default string datetime format.
    """
    return global_data.getGlobal('DEFAULT_STR_DATETIME_FMT')

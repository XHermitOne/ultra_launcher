#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Text file functions.
"""

import os
import os.path

from . import log_func
from . import global_func

__version__ = (0, 0, 0, 1)

DEFAULT_ENCODING = global_func.getDefaultEncoding()


def loadTextFile(txt_filename):
    """
    Load from text file.

    :param txt_filename: Text file name.
    :return: File text or empty text if error.
    """
    if not os.path.exists(txt_filename):
        log_func.warning(u'File <%s> not found' % txt_filename)
        return ''

    file_obj = None
    try:
        file_obj = open(txt_filename, 'rt')
        txt = file_obj.read()
        file_obj.close()
    except:
        if file_obj:
            file_obj.close()
        log_func.fatal(u'Load text file <%s> error' % txt_filename)
        return ''

    return txt

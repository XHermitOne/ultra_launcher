#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль приложения WX.
"""
import wx

from . import wx_ctrlfrm

__version__ = (0, 0, 3, 1)


class UltraLaunchApp(wx.App):

    def OnInit(self):
        wx.InitAllImageHandlers()
        self.ctrl_form = wx_ctrlfrm.UltraLaunchCtrlForm(None)
        self.SetTopWindow(self.ctrl_form)
        return 1
    
    def start(self):
        """
        Запустить.
        """
        self.ctrl_form.start()

    def stop(self):
        """
        Остановить.
        """
        self.ctrl_form.stop()
        

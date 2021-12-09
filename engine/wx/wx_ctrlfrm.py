# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль формы управления запуском/остановом цикла прослушки.
"""

import wx
from . import ultra_launch_ctrl_dlg_proto
from . import wx_taskbar
from .. import launch
from ..util import log_func

__version__ = (0, 0, 3, 1)


class UltraLaunchCtrlForm(ultra_launch_ctrl_dlg_proto.UltraLaunchCtrlDlgProto):
    """
    Форма управления запуском/остановом цикла прослушки.
    """

    def __init__(self, *args, **kwargs):
        """
        Конструктор.
        :param TaskBarIcon_: Объект управления иконки трея.
        """
        ultra_launch_ctrl_dlg_proto.UltraLaunchCtrlDlgProto.__init__(self, *args, **kwargs)
        
        self.tb_icon = wx_taskbar.WxTaskBarIcon(self)
        
        self.launch_manager = launch.UltraLaunchManager(self.tb_icon)
        
    def onCloseWindow(self, event):
        """
        Обработчик закрытия окна.
        """
        self.Hide()
        
    def start(self):
        """
        Запустить.
        """
        self.launch_manager.startLoop()
        
        self.tb_icon.changeIcon('loop')
        self.start_button.Enable(False)
        self.stop_button.Enable(True)
        
    def stop(self):
        """
        Остановить.
        """
        self.launch_manager.stopLoop()
        
        self.tb_icon.changeIcon('stop')
        self.start_button.Enable(True)
        self.stop_button.Enable(False)
        
    def onStartButtonClick(self, event):
        """
        Обработчик кнопки пуска.
        """
        log_func.info('START')
        self.start()
        
        event.Skip()

    def onStopButtonClick(self, event):
        """
        Обработчик кнопки останова.
        """
        log_func.info('STOP')
        self.stop()

        event.Skip()
        

def main():
    """
    Основная запускаемая функция.
    """
    app = wx.PySimpleApp()
    tb_icon = wx_taskbar.WxTaskBarIcon(app)
    app.MainLoop()
    tb_icon.Destroy()

    
if __name__ == '__main__':
    main()

# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль управления запуском/остановом цикла прослушки.
Управление производится в форме управления.
Форма управления вызывается двойным кликом на иконке в трее.
"""

import wx
import wx.adv
import os
import os.path

from .. import launch

from ..utils import config
from .. import global_data

from ..utils import log_func
from ..utils import txtfile_func

__version__ = (0, 0, 3, 1)

WIN_ICON_SIZE = (16, 16)
GTK_ICON_SIZE = (16, 16)

# Сигнатуры сообщений
# Сигнатура определяет цвет фона окна дополнительной информации
# По умолчанию окно с серым фоном
ERROR_INFO_SIGNATURE = u'ERROR:'        # Красный фон
WARNING_INFO_SIGNATURE = u'WARNING:'    # Желтый фон
DEBUG_INFO_SIGNATURE = u'DEBUG:'        # Бирюзовый фон

# Период проверки вывода информационных сообщений
DEFAULT_TIMER_TICK = 30000


class WxTaskBarIcon(wx.adv.TaskBarIcon):
    """
    Класс иконки на панели задач/в трее.
    """
    _ID_TBMENU_EXIT = wx.NewId()
    
    def __init__(self, control_form):
        """
        Конструктор.

        @param control_form: Форма управления.
        """
        wx.adv.TaskBarIcon.__init__(self)

        # Имя файла сообщения дополнительной информации
        self.info_filename = global_data.getGlobal('DEFAULT_INFO_FILENAME')
        if os.path.exists(launch.DEFAULT_CFG_FILENAME):
            # Конфигурация запуска
            self.cfg = config.UltraConfig()
            self.cfg.parseConfig(launch.DEFAULT_CFG_FILENAME)
            self.info_filename = self.cfg.info_filename

        # Форма управления
        self.main_form = control_form

        # Иконки
        loop_img = self._createIconImage(global_data.getGlobal('LOOP_ICON_FILENAME'))
        stop_img = self._createIconImage(global_data.getGlobal('STOP_ICON_FILENAME'))
        run_img = self._createIconImage(global_data.getGlobal('RUN_ICON_FILENAME'))

        self.images = {'loop': loop_img, 'stop': stop_img, 'run': run_img}
        
        icon = self.createIcon(stop_img)
        self.SetIcon(icon, 'IC services ultra launch')
        self.imgidx = 1

        # Сообщение о занятом процессе
        self.busy_info = None

        # Таймер проверки текстового файла информационного сообщения
        self.timer = None

        # bind some events
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.onTaskBarActivate)
        self.Bind(wx.EVT_MENU, self.onTaskBarExit, id=self._ID_TBMENU_EXIT)
        self.Bind(wx.EVT_TIMER, self.onTimerTick)

        # Запустить таймер
        self.startTimer()

    def _createIconImage(self, png_filename):
        """
        Инициализация образа иконки по имени файла иконки.
        """
        icon_file_name = os.path.join(os.path.dirname(__file__), png_filename)
        if not os.path.exists(icon_file_name):
            icon_file_name = os.path.join(os.getcwd(), png_filename)

        return wx.Image(icon_file_name, wx.BITMAP_TYPE_PNG)
        
    def CreatePopupMenu(self):
        """
        This method is called by the base class when it needs to popup
        the menu for the default event_RIGHT_DOWN event.  Just create
        the menu how you want it and return it from this function,
        the base class takes care of the rest.
        """
        menu = wx.Menu()
        menu.Append(self._ID_TBMENU_EXIT, u'Выход')
        return menu

    def getIconSize(self):
        """
        Размер иконки.
        """
        icon_size = GTK_ICON_SIZE
        if 'wxMSW' in wx.PlatformInfo:
            icon_size = WIN_ICON_SIZE
        elif 'wxGTK' in wx.PlatformInfo:
            icon_size = GTK_ICON_SIZE
        return icon_size

    def createIcon(self, img):
        """
        The various platforms have different requirements for the
        icon size...
        """
        icon_size = self.getIconSize()
        img = img.Scale(*icon_size)
        # wxMac can be any size upto 128x128, so leave the source img alone....
        icon = wx.Icon(img.ConvertToBitmap())
        return icon    

    def onTaskBarActivate(self, event):
        """
        Двойной клик на иконке в трее.
        """
        if self.main_form.IsIconized():
            self.main_form.Iconize(False)
        if not self.main_form.IsShown():
            self.main_form.Show(True)
        self.main_form.Raise()

    def onTaskBarExit(self, event):
        """
        Выход.
        """
        launch.stopLoop()
        self.RemoveIcon()
        self.main_form.Destroy()

    def showInfoWindow(self, msg, bg_colour=None):
        """
        Отобразить всплывающее окно с сообщением.

        @param msg: Текст сообщения.
        @param bg_colour: Цвет фона окна.
        @return: True/False.
        """
        log_func.debug(u'Отображение дополнительной информации')
        try:
            app = wx.GetApp()
            popup_window = wx.PopupTransientWindow(app.GetTopWindow(), wx.SIMPLE_BORDER)
            panel = wx.Panel(popup_window)

            if bg_colour is not None:
                panel.SetBackgroundColour(bg_colour)

            label = wx.StaticText(panel, -1, msg, pos=(10, 10))

            size = label.GetBestSize()
            popup_window.SetSize((size.width + 20, size.height + 20))
            panel.SetSize((size.width + 20, size.height + 20))

            dw, dh = wx.DisplaySize()
            x = dw - size.width
            icon_size = self.getIconSize()
            y = icon_size[1] + 1

            popup_window.Position(wx.Point(x, y), wx.Size(0, 0))
            popup_window.Popup()
            return True
        except:
            log_func.fatal(u'Ошибка отображения всплывающего окна с сообщением')
        return False

    def showInfo(self, info_filename=None):
        """
        Отобразить дополнительное сообщение.

        @param info_filename: Полное имя файла дополнительной информации.
        @return: True/False.
        """
        if info_filename is None:
            info_filename = self.info_filename

        if os.path.exists(info_filename):
            msg = txtfile_func.loadTextFile(info_filename)
            colour = wx.LIGHT_GREY
            if msg.startswith(ERROR_INFO_SIGNATURE):
                colour = wx.RED
                msg = msg.replace(ERROR_INFO_SIGNATURE, u'')
            elif msg.startswith(WARNING_INFO_SIGNATURE):
                colour = wx.YELLOW
                msg = msg.replace(WARNING_INFO_SIGNATURE, u'')
            elif msg.startswith(DEBUG_INFO_SIGNATURE):
                colour = wx.CYAN
                msg = msg.replace(DEBUG_INFO_SIGNATURE, u'')

            self.showInfoWindow(msg, colour)

            # После отображения окна с дополнительной информации
            # удаляем файл
            try:
                os.remove(info_filename)
            except OSError:
                log_func.fatal(u'Ошибка удаления файла <%s>' % info_filename)
                return False
            return True
        else:
            log_func.warning(u'Информационный файл <%s> не найден' % info_filename)

        return False

    def changeIcon(self, image_name):
        """
        Смена иконки.

        @param image_name: Имя образа.
        """
        names = ['loop', 'stop', 'run']
        name = names[self.imgidx]
        
        self.imgidx += 1
        if self.imgidx >= len(names):
            self.imgidx = 0
            
        icon = self.createIcon(self.images[image_name])
        log_func.info(u'Смена иконки на <%s : %s>' % (name, image_name))
        self.SetIcon(icon, u'Текущее состояние: ' + name)

    def startTimer(self):
        """
        Запуск таймера проверки вывода информационного сообщения.
        """
        self.timer = wx.Timer(self)
        self.timer.Start(DEFAULT_TIMER_TICK)

    def stopTimer(self):
        """
        Останов таймера проверки вывода информационного сообщения.
        """
        if self.timer:
            self.timer.Stop()
            self.timer = None

    def onTimerTick(self, event):
        """
        Обработчик одного тика таймера.
        """
        # ВНИМАНИЕ! При смене иконки, возможно необходимо показать
        # дополнительную информацию
        self.showInfo(self.info_filename)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Индикатор программы в трее.
Реализация на GTK.
"""

import os
import signal
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

import gi.repository.Gtk
import gi.repository.AppIndicator3


from .. import global_data
from .. import launch
from ..util import log_func

__version__ = (0, 0, 0, 1)

ICONS = {
    'run': global_data.getGlobal('RUN_ICON_FILENAME'),
    'loop': global_data.getGlobal('LOOP_ICON_FILENAME'),
    'stop': global_data.getGlobal('STOP_ICON_FILENAME'),
    'error': global_data.getGlobal('ERR_ICON_FILENAME'),
}


class GtkTaskBarIndicator():
    def __init__(self):
        """
        Конструктор.
        """
        self.app = 'show_proc'

        self.launch_manager = launch.UltraLaunchManager(self)

        icon_filename = ICONS['stop']
        
        # after you defined the initial indicator, you can alter the icon!
        self.indicator = gi.repository.AppIndicator3.Indicator.new(self.app, icon_filename,
                                                                   gi.repository.AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(gi.repository.AppIndicator3.IndicatorStatus.ACTIVE)
        self.popup_menu = self.createMenu()
        self.indicator.set_menu(self.popup_menu)

    def createMenu(self):
        """
        Создание контекстного меню.
        """
        menu = gi.repository.Gtk.Menu()
        self.menuitem_start = gi.repository.Gtk.MenuItem(label=u'Запуск')
        self.menuitem_start.connect('activate', self.onStartMenuItem)
        self.menuitem_stop = gi.repository.Gtk.MenuItem(label=u'Останов')
        self.menuitem_stop.connect('activate', self.onStopMenuItem)
        self.menuitem_stop.set_sensitive(False)
        self.menuitem_exit = gi.repository.Gtk.MenuItem(label=u'Выход')
        self.menuitem_exit.connect('activate', self.onExitMenuItem)
        
        menu.append(self.menuitem_start)
        menu.append(self.menuitem_stop)
        menu.append(self.menuitem_exit)
        menu.show_all()
        return menu

    def changeIcon(self, image_name):
        """
        Смена иконки.

        :param image_name: Имя образа.
        """
        icon_filename = ICONS.get(image_name, ICONS['error'])
        self.indicator.set_icon(icon_filename)
        log_func.info(u'Смена иконки на <%s>' % image_name)

    def onExitMenuItem(self, source):
        """
        Обработчик выхода.
        """
        gi.repository.Gtk.main_quit()

    def start(self):
        """
        Запустить.
        """
        self.launch_manager.startLoop()
        self.changeIcon('loop')

        self.menuitem_start.set_sensitive(False)
        self.menuitem_stop.set_sensitive(True)

    def onStartMenuItem(self, source):
        """
        Запустить.
        """
        self.start()

    def stop(self):
        """
        Остановить.
        """
        self.launch_manager.stopLoop()
        self.changeIcon('stop')

        self.menuitem_start.set_sensitive(True)
        self.menuitem_stop.set_sensitive(False)

    def onStopMenuItem(self, source):
        """
        Остановить.
        """
        self.stop()

    def runMainLoop(self):
        """
        Запуск основного цикла обработки событий.
        """
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        gi.repository.Gtk.main()

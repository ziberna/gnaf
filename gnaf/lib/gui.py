#    GNAF (GTK Notification Applet Framework)
#    Copyright (C) 2011 Kantist
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.
#    If not, see http://www.gnu.org/licenses/gpl-3.0.html

import os; exists = os.path.exists
import time
import re

from gnaf.lib.istype import *
from gnaf.lib.tools import Regex
from gnaf.lib.format import wrap

################################################################################
# GTK3 has issues with status icon. The following variables will allow me a    #
# smooth migration from GTK2 to GTK3 once the icon issue in GTK3 is fixed.     #
################################################################################
import gtk
import gobject
import pygtk; pygtk.require('2.0')
import pynotify; pynotify.init('GNAF')

GtkStatusIcon = gtk.StatusIcon
GtkStatusIconPositionMenu = gtk.status_icon_position_menu
GtkMenu = gtk.Menu
GtkMenuItem = gtk.MenuItem
GtkSeparatorMenuItem = gtk.SeparatorMenuItem
GtkCurrentEventTime = gtk.get_current_event_time

# left unchanged (can't set attributes)
#  - gtk.StatusIcon.set_from_file
#  - gtk.StatusIcon.set_visible
#  - gtk.Menu.append
#  - gtk.Menu.show_all
#  - gtk.Menu.popup
#  - gtk.MenuItem.set_submenu
#  - gtk.{StatusIcon,MenuItem}.set_tooltip_markup
#  - gtk.{StatusIcon,MenuItem}.connect

ThreadsInit = gobject.threads_init
IdleAdd = gobject.idle_add
TimeoutAdd = gobject.timeout_add_seconds
Main = gtk.main
Quit = gtk.main_quit
################################################################################

class Gui(object):
    def __init__(self):
        self.icon_gtk = None
        self.icon_type = None
        self.icon_paths = []
        self.icon_types = {}
        self.icon_visible = None
        self.icon_path_notification = None
        self.tooltip_markup = None
        self.leftmenu_gtk = None
        self.leftmenu_items = []
        self.rightmenu_gtk = None
        self.rightmenu_items = []
        self.notification_stack = None
        self.regex = Regex()
        self.menu_wrap = 50
        self.tooltip_wrap = 50
        self.icon_tooltip_wrap = 50
    
    def icon(self, type=None):
        if type == None:
            return self.icon_type
        elif self.icon_gtk == None:
            self.icon_init()
        self.icon_type = type
        path = self.icon_path_from_type(type)
        if path != None:
            self.icon_gtk.set_from_file(path)
    
    def icon_path_from_type(self, type):
        if not type in self.icon_types:
            return None
        file = self.icon_types[type]
        for path in self.icon_paths:
            path += '/' + file
            if exists(path):
                return path
        return None
    
    def icon_init(self):
        self.icon_gtk = GtkStatusIcon()
        self.icon_gtk.connect('activate', lambda i: self.leftclick(i))
        self.icon_gtk.connect('popup-menu', lambda i, b, t: self.rightclick(i, b, t))
    
    def visible(self, value=None):
        if None:
            return self.icon_visible
        if self.icon_gtk == None:
            self.icon_init()
        self.icon_visible = value
        self.icon_gtk.set_visible(value)
    
    def tooltip(self, markup=None):
        if markup == None:
            return self.tooltip_markup
        if self.regex.ignore(markup):
            return
        elif self.icon_gtk == None:
            self.icon_init()
        markup = self.regex.alias(markup)
        markup = wrap(markup, self.icon_tooltip_wrap)
        markup = self.markup_escape(markup)
        self.tooltip_markup = markup
        self.icon_gtk.set_tooltip_markup(markup)
        
    def leftmenu(self, items=None):
        if items == None:
            return self.leftmenu_items
        self.leftmenu_items = items
        self.leftmenu_gtk = self.menu(items)
    
    def leftclick(self, icon):
        if self.leftmenu_gtk == None:
            return
        button = 1
        time = GtkCurrentEventTime()
        self.leftmenu_gtk.popup(None, None, GtkStatusIconPositionMenu, button,
                            time, self.icon_gtk)
    
    def rightmenu(self, items=None):
        if items == None:
            return self.rightmenu_items
        self.rightmenu_items = items
        self.rightmenu_gtk = self.menu(items)
    
    def rightclick(self, icon, button, time):
        if self.rightmenu_gtk == None:
            return
        self.rightmenu_gtk.popup(None, None, GtkStatusIconPositionMenu, button,
                            time, self.icon_gtk)
    
    def menu(self, items):
        items = [item for item in items if item != None]
        menu_gtk = GtkMenu()
        for item in items:
            menu_item_gtk = self.menu_item(item)
            if menu_item_gtk != None:
                menu_gtk.append(menu_item_gtk)
        menu_gtk.show_all()
        return menu_gtk
    
    def menu_item(self, item):
        tooltip = None
        submenu = None
        function = None
        args = ()
        
        if isstr(item):
            text = item
        else:
            length = len(item)
            text = item[0]
            if length >= 2:
                if islist(item[1]):
                    submenu = item[1]
                    if length == 3:
                        tooltip = item[2]
                elif isstr(item[1]):
                    tooltip = item[1]
                elif iscallable(item[1]):
                    function = item[1]
                    if length >= 3:
                        if istuple(item[2]):
                            args = item[2]
                            if length >= 4:
                                tooltip = item[3]
                        else:
                            tooltip = item[2]
        
        if text == '-':
            menu_item_gtk = GtkSeparatorMenuItem()
            return menu_item_gtk
        if self.regex.ignore(text):
            return None
        
        text = wrap(self.regex.alias(text), self.menu_wrap)
        menu_item_gtk = GtkMenuItem(text)
        
        if tooltip != None and not self.regex.ignore(tooltip):
            tooltip = self.regex.alias(tooltip)
            tooltip = wrap(tooltip, self.tooltip_wrap)
            tooltip = self.markup_escape(tooltip)
            menu_item_gtk.set_tooltip_markup(tooltip)
        if submenu != None:
            menu_item_gtk.set_submenu(self.menu(submenu))
        if function != None:
            menu_item_gtk.connect('activate', lambda g, f=function, a=args: IdleAdd(f,*a))
        return menu_item_gtk
    
    def notify(self, item):
        if isstr(item):
            self.notify_show(item)
        elif istuple(item):
            if len(item) == 1:
                self.notify_show(item[0])
            elif len(item) == 2:
                if isbool(item[1]):
                    self.notify_show(item[0], stack=item[1])
                elif exists(item[1]):
                    self.notify_show(item[0], icon=item[1])
                else:
                    self.notify_show(item[0], item[1])
            elif len(item) == 3:
                if exists(item[1]):
                    self.notify_show(item[0], icon=item[1], stack=item[2])
                elif exists(item[2]):
                    self.notify_show(*item)
                else:
                    self.notify_show(item[0], item[1], stack=item[2])
            elif len(item) >= 4:
                self.notify_show(item[0], item[1], item[2], item[3])
    
    def notify_show(self, title, body=None, icon=None, stack=False):
        if self.regex.ignore(title) or self.regex.ignore(body):
            return
        title = self.regex.alias(title)
        body = self.regex.alias(body)
        if icon == None:
            icon = self.icon_path_notification
        n = pynotify.Notification(title, body, icon)
        n.show()
        if not self.notification_stack or not stack:
            n.close()
    
    def markup_escape(self, markup):
        markup = re.sub(r'<(/?(b|i|u|s|span|big|sub|sup|small|tt))>',r'[\1]',markup)
        markup = markup.replace('<','&lt;').replace('>','&gt;')
        markup = re.sub(r'\[(/?(b|i|u|s|span|big|sub|sup|small|tt))\]',r'<\1>',markup)
        return markup

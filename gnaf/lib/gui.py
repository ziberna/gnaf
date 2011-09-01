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

import time
import os; exists = os.path.exists

from gnaf.lib.istype import *
from gnaf.lib.format import bashQuotes
from gnaf.lib.tools import id, Shell
from gnaf.lib.write import writeLR

################################################################################
# GTK3 has issues with status icon. The following variables will allow me a    #
# smooth migration from GTK2 to GTK3 once the icon issue in GTK3 is fixed.     #
################################################################################
import gtk
import pygtk; pygtk.require('2.0')
GtkStatusIcon = gtk.StatusIcon
GtkStatusIconPositionMenu = gtk.status_icon_position_menu
GtkMenu = gtk.Menu
GtkMenuItem = gtk.MenuItem
GtkSeparatorMenuItem = gtk.SeparatorMenuItem
GtkCurrentEventTime = gtk.get_current_event_time

Main = gtk.main
Quit = gtk.main_quit

# left unchanged:
#  - gtk.StatusIcon.set_from_file
#  - gtk.<any>.set_tooltip_markup

import gobject
ThreadsInit = gobject.threads_init
GobjectIdleAdd = gobject.idle_add
GobjectTimeoutAdd = gobject.timeout_add
################################################################################
gui_count = 0
update_count = 0
gui_change_id = 0
gui_interval = 0.25

def GuiCount():
    global gui_count
    gui_count += 1
    if gui_count % 10 == 0:
        Statistics()

def UpdateCount():
    global update_count
    update_count += 1

def Statistics():
    writeLR(' - statistics', '%i GUI changes/%i applet updates - ' % (gui_count, update_count))

def IdleAdd(function, *params):
    global gui_change_id; global gui_interval
    gui_id = id()
    diff = gui_id - gui_change_id
    if diff < gui_interval and diff > 0:
        time.sleep(diff)
        IdleAdd(function, *params)
    else:
        gui_change_id = gui_id
        GobjectIdleAdd(function, *params)
        GuiCount()

def TimeoutAdd(seconds, function, *params):
    global gui_change_id; global gui_interval
    gui_id = id()
    diff = gui_id - gui_change_id
    if diff < gui_interval and diff > 0:
        time.sleep(diff)
        IdleAdd(function, *params)
    else:
        gui_change_id = gui_id
        GobjectTimeoutAdd(seconds * 1000, function, *params)
        GuiCount()

class Icon(object):
    _type = None
    _file = None
    _path = None
    
    def __init__(self, type=None, file=None, path=None, paths=[], types={}, icon=None, visible=True):
        self.paths = paths
        self.types = types
        self.icon = icon if icon != None else GtkStatusIcon()
        self.icon.connect('activate', self.leftclick)
        self.icon.connect('popup-menu', self.rightclick)
        
        self._tooltip = Tooltip(self.icon, thread=True)
        self._leftmenu = Menu()
        self._rightmenu = Menu()
        
        self.visible = visible
        if type != None:
            self.type = type
        elif path != None:
            self.path = path
        elif file != None:
            self.file = file
        else:
            id(self)
    
    @property
    def type(self): return self._type
    
    @type.setter
    def type(self, value):
        id(self)
        self._type = value
        self.from_type(value)
    
    @property
    def file(self): return self._file
    
    @file.setter
    def file(self, value):
        id(self)
        self._file = value
        self.from_file(value)
    
    @property
    def path(self): return self._path
    
    @path.setter
    def path(self, value):
        id(self)
        self._path = value
        self.from_path(value)
    
    @property
    def visible(self): return self._visible
    
    @visible.setter
    def visible(self, value):
        self._visible = value
        current = self.icon.get_visible()
        if current != value:
            IdleAdd(self.icon.set_visible, value)
    
    def from_type(self, type):
        path = self.path_from_type(type)
        self.from_path(path)
    
    def from_file(self, file):
        path = self.path_from_file(file)
        self.from_path(path)
    
    def from_path(self, path):
        if self.path != path and path != None:
            IdleAdd(self.icon.set_from_file, path)
        self._path = path
    
    
    def path_from_type(self, type):
        if not type in self.types:
            return None
        file = self.types[type]
        return self.path_from_file(file)
    
    def path_from_file(self, file):
        for path in self.paths:
            path += '/' + file
            if exists(path):
                return path
        return None
    
    @property
    def tooltip(self): return self._tooltip.text
    
    @tooltip.setter
    def tooltip(self, value): self._tooltip.text = value
    
    @property
    def leftmenu(self): return self._leftmenu.items
    
    @leftmenu.setter
    def leftmenu(self, value): self._leftmenu.items = value
    
    def leftclick(self, icon):
        button = 1
        time = GtkCurrentEventTime()
        self._leftmenu.popup(None, None, GtkStatusIconPositionMenu, button,
                            time, self.icon)
    
    @property
    def rightmenu(self): return self._rightmenu.items
    
    @rightmenu.setter
    def rightmenu(self, value): self._rightmenu.items = value
    
    def rightclick(self, icon, button, time):
        self._rightmenu.popup(None, None, GtkStatusIconPositionMenu,
                               button, time, self.icon)


class Tooltip(object):
    _text = None
    
    def __init__(self, target, text=None, thread=False):
        self.target = target
        self.thread = thread
        self.text = text
    
    @property
    def text(self): return self._text
    
    @text.setter
    def text(self, value):
        id(self)
        self._text = value
        current = self.target.get_tooltip_markup()
        if current != value or (current != None and value != ''):
            if self.thread:
                IdleAdd(self.target.set_tooltip_markup, value)
            else:
                self.target.set_tooltip_markup(value)


class Menu(object):
    _items = None
    
    def __init__(self, items=None):
        self.items = items
    
    @property
    def items(self): return self._items
    
    @items.setter
    def items(self, value):
        id(self)
        self._items = value
        self.menu = Menu.generate(value)
    
    def popup(self, parent_shell, parent_item, func, button, time, target):
        if self.menu != None:
            IdleAdd(self.menu.popup, parent_shell, parent_item, func, button, time, target)
    
    @staticmethod
    def generate(items):
        if items == None:
            return None
        items = [item for item in items if item != None]
        menu = GtkMenu()
        for item in items:
            menu.append(MenuItem.generate(item).item)
        menu.show_all()
        return menu


class MenuItem(object):
    _text = None
    _tooltip = None
    _submenu = None
    _function = None
    _args = None
    _signal_id = None
    
    def __init__(self, text, tooltip=None, submenu=None, function=None, args=None):
        self.text = text
        self.tooltip = tooltip
        self.submenu = submenu
        self.function = function
        self.args = args
        
    @property
    def text(self): return self._text
    
    @text.setter
    def text(self, value):
        if value == '-':
            self.item = GtkSeparatorMenuItem()
        else:
            self.item = GtkMenuItem(value)
    
    @property
    def tooltip(self): return self._tooltip
    
    @tooltip.setter
    def tooltip(self, value):
        self._tooltip = value
        self._tooltip_obj = Tooltip(self.item, value)
    
    @property
    def submenu(self): return self._submenu.items
    
    @submenu.setter
    def submenu(self, value):
        self._submenu = Menu(value)
        self.item.set_submenu(self._submenu.menu)
    
    @property
    def function(self): return self._function
    
    @function.setter
    def function(self, value):
        self._function = value
        if value != None:
            if self._signal_id != None:
                self.item.disconnect(self._signal_id)
            if self.args != None:
                signal = self.item.connect('activate', lambda g, f=value, a=self.args: f(*a))
            else:
                signal = self.item.connect('activate', lambda g, f=value: f())
            self._signal_id = signal
    
    @property
    def args(self): return self._args
    
    @args.setter
    def args(self, value):
        self._args = value
        if self.function != None:
            self.function = self.function
    
    @staticmethod
    def generate(item):        
        tooltip = None
        submenu = None
        function = None
        args = None
        
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
        return MenuItem(text, tooltip, submenu, function, args)


class Notifier(object):
    _items = None
    
    def __init__(self, auto=False, icon='', items=[]):
        self.cmd = 'notify-send -i'
        self.auto = auto
        self.icon = icon
        self.items = items
    
    @property
    def items(self): return self._items
    
    @items.setter
    def items(self, value):
        id(self)
        self._items = value
        if self.auto: Notifier.show(value, self.icon)
    
    @staticmethod
    def show(items, icon=None):
        for item in items:
            if isstr(item):
                Notifier.execute(item, icon=icon)
            elif istuple(item):
                if len(item) == 1:
                    Notifier.execute(item[0], icon=icon)
                elif len(item) == 2:
                    if exists(item[1]):
                        Notifier.execute(item[0], icon=item[1])
                    else:
                        Notifier.execute(item[0], item[1], icon)
                elif len(item) >= 3:
                    Notifier.execute(item[0], item[1], item[2])
    
    @staticmethod
    def execute(title, body=None, icon=None):
        title = "'%s'" % bashQuotes(title)
        body = ("'%s'" % bashQuotes(body)) if body != None else ''
        icon = ("-i '%s'" % bashQuotes(icon)) if icon != None else ''
        
        Shell("notify-send %s %s %s" % (icon, title, body))

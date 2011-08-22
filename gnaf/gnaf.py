#    GNAF (Gtk Notification Applet Framework)
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

import pygtk
import gtk
import gobject
import thread
import time
import sys
import os
import traceback
write = sys.stdout.write

from lib.dictmerge import DictMerge
from lib.shell import Shell, bash_quotes
from lib.format import format_L_R, format_C

GnafApplets = []

class Gnaf:
    running = False
    updating = False
    enabled = True
    
    settings = {}
    name = ''
    
  #::Initialization methods
    def __init__(self, settings):
        # settings initialization
        self.settings = DictMerge(settings, self.settings)
        self.interval = int(self.settings.get('interval') * 60 * 1000)
        # GUI initialization
        self.icon_init()
        self.tooltip_init()
        self.contextmenu_init()
        self.datamenu_init()
        self.notifications_init()
        # final
        global GnafApplets
        GnafApplets.append(self)
    
    def icon_init(self):
        self.icon = gtk.StatusIcon()
        self.icontype = 'idle'
        self.set_icon()
        self.icon.connect('activate', self.leftclick)
        self.icon.connect('popup-menu', self.rightclick)
    
    def contextmenu_init(self):
        self.context = [
            ('Update now', self.update_manual),
            ('Clear data', self.cleardata),
            ('Mark as idle', self.set_icon_idle),
            '-',
            ('Disable' if self.enabled else 'Enable', self.enable_disable),
            ('Quit', self.quit),
            ('Quit all', Gnaf.main_quit)
        ]
        self.contextmenu = self.menu(self.context)
    
    def datamenu_init(self):
        self.data = ['Not updated yet...']
        self.set_datamenu()
    
    def tooltip_init(self):
        self.tooltip = 'Not updated yet...'
        self.set_tooltip()
    
    def notifications_init(self):
        self.notifications = []
    
  #::Main methods
    @staticmethod
    def main():
        pygtk.require('2.0')
        gtk.gdk.threads_init()
        global GnafApplets
        for applet in GnafApplets:
            gobject.idle_add(applet.update_manual)
        gtk.main()
    
    @staticmethod
    def main_quit():
        write('%s\n' % format_C(' Gnaf applets quitting ', '-'))
        for applet in list(GnafApplets):
            applet.quit()
    
    def quit(self):
        self.enabled = False
        self.icon.set_visible(False)
        global GnafApplets
        GnafApplets.remove(self)
        self.log('', 'QUIT')
        if len(GnafApplets) == 0:
            gtk.main_quit()
    
    def enable_disable(self):
        self.enabled = not self.enabled
        self.icontype = 'idle'
        self.set_icon()
        self.contextmenu_init()
        self.log('', 'ENABLED' if self.enabled else 'DISABLED')
        
    def __update__(self, id=None):
        if self.enabled:
            if self.running:
                if not self.updating and id == self.update_id:
                    thread.start_new(self.updatedata, ())
            else:
                thread.start_new(self.initializedata, ())
        else:
            gobject.timeout_add(self.interval, self.__update__)
    
    def update_manual(self):
        if not self.updating:
            self.update_id = int(time.time())
            self.__update__(self.update_id)
    
    def update_id_set(self):
        self.update_id = int(time.time())
    
    #> separate thread !
    def initializedata(self):
        gobject.idle_add(self.set_tooltip, 'Initializing...')
        self.log('initializing', '...')
        try:
            success = self.initialize()
        except:
            self.debug_output()
            success = False
        if success:
            self.log('initialization', 'DONE')
            self.running = True
            self.update_id_set()
            gobject.idle_add(self.__update__, self.update_id)
        else:
            self.log('initialization', 'ERROR')
            message = 'Error while initializing.\nNext try at %s' \
                       % time.strftime('%H:%M', self.next_update_at())
            gobject.idle_add(self.set_icon, 'error')
            gobject.idle_add(self.set_tooltip, message)
            gobject.idle_add(self.set_datamenu, [message])
            gobject.timeout_add(self.interval, self.__update__)
    
    #> separate thread !
    def updatedata(self):
        gobject.idle_add(self.set_icon, 'updating')
        gobject.idle_add(self.set_tooltip, 'Updating...')
        self.updating = True
        self.log('updating', '...')
        try:
            success = self.update()
        except:
            self.debug_output()
            success = None
        if success == None:
          # Error
            self.log('update', 'ERROR')
            self.icontype = 'error'
            message = 'Error while updating.\nNext try at %s' \
                       % time.strftime('%H:%M', self.next_update_at())
            gobject.idle_add(self.set_tooltip, message)
        elif success == False:
          # No updates
            self.log('update', 'NO UPDATES')
            self.icontype = 'idle'
            gobject.idle_add(self.set_datamenu)
            gobject.idle_add(self.set_tooltip)
        else:
          # Updates
            self.log('update', 'NEW')
            self.icontype = 'new'
            gobject.idle_add(self.set_datamenu)
            gobject.idle_add(self.set_tooltip)
            self.notifydata()
        gobject.idle_add(self.set_icon)
        # Final
        self.update_id_set()
        gobject.timeout_add(self.interval, self.__update__, self.update_id)
        self.updating = False
    
    def notifydata(self):
        if self.settings.get('notify') != False:
            try:
                success = self.notify()
            except:
                success = None
                self.debug_output()
            if success:
                self.notify_send()
        
    def cleardata(self):
        self.log('clearing data', '...')
        self.running = False
        self.updating = False
        self.enabled = True
        self.set_icon_idle()
        self.tooltip_init()
        self.contextmenu_init()
        self.datamenu_init()
        self.notifications_init()
        self.log('clear data', 'DONE')
    
  #::Icon, tooltip and notification methods
    def set_icon(self, type=None):
        if type == None:
            type = self.icontype
        filename = self.settings.get('icon', type)
        self.set_icon_fromfile(filename)
    
    def set_icon_fromfile(self, filename):
        path = self.get_icon_path_fromfile(filename)
        self.set_icon_frompath(path)
    
    def set_icon_frompath(self, path):
        self.icon.set_from_file(path)
    
    def set_icon_idle(self):
        self.set_icon('idle')
    
    def get_icon_path(self, type=None):
        if type == None:
            type = self.icontype
        filename = self.settings.get('icon', type)
        return self.get_icon_path_fromfile(filename)
    
    def get_icon_path_fromfile(self, filename):
        paths = [
            '%s/%s/%s' % (Gnaf.user_dir, self.name, filename),
            '%s/%s' % (Gnaf.user_dir, filename),
            '%s/%s/icons/%s' % (Gnaf.applet_dir, self.name, filename),
            '%s/%s/%s' % (Gnaf.applet_dir, self.name, filename),
            '%s/%s' % (Gnaf.applet_dir, filename)
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    
    def set_tooltip(self, text=None):
        if text == None:
            text = self.tooltip
        self.icon.set_tooltip_markup(text)
    
    def set_datamenu(self, data=None):
        if data == None:
            data = self.data
        self.datamenu = self.menu(data)
    
    def notify_send(self):
        if self.settings.get('notifications') == False:
            return
        icon_new = self.get_icon_path('new')
        for note in self.notifications:
            if type(note).__name__ == 'str':
                n = bash_quotes(note)
                command = "notify-send -i '%s' '%s'" % (icon_new, n)
            elif type(note).__name__ == 'tuple':
                icon = note[0] if note[0] != None else icon_new
                n1 = bash_quotes(note[1])
                if len(note) == 2:
                    command = "notify-send -i '%s' '%s'" % (icon, n1)
                elif len(note) >= 3:
                    n2 = bash_quotes(note[2])
                    command = "notify-send -i '%s' '%s' '%s'" % (icon, n1, n2)
            else:
                continue
            Shell(command)
        self.notifications = []
    
  #::Interaction methods
    def leftclick(self, icon):
        button = 1
        time = gtk.get_current_event_time()
        self.datamenu.popup(None, None, gtk.status_icon_position_menu, button,
                            time, self.icon)
    
    def rightclick(self, icon, button, time):
        self.contextmenu.popup(None, None, gtk.status_icon_position_menu,
                               button, time, self.icon)
    
    def menu(self, items):
        menu = gtk.Menu()
        for item in items:
            if type(item).__name__ == 'str':
                if item == '-':
                    menuItem = gtk.SeparatorMenuItem()
                else:
                    menuItem = gtk.MenuItem(item)
            else:
                menuItem = gtk.MenuItem(item[0])
                if type(item[1]).__name__ == 'list':
                    subMenu = self.menu(item[1])
                    menuItem.set_submenu(subMenu)
                    if len(item) == 3:
                        menuItem.set_tooltip_markup(item[2])
                elif type(item[1]).__name__ == 'str':
                    menuItem.set_tooltip_markup(item[1])
                elif type(item[1]).__name__ == 'instancemethod' or \
                     type(item[1]).__name__ == 'function':
                    if len(item) == 3 and type(item[2]).__name__ == 'tuple':
                        menuItem.connect('activate', lambda s, f=item[1], a=item[2]: f(*a))
                    else:
                        menuItem.connect('activate', lambda s, f=item[1]: f())
                        if len(item) == 3:
                            menuItem.set_tooltip_markup(item[2])
            menu.append(menuItem)
        menu.show_all()
        return menu
    
  #::Log methods
    def log(self, type, status=None):
        message = '[%s] %s: %s' % (
            time.strftime('%H:%M:%S'),
            self.settings_name,
            type
        )
        if status != None:
            status = '[%s]' % status
            message = format_L_R(message, status, '', 80, 1)
        write('%s\n' % message)        
    
    def debug_output(self):
        if self.settings.get('debug') != False:
            write('%s\n' % format_C(' DEBUG OUTPUT ', '*'))
            traceback.print_exc()
            write('%s\n' % format_C(' END DEBUG OUTPUT ', '*'))
    
    def next_update_at(self, from_id=True):
        if from_id:
            last = self.update_id
        else:
            last = time.time()
        return time.localtime(last + self.interval / 1000)
        

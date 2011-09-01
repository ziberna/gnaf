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

import time
import sys
import os

import lib.gui as gui
from lib.tools import id, tolist, dictmerge, thread, timeout, threadTimeout
from lib.write import logC, logTime, debug, writeln
from lib.format import timestamp

GnafApplets = []

class Gnaf(object):    
    def __init__(self, settings):
        self.settings = dictmerge(self.settings, settings)
        self.interval = self.settings['interval'] * 60
        # Flags and IDs initialization
        self.flag_init()
        # GUI initialization
        self.icon_init()
        self.tooltip_init()
        self.data_init()
        self.context_init()
        self.notifications_init()
        # Final
        global GnafApplets
        GnafApplets.append(self)
    
    def flag_init(self):
        self.enabled = True
        self.running = True
        self.initialized = False
        self.initializing = False
        self.initialize_id = 0
        self.updating = False
        self.update_id = 0
        self.notify_enabled = (not 'notify' in self.settings or self.settings['notify'])
        self.appletting = False
    
    # Main methods #
    @staticmethod
    def main():
        gui.ThreadsInit()
        global GnafApplets
        for applet in GnafApplets:
            thread(applet.run)
        gui.Main()
    
    @staticmethod
    def main_quit():
        logC('Gnaf applets quitting')
        global GnafApplets
        for applet in list(GnafApplets):
            applet.quit()
    
    def quit(self):
        self.log(status='QUIT')
        self.enabled = False
        self.running = False
        self.visible = False
        global GnafApplets
        GnafApplets.remove(self)
        if len(GnafApplets) == 0:
            gui.Quit()
    
    def enable_disable(self):
        self.enabled = not self.enabled
        self.log('Enabled', 'TRUE' if self.enabled else 'FALSE')
        self.context = []
    
    def run(self, update_id=None):
        if not self.running:
            return
        elif not self.enabled:
            threadTimeout(self.interval, self.run)
        elif not self.initialized and not self.initializing:
            self.initialize_applet()
        elif not self.updating and update_id == self.update_id:
            self.update_applet()
    
    def clear(self):
        self.log('Clearing data', '...')
        # Flags and IDs initialization
        self.flag_init()
        # GUI initialization
        self.icon = 'idle'
        self.tooltip = None
        self.data = 'Not updated yet.'
        self._context_time = []
        self._context_applet = []
        self.context = []
        self.log('Data clearance', 'DONE')
    
    def run_manual(self):
        self.update_id = id()
        self.run(self.update_id)
    
    def initialize_applet(self):
        # Set flags and GUI elements
        self.initializing = True
        self.log('Initializing', '...')
        self.icon = 'updating'
        self.tooltip = 'Initializing...'
        # Call applet's initialize method
        self.initialize_id = id()
        try:
            self.appletting = True
            success = self.initialize()
        except:
            success = None
            self.initialize_id = 0
            self.debug()
        finally:
            self.appletting = False
        # Determine success
        if success:
            self.initialized = True
            self.log('Initialization', 'TRUE')
            self.tooltip = 'Initialized.'
            self.update_id = id()
            thread(self.run, self.update_id)
        else:
            self.log('Initialization', 'ERROR')
            self.icon = 'error'
            self.tooltip = self.error_message()
            threadTimeout(self.interval, self.run)
        # Final
        self.initializing = False
    
    def update_applet(self):
        # Set flags and GUI elements
        self.updating = True
        self.log('Updating', '...')
        self.icon = 'updating'
        self.tooltip = 'Updating...'
        # Call applet's update method
        self.update_id = id()
        try:
            self.appletting = True
            success = self.update()
        except:
            success = None
            self.update_id = 0
            self.debug()
        finally:
            self.appletting = False
        # Determine success
        if success == True:
            self.log('Update', 'TRUE')
            self.icon = 'new'
            self.tooltip = None
        elif success == False:
            self.log('Update', 'FALSE')
            self.icon = 'idle'
            self.tooltip = None
        else:
            self.log('Update', 'ERROR')
            self.icon = 'error'
            self.tooltip = self.error_message()
        self.context = []
        # Add next update interval
        self.update_id = id()
        threadTimeout(self.interval, self.run, self.update_id)
        # Final
        self.updating = False
        if self.notify_enabled:
            self.notify_applet()
        gui.UpdateCount()
    
    def notify_applet(self):
        try:
            success = self.notify()
        except:
            success = None
            self.debug()
        
        if success == True:
            self.log('Notify', 'TRUE')
        elif success == False:
            self.log('Notify', 'FALSE')
        else:
            self.log('Notify', 'ERROR')
    
    # GUI elements #
    @property
    def icon(self): return self._icon.type
    
    @icon.setter
    def icon(self, value):
        if not self.was_set(self._icon):
            self._icon.type = value
    
    def icon_init(self):
        self.paths = [
            '%s/%s' % (Gnaf.user_dir, self.name),
            '%s' % (Gnaf.user_dir),
            '%s/%s/icons' % (Gnaf.applet_dir, self.name),
            '%s/%s' % (Gnaf.applet_dir, self.name),
            '%s' % (Gnaf.applet_dir)
        ]
        self._icon = gui.Icon(paths=self.paths, types=self.settings['icon'])
        self.visible = (not 'visible' in self.settings or self.settings['visible'])
        self._icon.type = 'idle'
    
    @property
    def visible(self): return self._visible
    
    @visible.setter
    def visible(self, value):
        self._visible = value
        self._icon.visible = value
    
    @property
    def tooltip(self): return self._tooltip.text
    
    @tooltip.setter
    def tooltip(self, value):
        if self.appletting:
            self._tooltip_applet = value
        elif value == None:
            value = self._tooltip_applet
        if not self.was_set(self._tooltip):
            self._tooltip.text = value
    
    def tooltip_init(self):
        self._tooltip = self._icon._tooltip
        self._tooltip_applet = None
    
    @property
    def data(self): return self._data.items
    
    @data.setter
    def data(self, value):
        value = tolist(value)
        if not self.was_set(self._data):
            self._data.items = value
    
    def data_init(self):
        self._data = self._icon._leftmenu
        self.data = 'Not updated yet.'
    
    @property
    def context(self): return self._context_applet
    
    @context.setter
    def context(self, value):
        value = tolist(value)
        if self.appletting:
            self._context_applet = value + ['-']
        elif self.updating:
            self._context_time = ['Next update at %s' % timestamp(id() + self.interval), '-']
        self._context_default = [
            ('Update now', self.run_manual),
            ('Clear data', self.clear),
            ('Mark as idle', self.mark_as_idle) if self.icon != 'idle' else None,
            ('%s notifications' % ('Disable' if self.notify_enabled else 'Enable'), self.notiy_enable_disable),
            '-',
            ('Hide', self.hide),
            ('Disable' if self.enabled else 'Enable', self.enable_disable),
            ('Quit', self.quit),
            ('Quit all', Gnaf.main_quit)
        ]
        self._context.items = self._context_applet + self._context_time + self._context_default
    
    def context_init(self):
        self._context = self._icon._rightmenu
        self._context_applet = []
        self._context_time = []
        self.context = []
    
    @property
    def notifications(self): return self._notifications.items
    
    @notifications.setter
    def notifications(self, value):
        if not self.notify_enabled:
            return
        value = tolist(value)
        if not self.was_set(self._notifications):
            self._notifications.items = value
    
    def notifications_init(self):
        iconpath = self._icon.path_from_type('new')
        self._notifications = gui.Notifier(auto=True,icon=iconpath)
    
    # Helper methods #
    def was_set(self, target):
        if self.appletting:
            return False
        if self.updating:
            return self.update_id > 0 and self.update_id < target.id
        if self.initializing:
            return self.initialize_id > 0 and self.initialize_id < target.id
        return False
    
    def log(self, subject=None, status=None):
        if subject != None:
            subject = '%s: %s' % (self.setting_name, subject)
        else:
            subject = self.setting_name
        logTime(subject, status)
    
    def debug(self):
        if 'debug' not in self.settings or self.settings['debug']:
            debug()
    
    def error_message(self):
        if self.initializing:
            message = 'Error while initializing.'
        elif self.updating:
            message = 'Error while updating.'
        else:
            message = 'Error occurred.'
        if self.updating or self.initializing:
            time = timestamp(id() + self.interval)
            message += ' Next try at %s' % time
        return message
    
    def mark_as_idle(self):
        self.icon = 'idle'
        self.context = []
    
    def notiy_enable_disable(self):
        self.notify_enabled = not self.notify_enabled
        self.log('Notifications enabled', 'TRUE' if self.notify_enabled else 'FALSE')
        self.context = []
    
    def hide(self):
        self.visible = False

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

import lib.gui as gui
from lib.tools import id, tolist, dictmerge, Dict, thread, threadTimeout, Regex
from lib.write import logC, logTime, debug
from lib.format import timestamp

GnafApplets = []

DefaultSettings = {
    'interval':60,
    'icon':{
        'idle':'idle.png',
        'new':'new.png',
        'updating':'updating.png',
        'error':'error.png'
    },
    'enabled':True,
    'debug':True,
    'visible':True,
    'notify':True,
    'alias':{},
    'ignore':[],
    'notification-stack':False,
    'menu-wrap':-1,
    'tooltip-wrap':-1,
    'icon-tooltip-wrap':-1,
    'wrap':50,
}

class Gnaf(object):    
    def __init__(self, settings):
        global DefaultSettings
        self.settings = dictmerge(DefaultSettings, self.settings, settings)
        self.interval = self.settings['interval'] * 60
        # Flags and IDs initialization
        self.flag_init()
        # GUI initialization
        gui.IdleAdd(self.gui_init)
        gui.IdleAdd(self.icon_init)
        gui.IdleAdd(self.tooltip_init)
        gui.IdleAdd(self.data_init)
        gui.IdleAdd(self.context_init)
        gui.IdleAdd(self.notifications_init)
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
        self.appletting = False
        self.value = Dict()
        self.id = Dict(1)
        self.regex = Regex()
        self.regex.alias_patterns = self.settings['alias']
        self.regex.ignore_patterns = self.settings['ignore']
    
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
        gui.IdleAdd(self.gui_del)
        global GnafApplets
        GnafApplets.remove(self)
        if len(GnafApplets) == 0:
            gui.Quit()
    
    def enable_disable(self):
        self.enabled = not self.enabled
        self.log('Enabled', 'TRUE' if self.enabled else 'FALSE')
        if self.enabled:
            self.icon = 'idle'
        self.context = []
        self.update_id = id()
        self.run(self.update_id)
    
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
        # GUI resets
        self.icon = 'idle'
        self.tooltip = None
        self.data = 'Not updated yet.'
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
            self.success = self.initialize()
        except:
            self.success = None
            self.initialize_id = 0
            self.debug()
        finally:
            self.appletting = False
        # Determine success
        if self.success:
            self.initialized = True
            self.log('Initialization', 'DONE')
            self.update_id = id()
            thread(self.run, self.update_id)
        else:
            self.log('Initialization', 'ERROR')
            self.icon = 'error'
            self.context = []
            threadTimeout(self.interval, self.run)
        self.tooltip = None
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
            self.success = self.update()
        except:
            self.success = None
            self.update_id = 0
            self.debug()
        finally:
            self.appletting = False
        # Determine success
        if self.success == True:
            self.log('Update', 'NEW')
            self.icon = 'new'
        elif self.success == False:
            self.log('Update', 'OLD')
            self.icon = 'idle'
        else:
            self.log('Update', 'ERROR')
            self.icon = 'error'
        self.tooltip = None    
        self.context = []
        # Add next update interval
        self.update_id = id()
        threadTimeout(self.interval, self.run, self.update_id)
        # Final
        self.updating = False
        if self.success and self.settings['notify']:
            self.notify_applet()
    
    def notify_applet(self):
        try:
            self.success = self.notify()
        except:
            self.success = None
            self.debug()
        
        if self.success == True:
            self.log('Notify', 'YES')
        elif self.success == False:
            self.log('Notify', 'NO')
        else:
            self.log('Notify', 'ERROR')
    
    # GUI methods #
    def gui_init(self):
        self.gui = gui.Gui()
        self.gui.regex = self.regex
        
        wrap = self.settings['wrap']
        menu_wrap = self.settings['menu-wrap']
        tooltip_wrap = self.settings['tooltip-wrap']
        icon_tooltip_wrap = self.settings['icon-tooltip-wrap']
        
        if menu_wrap <= 0: menu_wrap = wrap
        if tooltip_wrap <= 0: tooltip_wrap = wrap
        if icon_tooltip_wrap <= 0: icon_tooltip_wrap = wrap

        self.gui.menu_wrap = self.settings['menu-wrap'] = menu_wrap
        self.gui.tooltip_wrap = self.settings['tooltip-wrap'] = tooltip_wrap
        self.gui.icon_tooltip_wrap = self.settings['icon-tooltip-wrap'] = icon_tooltip_wrap
    
    def gui_del(self): del self.gui
    
    @property
    def icon(self): return self.value['icon']
    
    @icon.setter
    def icon(self, value):
        if not self.was_set(self.id['icon']):
            self.id['icon'] = id()
            self.value['icon'] = value
            gui.IdleAdd(self.icon_setter, value)
    
    def icon_setter(self, value): self.gui.icon(value)
    
    def icon_init(self):
        self.value['icon'] = 'idle'
        self.value['visible'] = ('visible' not in self.settings or self.settings['visible'])
        self.gui.icon_types = self.settings['icon']
        self.gui.icon_paths = [
            '%s/%s' % (Gnaf.user_dir, self.name),
            '%s' % (Gnaf.user_dir),
            '%s/%s/icons' % (Gnaf.user_dir, self.name),
            '%s/%s/icons' % (Gnaf.applet_dir, self.name),
            '%s/%s' % (Gnaf.applet_dir, self.name),
            '%s' % (Gnaf.applet_dir)
        ]
        self.gui.icon(self.value['icon'])
        self.gui.visible(self.value['visible'])
    
    @property
    def visible(self): return self.value['visible']
    
    @visible.setter
    def visible(self, value):
        self.id['visible'] = id()
        self.value['visible'] = value
        gui.IdleAdd(self.visible_setter, value)
        
    def visible_setter(self, value): self.gui.visible(value)
    
    @property
    def tooltip(self): return self.value['tooltip']
    
    @tooltip.setter
    def tooltip(self, value):
        if self.appletting:                
            self.value['tooltip-applet'] = value
        elif value == None:
            value = self.value['tooltip-applet']
        if not self.was_set(self.id['tooltip']):
            self.id['tooltip'] = id()
            self.value['tooltip'] = value
        gui.IdleAdd(self.tooltip_setter, value)
    
    def tooltip_setter(self, value): self.gui.tooltip(value)
    
    def tooltip_init(self):
        pass
    
    @property
    def data(self): return self.value['data']
    
    @data.setter
    def data(self, value):
        if not self.was_set(self.id['data']):
            value = tolist(value)
            self.id['data'] = id()
            self.value['data'] = value
            gui.IdleAdd(self.data_setter, value)
    
    def data_setter(self, value): self.gui.leftmenu(value)
    
    def data_init(self):
        self.value['data'] = ['Not updated yet.']
        self.gui.leftmenu(self.value['data'])
    
    @property
    def context(self): return self.value['context-applet']
    
    @context.setter
    def context(self, value):
        value = tolist(value)
        
        if self.appletting:
            self.value['context-applet'] = value
            value += ['-']
        else:
            time = timestamp(id() + self.interval)
            if self.updating:
                if self.success == None:
                    self.value['context-time'] = ['Error while updating. Next try at '+time,'-']
                else:
                    self.value['context-time'] = ['Next update at '+time,'-']
            elif self.initializing and self.success == None:
                self.value['context-time'] = ['Error while initializing. Next try at '+time,'-']
        
        self.value['context-default'] = self.context_default()
        value += self.value['context-time'] + self.value['context-default']
        gui.IdleAdd(self.context_setter, value)
    
    def context_setter(self, value): self.gui.rightmenu(value)
    
    def context_init(self):
        self.gui.rightmenu(self.context_default())
    
    def context_default(self):
        return [
            ('Update now', self.run_manual),
            ('Clear data', self.clear),
            ('Mark as idle', self.mark_as_idle) if self.icon != 'idle' else None,
            ('%s notifications' % ('Disable' if self.settings['notify'] else 'Enable'), self.notify_enable_disable),
            '-',
            ('Hide', self.hide),
            ('Disable' if self.enabled else 'Enable', self.enable_disable),
            ('Quit', self.quit),
            ('Quit all', Gnaf.main_quit)
        ]
    
    @property
    def notifications(self): return self.value['notifications']
    
    @notifications.setter
    def notifications(self, value):
        if not self.settings['notify']:
            return
        if not self.was_set(self.id['notifications']):
            self.id['notifications'] = id()
            self.value['notifications'] = value
            gui.IdleAdd(self.notifications_setter, tolist(value))
    
    def notifications_setter(self, value):
        for notification in value:
            self.gui.notify(notification)
    
    def notifications_init(self):
        self.gui.icon_path_notification = self.gui.icon_path_from_type('new')
        self.gui.notification_stack = self.settings['notification-stack']
    
    # Helper methods #
    def was_set(self, id):
        if not id:
            return False
        if self.appletting:
            return False
        if self.updating:
            return self.update_id > 0 and self.update_id < id
        if self.initializing:
            return self.initialize_id > 0 and self.initialize_id < id
        return False
    
    def log(self, subject=None, status=None):
        if subject != None:
            subject = '%s: %s' % (self.instance_name, subject)
        else:
            subject = self.instance_name
        logTime(subject, status)
    
    def debug(self):
        if self.settings['debug']:
            debug()
    
    def mark_as_idle(self):
        self.icon = 'idle'
        self.context = []
    
    def notify_enable_disable(self):
        self.settings['notify'] = not self.settings['notify']
        self.log('Notifications enabled', 'TRUE' if self.settings['notify'] else 'FALSE')
        self.context = []
    
    def hide(self):
        self.visible = False
    
    def show(self):
        self.visible = True
    
    def alias(self, str):
        return self.regex.alias(str)
    
    def ignore(self, str):
        return self.regex.ignore(str)

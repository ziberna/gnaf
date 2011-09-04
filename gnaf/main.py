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

import os; exists = os.path.exists
import sys

from gnaf import Gnaf
from lib.write import writeln, debug, logC, logLR
from lib.istype import *


def main():  
    # dirs, files
    user_dir, this_dir, applet_dir = dirs()
    settings_file = user_dir + '/settings.py'
    
    # python paths
    sys.path.insert(0, user_dir)
    sys.path.insert(1, applet_dir)
    
    # gnaf paths
    Gnaf.user_dir = user_dir
    Gnaf.this_dir = this_dir
    Gnaf.applet_dir = applet_dir
    
    # settings
    if not exists(settings_file):
        writeln('No settings file found. Create %s.' % settings_file)
        return False
    try:
        import settings
    except:
        debug()
        writeln('Error in settings file. Check %s.' % settings_file)
        return False
    
    # find applets
    applets = parse_settings(settings, user_dir, applet_dir)
    count = len(applets)
    if count == 0:
        writeln('No applets found. Check %s.' % settings_file)
        return False
    
    # start applets
    for applet in applets:
        if not applet_enabled(applet):
            count -= 1
            continue
        
        for instance in applet['instances']:
            instance(applet['settings'])
    
    if count == 0:
        writeln('No enabled or valid applets found.')
        return False
    
    # start GUI
    logC('Gnaf applets starting (%i total)' % count)
    Gnaf.main()


def dirs():
    user_dir = '%s/.gnaf' % os.getenv('HOME')
    this_dir = os.path.abspath(os.path.dirname(__file__))
    applet_dir = '%s/applets' % this_dir
    return user_dir, this_dir, applet_dir


def parse_settings(settings, user_dir, applet_dir):
    applets = []
    variables = vars(settings)
    
    for var in variables:
        setting = variables[var]
        if not isdict(setting) or 'applet' not in setting:
            continue
        
        instances = find_applet(user_dir, applet_dir, setting, var)
        if len(instances) == 0:
            continue
        
        applet = {
            'instances': instances,
            'settings': setting
        }
        applets.append(applet)
    
    return applets


def find_applet(user_dir, applet_dir, setting, setting_name):
    applets = []
    
    applet_name = setting['applet']
    class_name = None if not 'class' in setting else setting['class']
    
    user = applet_info(user_dir, 'user')
    installed = applet_info(applet_dir, 'installed')
    
    # search user and applet directories
    for source in [user, installed]:
        path = source['path'] + '/' + applet_name + '/'
        
        if not exists(path + '__init__.py') or not exists(path + 'applet.py'):
            continue
        
        # import module and get its variables
        try:
            module = applet_import(applet_name, source['type'])
        except:
            logLR('%s (%s)' % (setting_name, applet_name), 'IMPORT ERROR')
            if 'debug' not in setting or setting['debug']:
                debug()
            continue
        
        # extract variables
        variables = vars(module)
        # search for a certain variable
        if isstr(class_name) and class_name in variables:
            applets.append(variables[class_name])
        # search for variables as defined in a list
        elif islist(class_name):
            applets.extend(variables[c] for c in class_name if c in variables)
        # except all variables
        else:
            applets.extend(variables[var] for var in variables)
    
    # filter Gnaf classes
    applets = [applet for applet in applets if isgnaf(applet)]
    for applet in applets:
        logLR('%s: class %s (from %s)' % (setting_name, name(applet), applet_name), 'FOUND APPLET')
        applet.instance_name = setting_name
        applet.name = applet_name
    return applets


def applet_enabled(applet):
    return ('enabled' not in applet['settings'] or applet['settings']['enabled'] == True)


def applet_info(dir, applet_type):
    return {'path':dir,'type':applet_type}


def applet_import(name, applet_type):
    if applet_type == 'user':
        path = name + '.applet'
        level = -1
    elif applet_type == 'installed':
        path = 'gnaf.applets.' + name + '.applet'
        level = 0
    return __import__(path, globals(), locals(), ['*'], level)

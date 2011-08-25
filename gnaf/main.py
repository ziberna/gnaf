import os
import sys
import traceback
write = sys.stdout.write
from gnaf import Gnaf
from lib.format import format_L_R, format_C

def main():  
    # dirs
    user_dir, this_dir, applet_dir = get_paths()
    # python paths
    sys.path.insert(0, user_dir)
    sys.path.insert(1, applet_dir)
    # gnaf paths
    Gnaf.user_dir = user_dir
    Gnaf.this_dir = this_dir
    Gnaf.applet_dir = applet_dir
    # applets
    settings_file = '%s/settings.py' % user_dir
    if os.path.exists(settings_file):
        try:
            import settings
        except:
            write('%s\n' % format_C(' DEBUG OUTPUT ', '*'))
            traceback.print_exc()
            write('%s\n' % format_C(' END DEBUG OUTPUT ', '*'))
            write('Error in settings.py. Check the file in ~/.gnaf\n')
            return
        applets = parse_settings(settings, user_dir, applet_dir)
        applet_count = len(applets)
        if applet_count > 0:
            for applet in applets:
                if ('enabled' in applet['settings'] and applet['settings']['enabled'] == False) \
                    or len(applet['instances']) == 0:
                    applet_count -= 1
                else:
                    for app in applet['instances']:
                        app(applet['settings'])
            if applet_count > 0:
                write('%s\n' % format_C(' Gnaf applets starting (%i total) ' % applet_count, '-'))
                Gnaf.main()
            else:
                write('No enabled or valid applets found.\n')
        else:
            write('No applets found. Check settings in ~/.gnaf/setting.py.\n')
    else:
        write('No settings found. Create %s.' % settings_file)

def get_paths():
    user_dir = '%s/.gnaf' % os.getenv('HOME')
    this_dir = os.path.abspath(os.path.dirname(__file__))
    applet_dir = '%s/applets' % this_dir
    return user_dir, this_dir, applet_dir

def parse_settings(settings, user_dir, applet_dir):
    applets = []
    variables = vars(settings)
    for var in variables:
        sett = variables[var]
        if type(sett).__name__ == 'dict' and 'applet' in sett:
            classname = sett['class'] if 'class' in sett else None
            applet = {
                'instances': find_applet(user_dir, applet_dir, sett, classname, var),
                'settings': sett
            }
            applets.append(applet)
    return applets
    
def find_applet(user_dir, applet_dir, settings, classname, sett_name):
    applets = []
    applet = settings['applet']
    # check user and applet dirs
    for dir in [user_dir, applet_dir]:
        # check if applet exists
        if os.path.exists('%s/%s/__init__.py' % (dir, applet)) \
        and os.path.exists('%s/%s/applet.py' % (dir, applet)):
            # import module and get its variables
            module_path = ('%s.applet' % applet) if dir == user_dir else ('gnaf.applets.%s.applet' % applet)
            try:
                module = __import__(module_path, globals(), locals(), ['*'], -1 if dir == user_dir else 0)
            except:
                write('%s\n' % format_L_R('%s (%s applet)' % (sett_name, applet), '[IMPORT ERROR]', '', 80, 1))
                if 'debug' not in settings or settings['debug'] != False:
                    write('%s\n' % format_C(' DEBUG OUTPUT ', '*'))
                    traceback.print_exc()
                    write('%s\n' % format_C(' END DEBUG OUTPUT ', '*'))
                continue
            variables = vars(module)
            # search for a certain variable
            if type(classname).__name__ == 'str' and classname in variables:
                obj = variables[classname]
                applets.append(obj)
            # search for variables as defined in a list
            elif type(classname).__name__ == 'list':
                objs = [variables[cn] for cn in classname if cn in variables]
                for obj in objs:
                    applets.append(obj)
            # except all variables
            else:
                applets.extend(variables[var] for var in variables)
    # filter variables for subclasses of Gnaf
    applets = [a for a in applets if type(a).__name__ == 'classobj' and issubclass(a, Gnaf)]
    for a in applets:
        write('%s\n' % format_L_R('%s: class %s (from %s)' % (sett_name, a.__name__, applet), '[FOUND APPLET]', '', 80, 1))
        a.name = applet
        a.settings_name = sett_name
    return applets

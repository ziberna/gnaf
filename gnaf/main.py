import os
import sys
write = sys.stdout.write
from gnaf import Gnaf

def main():  
    # dirs  
    user_dir = '%s/.gnaf' % os.getenv('HOME')
    this_dir = os.path.abspath(os.path.dirname(__file__))
    applet_dir = '%s/applets' % this_dir
    # python paths
    sys.path.insert(0, user_dir)
    sys.path.insert(1, applet_dir)
    # gnaf paths
    Gnaf.user_dir = user_dir
    Gnaf.this_dir = this_dir
    Gnaf.applet_dir = applet_dir
    # applets
    import settings
    applets = parse_settings(settings, user_dir, applet_dir)
    if len(applets) > 0:
        for applet in applets:
            for a in applet[0]:
                a(applet[1])
        write ('--- Gnaf applets starting (%i total) ---\n' % len(applets))
        Gnaf.main()
    else:
        write('No applets found. Check settings in ~/.gnaf/setting.py.\n')

def parse_settings(settings, user_dir, applet_dir):
    applets = []
    variables = vars(settings)
    for var in variables:
        sett = variables[var]
        if type(sett).__name__ == 'dict' and 'applet' in sett:
            classname = sett['class'] if 'class' in sett else None
            applets.append((find_applet(user_dir, applet_dir, sett['applet'], classname, var), sett))
    return applets
    
def find_applet(user_dir, applet_dir, applet, classname, setting):
    applets = []
    # check user and applet dirs
    for dir in [user_dir, applet_dir]:
        # check if applet exists
        if os.path.exists('%s/%s/__init__.py' % (dir, applet)) \
        and os.path.exists('%s/%s/applet.py' % (dir, applet)):
            # import module and get its variables
            module_path = ('%s.applet' % applet) if dir == user_dir else ('gnaf.applets.%s.applet' % applet)
            module = __import__(module_path, globals(), locals(), ['*'], -1 if dir == user_dir else 0)
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
        write('Found applet for %s: class %s (from %s)\n' % (setting, a.__name__, applet))
        a.name = applet
        a.settings_name = setting
    return applets

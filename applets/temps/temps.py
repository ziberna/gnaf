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

from gnaf.lib.tools import Shell

def Temps(method):
    if method == 'sensors':
        return Sensors()
    else:
        return None

def Sensors():
    output = Shell('sensors').output
    lines = output.split('\n')
    lines = [l for l in lines if l != '']
    lines = [l for l in lines if not l.startswith('Adapter')]
    temps = []
    for line in lines:
        if not line.startswith('fan') \
        and not line.startswith('temp') \
        and not line.startswith('Core'):
            temps.append({'id':line,'values':[]})
        else:
            line = line.replace('Core ', 'core')
            val = line.split(' ')
            val = [v for v in val if v != '']
            if len(val) > 0 and not '+0.0\xc2\xb0C' in val[1]:
                if val[1][0] == '+':
                    val[1] = val[1][1:]
                temps[-1]['values'].append({'id':val[0][:-1],'value':val[1]})
    return temps

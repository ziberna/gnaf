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

import gnaf
from temps import Temps
from gnaf.lib.format import format_L_R, format_tooltip

class TempsApplet(gnaf.Gnaf):
    settings = {
        'interval':3,
        'icon':{
            'new':None,
            'updating':None,
            'idle':None,
            'error':None
        },
        'method':'sensors',
        'critical':75
    }
    
    def initialize(self):
        return True
    
    def update(self):
        temps = Temps(self.settings.get('method'))
        critical = False
        critical_limit = self.settings.get('critical')
        data = []
        templist = []
        fanlist = []
        for temp in temps:
            id = temp['id']
            values = []
            tlist = []
            flist = []
            for t in temp['values']:
                if t['value'][-1] == 'C':
                    val = float(t['value'].replace('\xc2\xb0C', ''))
                    if val > 0:
                        tlist.append(val)
                    if val >= critical_limit:
                        critical = True
                else:
                    val = float(t['value'])
                    if val > 0:
                        flist.append(val)
                    t['value'] = '%s RPM' % t['value']
                values.append(format_L_R('%s:' % t['id'], t['value'], '', 40, 1))
            templist.extend(tlist)
            fanlist.extend(flist)
            data.append((
                id,
                values
            ))
        self.data = data
        self.tooltip = format_tooltip([
            ('Temp', '%.1f \xc2\xb0C' % (sum(templist) / len(templist))),
            ('Fan', '%.1f RPM' % (sum(fanlist) / len(fanlist)))
        ])
        return critical
    
    def notify(self):
        return None

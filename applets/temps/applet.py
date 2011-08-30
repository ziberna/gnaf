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
from gnaf.lib.format import formatTooltip

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
        'critical':75,
        'ignore':[],
        'alias':{}
    }
    
    def initialize(self):
        self.method = self.settings.get('method')
        self.critical_limit = self.settings.get('critical')
        self.critical = False
        self.ignore = self.settings.get('ignore')
        self.alias = self.settings.get('alias')
        return True
    
    def update(self):
        temps = Temps(self.method)
        self.critical = False
        data = []
        templist = []
        fanlist = []
        for temp in temps:
            if temp['id'] in self.ignore:
                continue
            id = temp['id'] if not temp['id'] in self.alias else self.alias[temp['id']]
            values = []
            tlist = []
            flist = []
            for t in temp['values']:
                if t['id'] in self.alias:
                    t['id'] = self.alias[t['id']]
                if t['value'][-1] == 'C':
                    val = float(t['value'].replace('\xc2\xb0C', ''))
                    tlist.append(val)
                    if val >= self.critical_limit:
                        self.critical = True
                        self.critical_value = val
                        self.critical_id = t['id']
                else:
                    val = float(t['value'])
                    flist.append(val)
                    t['value'] = '%s RPM' % t['value']
                values.append('%s: %s' % (t['id'], t['value']))
            templist.extend(tlist)
            fanlist.extend(flist)
            data.append((
                id,
                values
            ))
        self.data = data
        temp_str = 'no information' if len(templist) == 0 else '%.1f\xc2\xb0C' % (sum(templist) / len(templist))
        fan_str = 'no information' if len(fanlist) == 0 else '%.1f RPM' % (sum(fanlist) / len(fanlist))
        self.tooltip = formatTooltip([
            ('Temperatures', temp_str),
            ('Fan speeds', fan_str)
        ])
        return self.critical
    
    def notify(self):
        if self.critical:
            value = self.critical_value
            id = self.critical_id.capitalize()
            self.notifications = ['%s is at %.1f\xc2\xb0C!' % (id, value)]
        return self.critical


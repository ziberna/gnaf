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
            'idle':'temp.png',
            'error':'temp.png',
            'temp1':'temp1.png',
            'temp2':'temp2.png',
            'temp3':'temp3.png',
            'temp4':'temp4.png',
            'temp5':'temp5.png'
        },
        'method':'sensors',
        'critical':75,
        'low':20,
        'ignore':[],
        'alias':{}
    }
    
    def initialize(self):
        self.method = self.settings['method']
        self.critical_limit = self.settings['critical']
        low = self.settings['low']
        step = float(self.critical_limit - low) / 4
        self.steps = {
            '1':low + step,
            '2':low + step * 2,
            '3':low + step * 3,
            '4':self.critical_limit
        }
        self.critical = False
        self.ignore = self.settings['ignore']
        self.alias = self.settings['alias']
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
        temp_avg = sum(templist) / len(templist)
        fan_avg = sum(fanlist) / len(fanlist)
        
        step = '5'
        for key in self.steps:
            if temp_avg < self.steps[key]:
                step = key
                break
        self.icon = 'temp' + step
        
        self.data = data
        temp_str = 'no information' if len(templist) == 0 else '%.1f\xc2\xb0C' % temp_avg
        fan_str = 'no information' if len(fanlist) == 0 else '%.1f RPM' % fan_avg
        self.tooltip = formatTooltip([
            ('Temperatures', temp_str),
            ('Fan speeds', fan_str)
        ])
        return self.critical
    
    def notify(self):
        if self.critical:
            value = self.critical_value
            id = self.critical_id.capitalize()
            self.notifications = '%s is at %.1f\xc2\xb0C!' % (id, value)
        return self.critical

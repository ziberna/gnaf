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
            'new':'temp5.png',
            'temp1':'temp1.png',
            'temp2':'temp2.png',
            'temp3':'temp3.png',
            'temp4':'temp4.png',
            'temp5':'temp5.png'
        },
        'method':'sensors',
        'max':75,
        'min':20
    }
    
    def initialize(self):
        self.method = self.settings['method']
        self.max = self.settings['max']
        self.min = self.settings['min']
        step = float(self.max - self.min) / 4
        self.steps = {
            '1':self.min + step,
            '2':self.min + step * 2,
            '3':self.min + step * 3,
            '4':self.max
        }
        self.critical = False
        return True
    
    def update(self):
        temps = Temps(self.method)
        self.critical = False
        self.critical_value = 0.0
        data = []
        templist = []
        fanlist = []
        for temp in temps:
            if self.ignore(temp['id']):
                continue
            values = []
            for t in temp['values']:
                if self.ignore(t['id']):
                    continue
                if t['value'][-1] == 'C':
                    val = float(t['value'].replace('\xc2\xb0C', ''))
                    templist.append(val)
                    if val >= self.max and val > self.critical_value:
                        self.critical = True
                        self.critical_value = val
                        self.critical_id = t['id']
                else:
                    val = float(t['value'])
                    fanlist.append(val)
                    t['value'] = '%s RPM' % t['value']
                values.append('%s: %s' % (t['id'], t['value']))
            data.append((
                temp['id'],
                values
            ))
        temp_avg = sum(templist) / len(templist)
        fan_avg = sum(fanlist) / len(fanlist)
        
        step = '5'
        top = max(templist)
        for key in self.steps:
            if top < self.steps[key]:
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
            id = self.critical_id
            self.notifications = '%s is at %.1f\xc2\xb0C!' % (id, value)
        return self.critical

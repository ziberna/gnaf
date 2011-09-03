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

from rtorrent import RTorrent
import gnaf
from gnaf.lib.format import formatTooltip
from gnaf.lib.write import debug

class RTorrentApplet(gnaf.Gnaf):
    settings = {
        'icon':{
            'idle':'idle.png',
            'new':'new.png',
            'downloading':'downloading.png',
            'seeding':'seeding.png',
            'both':'both.png',
            'stopped':'stopped.png'
        },
        'interval':5,
        'server':'http://localhost'
    }
    
    def initialize(self):
        self.rtorrent = RTorrent(self.settings['server'])
        self.uncompleted = []
        self.new = []
        return True
    
    def update(self):
        try:
            self.torrents = self.rtorrent.get_torrents()
            downloaded, uploaded, downspeed, upspeed = self.rtorrent.get_global_vars()
        except:
            self.tooltip = 'RTorrent or RPC server isn\'t running.'
            self.data = self.tooltip
            self.icon = 'idle'
            return False
        if len(self.torrents) == 0:
            self.uncompleted = []
            self.tooltip = 'No torrents opened.'
            self.data = self.tooltip
            self.icon = 'idle'
            return False
        
        self.filter_new()
        
        data = []
        downloading_count = 0
        seeding_count = 0
        completed_count = 0
        stopped_count = 0
        ETA = 0
        
        for t in self.torrents:
            if len(t['name']) > 30:
                t['name'] = t['name'][:27] + '...'
            if t['state'] == 0:
                if t['percentage'] == 100.0:
                    state = 'completed'
                    state_symbol = '\xe2\x9c\x93'
                    completed_count += 1
                else:
                    state = 'stopped'
                    state_symbol = '\xc3\x97'
                    stopped_count += 1
            else:
                if t['percentage'] == 100.0:
                    state = 'seeding'
                    state_symbol = '\xe2\x86\x91'
                    seeding_count += 1
                else:
                    state = 'downloading'
                    state_symbol = '\xe2\x86\x93'
                    downloading_count += 1
            if t['ETA'] > ETA: ETA = t['ETA']
            info = [
                ('ETA', seconds_to_str(t['ETA'])) if t['ETA'] > 0 else None,
                ('Downloaded', bytes_to_str(t['downloaded']) + ((' / ' + bytes_to_str(t['size'])) if t['percentage'] != 100.0 else '')),
                ('Uploaded', bytes_to_str(t['uploaded'])),
                ('Ratio', '%.2f' % t['ratio']),
                ('Down', bytes_to_str(t['downspeed'], True) + '/s') if t['percentage'] != 100.0 or t['state'] != 0 else None,
                ('Up', bytes_to_str(t['upspeed'], True) + '/s') if t['state'] != 0 else None,
                ('Files', str(t['files']) + ' / ' + str(t['total-files'])),
                ('Total size', bytes_to_str(t['total-size'])) if t['total-size'] != t['downloaded'] else None
            ]
            info = [i for i in info if i != None]
            data.append((
                '[%s] %s (%s%%)' % (state_symbol, t['name'], ('%.2f' % t['percentage']) if t['percentage'] != 100.0 else '100'),
                formatTooltip(info)
            ))
        self.data = data
        
        self.tooltip = formatTooltip([
            '%i\xe2\x86\x93 / %i\xe2\x86\x91 / %i\xe2\x9c\x93 / %i\xc3\x97' % (downloading_count, seeding_count, completed_count, stopped_count),
            ('Downloaded', bytes_to_str(downloaded)),
            ('Uploaded', bytes_to_str(uploaded)),
            ('Down', bytes_to_str(downspeed, True) + '/s'),
            ('Up', bytes_to_str(upspeed, True) + '/s'),
            ('ETA', seconds_to_str(ETA))
        ])
        
        if len(self.new) > 0:
            self.icon = 'new'
        elif downloading_count > 0:
            if seeding_count > 0:
                self.icon = 'both'
            else:
                self.icon = 'downloading'
        elif seeding_count > 0:
            self.icon = 'seeding'
        else:
            self.icon = 'stopped'
        
        return (len(self.new) > 0)
    
    def notify(self):
        if len(self.new) == 0:
            return False
        notifications = []
        for n in self.new:
            notifications.append((
                n['name'],
                formatTooltip([
                    ('Uploaded', bytes_to_str(n['uploaded'])),
                    ('Ratio', '%.2f' % n['ratio'])
                ])
            ))
        self.notifications = notifications
        return True
    
    def filter_new(self):
        completed = [t for t in self.torrents if t['percentage'] == 100]
        self.new = []
        for u in self.uncompleted:
            for c in completed:
                if u['id'] == c['id']:
                    self.new.append(c)
                    completed.remove(c)
                    break
        self.uncompleted = [t for t in self.torrents if t['percentage'] < 100]
    

def bytes_to_str(bytes, kilo_preferred=False):
    kilo_limit = 1024 if kilo_preferred else 10.24
    
    bytes = float(bytes)
    kilo = bytes / 1024
    if kilo <= kilo_limit:
        return '%.2f kB' % kilo
    mega = kilo / 1024
    if mega <= 1024:
        return '%.2f MB' % mega
    giga = mega / 1024
    return '%.2f GB' % giga

def seconds_to_str(seconds):
    seconds = float(seconds)
    if seconds < 60:
        return '%.0f sec' % seconds
    minutes = seconds / 60
    if minutes < 60:
        return '%.0f min' % minutes
    hours = minutes / 60
    minutes = int(minutes) % 60
    if hours < 24:
        return '%.0f h, %i min' % (hours, minutes)
    days = hours / 24
    hours = int(hours) % 24
    if days < 7:
        return '%.0f days, %i h, %i min' % (days, hours, minutes)
    weeks = days / 7
    days = int(days) % 7
    return '%.0f weeks, %i days, %i h, %i min' % (weeks, days, hours, minutes)

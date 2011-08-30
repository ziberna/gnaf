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

class RTorrentApplet(gnaf.Gnaf):
    settings = {
        'icon':{
            'new':None,
            'idle':None,
            'updating':None,
            'error':None
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
            self.torrents = self.rtorrent.update()
        except:
            return None
        self.filter_new()
        data = []
        for t in self.torrents:
            tooltip = [
                ('ETA', seconds_to_str(t['ETA'])),
                ('Size', bytes_to_str(t['size'])),
                ('Ratio', '%.2f' % t['ratio'])
            ]
            if t['ETA'] == 0:
                del tooltip[0]
            data.append((
                '%s (%.0f%%)' % (t['name'], t['percentage']),
                formatTooltip(tooltip)
            ))
        self.data = data
        self.tooltip = '%i torrent(s)' % len(self.torrents)
        return (len(self.new) > 0)
    
    def notify(self):
        if len(self.new) == 0:
            return False
        title = '%i torrent(s) completed' % len(self.new)
        body = '\n'.join(t['name'] for t in self.new)
        self.notifications = (title, body)
        self.uncompleted = [t for t in self.torrents if t['percentage'] < 100]
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
    

def bytes_to_str(bytes):
    bytes = float(bytes)
    kilo = bytes / 1024
    if kilo <= 10.24:
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

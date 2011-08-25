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

from xmlrpclib import ServerProxy
    
class RTorrent:
    def __init__(self, server):
        self.server = ServerProxy(server)
        self.torrents = None
    
    def update(self):
        downloads = self.server.download_list()
        torrents = []
        D = self.server.d
        for d in downloads:
            t = {}
            t['id'] = d
            t['name'] = D.get_name(d)
            t['size'] = D.get_size_bytes(d)
            t['files'] = D.get_size_files(d)
            t['state'] = D.get_state(d)
            t['downloaded'] = D.get_bytes_done(d)
            t['uploaded'] = D.get_up_total(d)
            t['downspeed'] = D.get_down_rate(d)
            t['upspeed'] = D.get_up_rate(d)
            t['ratio'] = float(D.get_ratio(d)) / 1000
            t['percentage'] = float(t['downloaded']) / t['size'] * 100
            if t['downspeed'] > 0:
                t['ETA'] = float(t['size'] - t['downloaded']) / t['downspeed']
            else:
                t['ETA'] = 0
            torrents.append(t)
        self.torrents = torrents
        return self.torrents

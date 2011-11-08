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
    
    def get_torrents(self):
        downloads = self.server.download_list()
        torrents = []
        D = self.server.d
        for d in downloads:
            t = {}
            t['id'] = d
            t['name'] = D.get_name(d)
            t['total-files'] = D.get_size_files(d)
            t['total-size'] = D.get_size_bytes(d)
            t['size'], t['downloaded'], t['files'] = self.get_enabled_bytes(d, t['total-files'])
            t['state'] = D.get_state(d)
            t['uploaded'] = D.get_up_total(d)
            t['downspeed'] = D.get_down_rate(d)
            t['upspeed'] = D.get_up_rate(d)
            t['ratio'] = float(D.get_ratio(d)) / 1000
            t['percentage'] = float(t['downloaded']) / float(t['size']) * 100.0
            if t['downspeed'] > 0:
                t['ETA'] = float(t['size'] - t['downloaded']) / t['downspeed']
            else:
                t['ETA'] = 0
            peers_connected = D.peers_connected(d)
            t['seeds'] = D.peers_complete(d)
            t['peers'] = peers_connected - t['seeds']
            t['total-peers'] = peers_connected + D.peers_not_connected(d)
            torrents.append(t)
        self.torrents = torrents
        return self.torrents
    
    def get_enabled_bytes(self, id, file_count):
        all = 0.0
        completed = 0.0
        files = 0
        for f in range(0,file_count):
            if self.server.f.get_priority(id, f) == 0:
                continue
            files += 1
            chunks = float(self.server.f.get_size_chunks(id, f))
            chunks_completed = float(self.server.f.get_completed_chunks(id, f))
            bytes = float(self.server.f.get_size_bytes(id, f))
            all += bytes
            completed += (chunks_completed / chunks) * bytes
        return all, completed, files
    
    def get_global_vars(self):
        downloaded = self.server.get_down_total()
        uploaded = self.server.get_up_total()
        downspeed = self.server.get_down_rate()
        upspeed = self.server.get_up_rate()
        return downloaded, uploaded, downspeed, upspeed

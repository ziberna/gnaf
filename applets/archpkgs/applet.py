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
from arch_pkgs import ArchPkgs

class ArchPkgsApplet(gnaf.Gnaf):
    settings = {
        'interval':15,
        'icon':{
            'idle':'idle.png',
            'new':'new.png',
            'updating':'updating.png',
            'error':'error.png'
        },
        'repos':[
            'core',
            'extra',
            'community',
            'multilib',
            'aur'
        ],
        'aur':None
    }
    
    def initialize(self):
        self.ArchPkgs = ArchPkgs(self.settings.get('aur'))
        return self.ArchPkgs.pacman

    def update(self):
        pkgs = self.ArchPkgs.search()
        if pkgs == None:
            return None
        count = len(pkgs)
        if count == 0:
            self.tooltip = 'No updates, your system is up-to-date!'
            self.data = ['What, you think I\'m lying?']
            return False
        else:
            self.tooltip = '%i update(s)!' % count
            repos = self.settings.get('repos')
            data = []
            for repo in repos:
                repo_pkgs = [p for p in pkgs if p.repo == repo]
                repo_count = len(repo_pkgs)
                if repo_count > 0:
                    data.append((
                        '%s (%i)' % (repo, repo_count),
                        ['%s (%s -> %s)' % (p.name, p.old_version, p.version) for p in repo_pkgs]
                    ))
            self.data = data
            return True

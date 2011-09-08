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
from archpkgs import ArchPkgs

from gnaf.lib.format import formatTooltip
from gnaf.lib.istype import isint

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
        self.repos = self.settings['repos']
        self.ArchPkgs = ArchPkgs(self.repos, self.settings['aur'])
        self.pkgs_old = []
        return self.ArchPkgs.pacman

    def update(self):
        self.pkgs = self.ArchPkgs.search()
        if self.pkgs == None:
            return None
        count = len(self.pkgs)
        if count == 0:
            self.tooltip = 'No updates, your system is up-to-date!'
            self.data = 'Your system is up-to-date!'
            return False
        else:
            self.tooltip = '%i update(s)!' % count
            data = []
            for repo in self.repos:
                repo_pkgs = [p for p in self.pkgs if p.repo == repo]
                repo_count = len(repo_pkgs)
                if repo_count > 0:
                    p = repo_pkgs[0]
                    data.append((
                        '%s (%i)' % (repo, repo_count),
                        [('%s (%s -> %s)' % (p.name, p.version_old, p.version),
                          formatTooltip([(p.info[key][0],p.info[key][1]) for key in p.info if isint(key)])) for p in repo_pkgs]
                    ))
            self.data = data
            return True
    
    def notify(self):
        pkgs_new = list(self.pkgs)
        for p_old in self.pkgs_old:
            for p_new in pkgs_new:
                if p_new.name == p_old.name and p_new.version == p_old.version:
                    pkgs_new.remove(p_new)
                    break
        self.pkgs_old = list(self.pkgs)
        if len(pkgs_new) > 0:
            title = '%s new package(s)' % len(pkgs_new)
            body = ''
            for repo in self.repos:
                repo_pkgs = [p for p in pkgs_new if p.repo == repo]
                if len(repo_pkgs) == 0:
                    continue
                body += '<b>%s (%i)</b>:\n' % (repo, len(repo_pkgs))
                body += ''.join(['  %s (%s -> %s)\n' % (p.name, p.version_old, p.version) for p in repo_pkgs])
            self.notifications = (title, body)
            return True
        else:
            return False

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

import os
from gnaf.lib.shell import Shell

class Package:
    def __init__(self, name, version=None, version_old=None, repo=None):
        self.name = name
        self.version = version
        self.version_old = version_old
        self.repo = repo

class ArchPkgs:
    temp_dir = '/tmp/gnaf-arch-pkgs'
    pacman_dir = '/var/lib/pacman'
    local_dir = 'local'
    current_dir = os.path.dirname(__file__)
    
    def __init__(self, repos, aur_method=None):
        self.aur_method = aur_method
        self.init = Shell('%s/./init.bash %s %s %s' % (self.current_dir,
                                                     self.temp_dir,
                                                     self.pacman_dir,
                                                     self.local_dir))
        self.pacman = (self.init.output == 'start\nsuccess\n')
        self.repos = repos
    
    def search(self):
        if self.pacman == False:
            return None
        syb = Shell('fakeroot pacman -Syb %s' % self.temp_dir)
        if self.pacman_db_lock(syb.output) or self.pacman_no_conn(syb.output):
            return None
        qub = Shell('pacman -Qub %s' % self.temp_dir)
        if self.pacman_db_lock(qub.output):
            return None
        self.pkgs = self.parse_Qub(qub.output)
        self.parse_Ssb()
        self.aur()
        return self.pkgs
    
    def parse_Qub(self, output):
        pkgs_raw = output.split('\n')
        pkgs_raw = [pr for pr in pkgs_raw if pr != '']
        pkgs = []
        for pkg_raw in pkgs_raw:
            pkg_raw = pkg_raw.split(' ')
            # -Qub outputs name and old version
            pkgs.append(Package(pkg_raw[0], None, pkg_raw[1], None))
        return pkgs
    
    def parse_Ssb(self, pkgs=None):
        if pkgs == None:
            pkgs = self.pkgs
        for pkg in pkgs:
            output = Shell('pacman -Ss ^%s$ -b %s' % (pkg.name, self.temp_dir)).output.split('\n')[0]
            output = output.split(' ')
            repo = output[0].split('/')[0]
            version = output[1]
            pkg.repo = repo
            pkg.version = version
        self.pkgs = pkgs
        return self.pkgs
    
    def pacman_db_lock(self, output):
        return (output.split('\n')[0] == 'error: failed to init transaction (unable to lock database)')
    
    def pacman_no_conn(self, output):
        return False # old code didn't work
    
    def aur(self):
        if self.aur_method == 'cower':
            self.cower()
        else:
            return None
    
    def cower(self):
        cower = Shell('cower -u').output.split('\n')[:-1]
        for c in cower:
            c = c.split(' ')
            if c[0] == 'error:':
                continue
            else:
                self.pkgs.append(Package(c[1], c[4], c[2], 'aur'))

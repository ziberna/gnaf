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

import subprocess as sp

class Shell:
    def __init__(self, command):
        self.command = command
        p = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        self.pid = p.pid
        self.output, self.error = p.communicate()
        self.failed = p.returncode

def bash_quotes(str):
    return str.replace("'", "'\\''")
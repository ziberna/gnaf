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

class DictMerge:
    def __init__(self, *args):
        self.dictionaries = list(args)
        self.count = len(self.dictionaries)
    
    def get(self, *args):
        temps = list(self.dictionaries)
        for arg in args:
            i = 0
            while i < len(temps):
                if type(temps[i]).__name__ == 'dict' and arg in temps[i]:
                    temps[i] = temps[i][arg]
                    i += 1
                else:
                    del temps[i]
        return (temps[0] if len(temps) > 0 else None)
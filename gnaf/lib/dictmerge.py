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
    def __init__(self, *dicts):
        self.dictionaries = list(dicts)
        self.count = len(self.dictionaries)
    
    def get(self, *keys):
        return self.get_or_else(keys, None)
    
    def get_or_else(self, keys, else_value):
        temps = list(self.dictionaries)
        for arg in keys:
            i = 0
            while i < len(temps):
                if type(temps[i]).__name__ == 'dict' and arg in temps[i]:
                    temps[i] = temps[i][arg]
                    i += 1
                else:
                    del temps[i]
        return (temps[0] if len(temps) > 0 else else_value)
    
    def set(self, keys, value):
        d = {}
        d_tmp = d
        k_count = len(keys)
        k_end = k_count - 1
        for i in range(len(keys)):
            key = keys[i]
            if i == k_end:
                d_tmp[key] = value
            else:
                d_tmp[key] = {}
                d_tmp = d_tmp[key]
        self.dictionaries.insert(0, d)
        self.count = len(self.dictionaries)
        
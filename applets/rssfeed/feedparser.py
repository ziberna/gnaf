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

import urllib
import xml.etree.ElementTree as etree

NAMESPACE = 'http://www.w3.org/2005/Atom'

class Entry:
    def __init__(self, entry):
        self.title = entry.find('{%s}title' % NAMESPACE).text
        self.author = entry.find('{%s}author' % NAMESPACE).find('{%s}name' % NAMESPACE).text

class FeedParser:
    def __init__(self, url, namespace=None):
        if namespace != None:
            global NAMESPACE
            NAMESPACE = namespace
        self.url = url
    
    def update(self):
        try:
            self.file = urllib.urlopen(self.url)
            return True
        except (IOError,) as err:
            return None
    
    def parse(self):
        self.tree = etree.parse(self.file)
        self.root = self.tree.getroot()
        entries = self.root.findall('{%s}entry' % NAMESPACE)
        self.entries = []
        for entry in entries:
            self.entries.append(Entry(entry))
        return self.entries

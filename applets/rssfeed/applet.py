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

from feedparser import FeedParser
import random
import gnaf

class RssFeed(gnaf.Gnaf):
    settings = {
        'interval':15,
        'icon':{
            'idle':'idle.png',
            'new':'new.png',
            'updating':'updating.png',
            'error':'error.png'
        },
        'url':'http://feeds.bbci.co.uk/news/rss.xml',
        'namespace':'http://www.w3.org/2005/Atom',
        'entries-num':30,
        'max-title-length':75,
        'random':False
    }

    def initialize(self):
        url = self.settings.get('url')
        namespace = self.settings.get('namespace')
        self.FeedParser = FeedParser(url, namespace)
        self.tooltip = 'Feed URL: %s' % url
        return True

    def update(self):
        update = self.FeedParser.update()
        if update == None:
            return None
        else:
            entries = self.FeedParser.parse()
            if entries == None:
                return None
            elif len(entries) > 0:
                if self.settings.get('random'):
                    random.shuffle(entries)
                data = []
                num = self.settings.get('entries-num')
                length = self.settings.get('max-title-length')
                for entry in entries[:num]:
                    if length != None and len(entry.title) > length:
                        entry.title = '%s...' % entry.title[:length-3]
                    data.append((entry.title,entry.author))
                self.data = data
                return True
            else:
                return False

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
        'entries-num':10,
        'max-title-length':75,
        'random':False
    }

    def initialize(self):
        url = self.settings.get('url')
        namespace = self.settings.get('namespace')
        self.FeedParser = FeedParser(url, namespace)
        self.entries_old = None
        self.tooltip = 'Feed URL: %s' % url
        return True

    def update(self):
        update = self.FeedParser.update()
        if update == None:
            return None
        else:
            self.entries = self.FeedParser.parse()
            if self.entries == None:
                return None
            elif len(self.entries) > 0:
                if self.settings.get('random'):
                    random.shuffle(entries)
                num = self.settings.get('entries-num')
                self.entries = self.entries[:num]
                self.filter_new()
                length = self.settings.get('max-title-length')
                data = []
                for entry in self.entries:
                    if length != None and len(entry.title) > length:
                        entry.title = '%s...' % entry.title[:length-3]
                    data.append((
                        entry.title,
                        '<b>Author:</b> %s\n<b>Published:</b> %s' % (
                            entry.author,
                            entry.published.strftime('%d %b %Y at %H:%M')
                        )
                    ))
                self.data = data
                return len(self.entries_new) > 0
            else:
                return False
            
    def notify(self):
        if len(self.entries_new) == 0:
            return False
        title = '%i new feed entries' % len(self.entries_new)
        body = '\n'.join(['%s... (%s)' % (e.title[:10], e.author) for e in self.entries_new])
        self.notifications = [(None, title, body)]
        return True
    
    def filter_new(self):
        # return empty list on first run
        if self.entries_old == None:
            self.entries_old = list(self.entries)
            self.entries_new = []
        self.entries_new = list(self.entries)
        for e_old in self.entries_old:
            for e_new in self.entries_new:
                if e_new.title == e_old.title and e_new.published_str == e_old.published_str:
                    self.entries_new.remove(e_new)
                    break
        self.entries_old = list(self.entries)

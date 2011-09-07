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
from mail import Mail
from gnaf.lib.tools import Shell
from gnaf.lib.format import formatTooltip, bashQuotes

class MailApplet(gnaf.Gnaf):
    settings = {
        'interval':15,
        'icon':{
            'idle':'idle.png',
            'updating':'updating.png',
            'new':'new.png',
            'error':'error.png'
        },
        'username':'',
        'password':'',
        'host':'',
        'port':'auto',
        'ssl':True,
        'mailboxes':[
        '   Inbox'
        ],
        'url':None
    }
    
    def initialize(self):
        sett = self.settings
        self.Mail = Mail(
            sett['username'],
            sett['password'],
            sett['host'],
            sett['port'],
            sett['ssl']
        )
        self.mailboxes = sett['mailboxes']
        self.mails_old = {}
        
        return True
    
    def update(self):
        self.get_unreads()
        if self.mail_count == 0:
            self.data = ['No new mail...']
            self.tooltip = 'No new mail...'
            self.mails_old = {}
            return False
        if 'Inbox' in self.mails:
            self.remove_duplicates()
        data = []
        # loop through user's mailbox list instead, to ensure correct mailbox order
        for mailbox in self.mailboxes:
            if mailbox not in self.mails:
                continue
            mails = []
            for mail in self.mails[mailbox]:
                mails.append((mail['Subject'],
                             self.open_browser,
                             formatTooltip([
                                ('From', mail['From']),
                                ('Date', mail['Date'])
                             ])
                ))
            data.append((
                '%s (%s)' % (mailbox, len(mails)),
                mails
            ))
        self.data = data
        self.tooltip = '%i new mail(s)!' % self.mail_count
        return (True if not self.mail_failed else None)
    
    def notify(self):
        self.filter_new_ones()
        notifications = []
        for mailbox in self.mails_new:
            for mail in self.mails_new[mailbox]:
                mail_from = mail['From'].replace('<','&lt;').replace('>','&gt;')
                notifications.append((
                    mail['Subject'],
                    formatTooltip([
                        ('From', mail_from),
                        ('Date', mail['Date'])
                    ])
                ))
        self.notifications = notifications
        return (len(notifications) > 0)

    def get_unreads(self):
        self.mails = {}
        self.mail_count = 0
        self.mail_failed = False
        for mailbox in self.mailboxes:
            self.Mail.mailbox_change(mailbox)
            unreads = self.Mail.unread()
            if unreads == None:
                self.mail_failed = True
                continue
            unreads_num = len(unreads)
            if unreads_num > 0:
                self.mail_count += unreads_num
                self.mails[mailbox] = unreads
    
    def remove_duplicates(self):
        removals = []
        for mailbox in self.mails:
            if mailbox == 'Inbox':
                continue
            else:
                for m in self.mails[mailbox]:
                    removals.extend(im for im in self.mails['Inbox'] if im['Date'] ==
                                    m['Date'] and im['Subject'] == m['Subject'])
        removal_count = len(removals)
        if removal_count == len(self.mails['Inbox']):
            del self.mails['Inbox']
        elif removal_count > 0:
            for r in removals:
                self.mails['Inbox'].remove(r)
        self.mail_count -= removal_count
    
    def filter_new_ones(self):
        self.mails_new = self.clone_mails()
        for mailbox in self.mails:
            if mailbox in self.mails_old:
                removals = []
                for mo in self.mails_old[mailbox]:
                    removals.extend(mn for mn in self.mails_new[mailbox] if mn['Date'] ==
                                    mo['Date'] and mn['Subject'] == mo['Subject'])
                for rem in removals:
                    self.mails_new[mailbox].remove(rem)
        self.mails_old = self.clone_mails()
    
    def clone_mails(self):
        clone = {}
        for mailbox in self.mails:
            clone[mailbox] = list(self.mails[mailbox])
        return clone
    
    def open_browser(self):
        url = self.settings['url']
        if url != None:
            xdg_open = "xdg-open '%s'" % bashQuotes(url)
            Shell(xdg_open)
    

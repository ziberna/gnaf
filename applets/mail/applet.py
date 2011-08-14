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

class MailApplet(gnaf.Gnaf):
    settings = {
        'interval':15,
        'icon':{
            'idle':None,
            'updating':None,
            'new':None,
            'error':None
        },
        'username':'',
        'password':'',
        'host':'',
        'port':'auto',
        'ssl':True,
        'mailboxes':[
        '   Inbox'
        ]
    }
    
    def initialize(self):
        sett = self.settings
        self.Mail = Mail(
            sett.get('username'),
            sett.get('password'),
            sett.get('host'),
            sett.get('port'),
            sett.get('ssl')
        )
        return True
    
    def update(self):
        mailboxes = self.settings.get('mailboxes')
        mails = []
        count = 0
      #::Get unread mail from all mailboxes
        mails, count, failed = self.get_unreads()
        if count == 0:
            self.data = ['No new mail...']
            self.tooltip = 'No new mail...'
            return False
      #::Remove duplicate emails from Inbox
        if 'Inbox' in mailboxes:
            i = mailboxes.index('Inbox')
            removals = []
            for mbox in mails:
                if mbox[0] == 'Inbox':
                    continue
                else:
                    for m in mbox[1]:
                        removals.extend(im for im in mails[i][1] if im['Date'] ==
                                        m['Date'] and im['Subject'] == m['Subject'])
            removal_count = len(removals)
            if removal_count == len(mails[i][1]):
                del mails[i]
            elif removal_count > 0:
                for r in removals:
                    mails[i][1].remove(r)
            count -= removal_count
      #::Format mail lists for applet menu
        data = []
        for mbox in mails:
            mlist = []
            for m in mbox[1]:
                m_From = m['From'].replace('<','&lt;').replace('>','&gt;')
                mlist.append((m['Subject'], '<b>From:</b> %s\n<b>Date:</b> %s' %
                            (m_From, m['Date'])))
            data.append((
                '%s (%s)' % (mbox[0], len(mlist)),
                mlist
            ))
      #::Final
        self.data = data
        self.tooltip = '%i new mail(s)!' % count
        self.notification = ('%i new mails(s)!' % count, '\n'.join([mbox[0] for mbox in mails]))
        return (True if not failed else None)

    def get_unreads(self):
        mailboxes = self.settings.get('mailboxes')
        mails = []
        count = 0
        failed = False
        for mailbox in mailboxes:
            self.Mail.mailbox_change(mailbox)
            unreads = self.Mail.unread()
            if unreads == None:
                failed = True
                continue
            unreads_num = len(unreads)
            if unreads_num > 0:
                count += unreads_num
                mails.append([
                    mailbox,
                    unreads
                ])
        return mails, count, failed
    
    def remove_duplicates():
        pass


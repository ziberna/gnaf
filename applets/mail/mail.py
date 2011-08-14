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

import imaplib, email, socket
from getpass import getpass

class Mail:
    conn = None
    user = None
    password = None
    host = None
    port = None
    mailbox = None
    error = None
    
    def __init__(self, user, password, host, port, ssl):
      #::Connect to email host
        try:
            if ssl:
                if port == 'auto':
                    port = 993
                conn = imaplib.IMAP4_SSL(host, port)
            else:
                if port == 'auto':
                    port = 143
                conn = imaplib.IMAP4(host, port)
        except (imaplib.IMAP4.error, socket.error) as err:
            self.error = err
            return
      #::Log in
        if password == '':
            password = getpass('Mail password:')
        try:
            conn.login(user, password)
        except (imaplib.IMAP4.error, socket.error) as err:
            self.error = err
            return
        conn.select(readonly=True)
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.mailbox = 'Inbox'
        self.conn = conn
    
    def __del__(self):
        if self.conn != None:
            self.conn.close()
            self.conn.logout()
    
    def unread(self):
        try:
            typ, data = self.conn.search(None, 'UnSeen')
            mail_list = []
            for num in data[0].split():
                typ, data = self.conn.fetch(num, '(BODY.PEEK[HEADER])')
                e = email.message_from_string(data[0][1])
                mail_list.append(e)
            return mail_list
        except (imaplib.IMAP4.error, socket.error) as err:
            self.error = err
            return None
    
    def mailbox_change(self, mailbox):
        try:
            self.conn.select(mailbox, readonly=True)
            self.mailbox = mailbox
            return True
        except (imaplib.IMAP4.error, socket.error) as err:
            self.error = err
            return None
    
    def mailbox_list(self):
        try:
            return self.conn.list()
        except (imaplib.IMAP4.error, socket.error) as err:
            self.error = err
            return None

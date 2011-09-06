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

import sys
import re
import traceback

from gnaf.lib.istype import isstr
from gnaf.lib.format import formatLR, formatC, timestamp

width = 80

write = sys.stdout.write

def writeln(text):
    if not isstr(text):
        text = repr(text)
    write(text + '\n')

def writeC(text, fill='-'):
    writeln(formatC(text, fill, 1, width))

def writeLR(left, rigth, fill=''):
    writeln(formatLR(left, rigth, fill, 1, width))

def debug():
    text = formatC('DEBUG OUTPUT', '#', 1, width)
    text = re.sub(r'(#+)',r'\033[31m\1\033[0m',text)
    writeln(text)
    traceback.print_exc()
    text = formatC('END DEBUG OUTPUT', '#', 1, width)
    text = re.sub(r'(#+)',r'\033[31m\1\033[0m',text)
    writeln(text)

def logC(text):
    writeln(formatC(text, '-', 1, width))

def logLR(left, right):
    text = formatLR(left, '['+right+']', '', 1, width)
    text = re.sub(r'(DONE|TRUE|NEW|YES)',r'\033[32m\1\033[0m',text)
    text = re.sub(r'(NO|FALSE|OLD)',r'\033[33m\1\033[0m',text)
    text = re.sub(r'(IMPORT ERROR|ERROR)',r'\033[31m\1\033[0m',text)
    text = re.sub(r'(FOUND APPLET|\.\.\.|QUIT)',r'\033[36m\1\033[0m',text)
    writeln(text)

def logTime(subject, status=None):
    subject = '[%s] %s' % (timestamp(), subject)
    if status != None:
        logLR(subject, status)
    else:
        writeln(subject)

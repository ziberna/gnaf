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

def chop(seq, length, start=0):
    l = [seq[:start]] if start > 0 else []
    l.extend([seq[i:i+length] for i in range(start, len(seq), length)])
    return l

def format_L_R(text1, text2, fill='', margin=80, space=0):
    l1 = len(text1) % margin
    l2 = len(text2) % margin
    if l1 + l2 + space <= margin:
        chop2 = chop(text2, margin, l2)
        chop2[0] = ('{:%s>%i}' % (fill, margin-l1)).format(chop2[0])
        text2 = '\n'.join(chop2)
    else:
        text1 = ('{:%s<%i}\n' % (fill, margin)).format(text1)
        text2 = ('{:%s>%i}' % (fill, margin)).format(text2)
    return '%s%s' % (text1, text2)

def format_C(text, fill='', margin=80, space=0):
    l = len(text) + 2 * space
    if l <= margin:
        return ('{:%s^%i}' % (fill, margin)).format(text)
    elif l <= margin * 2:
        lh = int(l/2)
        t1 = ('{:%s>%i}\n' % (fill, margin)).format(text[:lh])
        t2 = ('{:%s<%i}' % (fill, margin)).format(text[lh:])
        return '%s%s' % (t1, t2)
    else:
        lm = l % margin
        chp = chop(text, margin, int(lm/2))
        chp[0] = ('{:%s>%i}' % (fill, margin)).format(chp[0])
        chp[-1] = ('{:%s<%i}' % (fill, margin)).format(chp[-1])
        return '\n'.join(chp)
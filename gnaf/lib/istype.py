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

def istype(var, name): return (type(var).__name__ == name)

def isclassobj(var): return istype(var, 'classobj')

def isclass(var): return (isclassobj(var) or istype(var, 'type'))

def isobj(var): return istype(var, 'object')

def isstr(var): return istype(var, 'str')

def isdict(var): return istype(var, 'dict')

def islist(var): return istype(var, 'list')

def istuple(var): return istype(var, 'tuple')

def isiterable(var): return islist(var) or isdict(var) or istuple(var)

def isindexed(var): return islist(var) or istuple(var)

def isint(var): return istype(var, 'int')

def isfloat(var): return istype(var, 'float')

def isfunc(var): return istype(var, 'function')

def ismethod(var): return istype(var, 'instancemethod')

def iscallable(var): return (isfunc(var) or ismethod(var))

def isbool(var): return istype(var, 'bool')

def isgnaf(var): return isclass(var) and issubclass(var, gnaf.Gnaf)

def name(var): return var.__name__

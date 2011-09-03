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

import time
import thread as threading
import subprocess as sp
from gnaf.lib.istype import isdict, islist
from gnaf.lib.write import debug

def id(object=None):
    t = time.time()
    if object != None:
        object.id = t
    return t

def thread(function, *params):
    threading.start_new(function, params)
    
def timeout(seconds, function, *params):
    time.sleep(seconds)
    function(*params)

def threadTimeout(seconds, function, *params):
    thread(lambda s=seconds, f=function, p=params: timeout(s,f,*p))

def tryExcept(function, *params):
    try:
        value = function(*params)
    except:
        debug()
        value = None
    return value

def tolist(value):
    if not islist(value):
        value = [value]
    return value

def dictmerge(*dicts):
    merge = Dict()
    for dict in dicts:
        for key in dict:
            if isdict(dict[key]) and key in merge and isdict(merge[key]):
                merge[key] = dictmerge(merge[key], dict[key])
            else:
                merge[key] = dict[key]
    return merge

class Dict(dict):
    def __init__(self, default=None):
        self.default = default
    
    def __getitem__(self, key):
        if key not in self:
            return self.default
        else:
            return dict.__getitem__(self, key)

class Shell:
    def __init__(self, command):
        self.command = command
        p = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        self.pid = p.pid
        self.output, self.error = p.communicate()
        self.failed = p.returncode

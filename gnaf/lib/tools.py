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
import re

from gnaf.lib.istype import isdict, islist, isstr
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


class Regex(object):
    alias_regex = []
    ignore_regex = []
    
    def alias(self, str):
        if not isstr(str):
            return str
        for alias in self.alias_regex:
            if alias[0].search(str):
                return alias[0].sub(alias[1], str)
        return str
    
    def ignore(self, str):
        if not isstr(str):
            return False
        for ignore in self.ignore_regex:
            if ignore.search(str):
                return True
        return False
    
    @property
    def alias_patterns(self): return self._alias_patterns
    
    @alias_patterns.setter
    def alias_patterns(self, patterns):
        self.alias_regex = [(re.compile(p), patterns[p]) for p in patterns]
        self._alias_patterns = patterns
    
    @property
    def ignore_patterns(self): return self._ignore_patterns
    
    @ignore_patterns.setter
    def ignore_patterns(self, patterns):
        self.ignore_regex = [re.compile(p) for p in patterns]
        self._ignore_patterns = patterns


class Shell:
    def __init__(self, command):
        self.command = command
        p = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        self.pid = p.pid
        self.output, self.error = p.communicate()
        self.failed = p.returncode

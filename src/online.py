# Copyright (C) 2010  Wil Mahan <wmahan+fatics@gmail.com>
#
# This file is part of FatICS.
#
# FatICS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FatICS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with FatICS.  If not, see <http://www.gnu.org/licenses/>.
#

import trie

#class AmbiguousException(Exception):
#        def __init__(self, matches):
#                self.matches = matches
class Online(object):
    def __init__(self):
        self.online = trie.Trie()

    def add(self, u):
        self.online[u.name.lower()] = u

    def remove(self, u):
        try:
            del self.online[u.name.lower()]
        except KeyError:
            pass

    def is_online(self, name):
        # there's probably a more efficient way
        return self.find_exact(name) is not None

    def find_exact(self, name):
        name = name.lower()
        try:
            u = self.online[name]
        except trie.NeedMore:
            u = None
        except KeyError:
            u = None
        return u

    def find_part(self, prefix):
        assert(not self.is_online(prefix))
        prefix = prefix.lower()
        try:
            ulist = self.online.all_children(prefix)
        except KeyError:
            ulist = []
        return ulist

    def __iter__(self):
        return self.online.itervalues()

    def itervalues(self):
        return self.online.itervalues()

online = Online()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

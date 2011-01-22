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
        # this is redundant, but faster; it's very slow to iterate
        # over the trie
        self.online_names = {}
        self.guest_count = 0
        self.pin_ivar = set()
        #self.shouts_var = set()

    def add(self, u):
        self.online[u.name.lower()] = u
        self.online_names[u.name.lower()] = u
        if u.is_guest:
            self.guest_count += 1

    def remove(self, u):
        if u in self.pin_ivar:
            self.pin_ivar.remove(u)
        #if u in shouts_var:
        #    shouts_var.remove(u)
        try:
            del self.online[u.name.lower()]
            del self.online_names[u.name.lower()]
        except KeyError:
            pass
        else:
            self.guest_count -= int(u.is_guest)

    def is_online(self, name):
        return name.lower() in self.online_names

    def find_exact(self, name):
        name = name.lower()
        try:
            u = self.online_names[name.lower()]
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
        return iter(self.online_names.values())

    def __len__(self):
        return len(self.online_names)

online = Online()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

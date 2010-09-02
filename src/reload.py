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

import twisted.python.rebuild

# don't reload connection because then we can't remove connections from
# the list when logging out

import admin, connection, db, session,  timer, user, login, telnet, timeseal, online, trie
modules = [admin, connection, db, session,  timer, user, login, telnet, timeseal, online, trie]

class Reload(object):
    def reload_all(self, conn):
        for mod in modules:
            try:
                twisted.python.rebuild.rebuild(mod)
            except twisted.python.rebuild.RebuildError:
                conn.write("failed to reload %s\n" % mod.__name__)
            else:
                conn.write("reloaded %s\n" % mod.__name__)
reload = Reload()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

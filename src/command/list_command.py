# -*- coding: utf-8 -*-
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

import list_

from command import *

@ics_command('addlist', 'ww',  admin.Level.user)
class Addlist(Command):
    def run(self, args, conn):
        try:
            ls = list_.lists.get(args[0])
        except KeyError:
            conn.write(_('''\"%s\" does not match any list name.\n''' % args[0]))
        except trie.NeedMore as e:
            conn.write(_('''Ambiguous list \"%s\". Matches: %s\n''') % (args[0], ' '.join([r.name for r in e.matches])))
        else:
            try:
                ls.add(args[1], conn)
            except list_.ListError as e:
                conn.write(e.reason)

@ics_command('showlist', 'o', admin.Level.user)
class Showlist(Command):
    def run(self, args, conn):
        if args[0] is None:
            for c in list_.lists.itervalues():
                conn.write('%s\n' % c.name)
            return

        try:
            ls = list_.lists.get(args[0])
        except KeyError:
            conn.write(_('''\"%s\" does not match any list name.\n''' % args[0]))
        except trie.NeedMore as e:
            conn.write(_('''Ambiguous list \"%s\". Matches: %s\n''') % (args[0], ' '.join([r.name for r in e.matches])))
        else:
            try:
                ls.show(conn)
            except list_.ListError as e:
                conn.write(e.reason)

@ics_command('sublist', 'ww', admin.Level.user)
class Sublist(Command):
    def run(self, args, conn):
        try:
            ls = list_.lists.get(args[0])
        except KeyError:
            conn.write(_('''\"%s\" does not match any list name.\n''' % args[0]))
        except trie.NeedMore as e:
            conn.write(_('''Ambiguous list \"%s\". Matches: %s\n''') % (args[0], ' '.join([r.name for r in e.matches])))
        else:
            try:
                ls.sub(args[1], conn)
            except list_.ListError as e:
                conn.write(e.reason)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

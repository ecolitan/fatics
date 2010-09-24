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

from command import *

@ics_command('observe', 'i', admin.Level.user)
class Observe(Command):
    def run(self, args, conn):
        if args[0] in ['/l', '/b', '/s', '/S', '/w', '/z', '/B', '/L', '/x']:
            conn.write('TODO: observe flag\n')
            return
        g = game.from_name_or_number(args[0], conn)
        if g:
            if g in conn.user.session.observed:
                conn.write(_('You are already observing game %d.\n' % g.number))
            elif conn.user in g.players:
                conn.write(_('You cannot observe yourself.\n'))
            else:
                assert(conn.user not in g.observers)
                g.observe(conn.user)

@ics_command('allobservers', 'o', admin.Level.user)
class Allobservers(Command):
    def run(self, args, conn):
        if args[0] is not None:
            g = game.from_name_or_number(args[0], conn)
            if g:
                if not g.observers:
                    conn.write(_('No one is observing game %d.\n')
                        % g.number)
                else:
                    g.show_observers(conn)
        else:
            for g in game.games.itervalues():
                g.show_observers(conn)

@ics_command('unobserve', 'n', admin.Level.user)
class Unobserve(Command):
    def run(self, args, conn):
        if args[0] is not None:
            g = game.from_name_or_number(args[0], conn)
            if g:
                if g in conn.user.session.observed:
                    g.unobserve(conn.user)
                else:
                    conn.write(_('You are not observing game %d.\n')
                        % g.number)
        else:
            if not conn.user.session.observed:
                conn.write(_('You are not observing any games.\n'))
            else:
                for g in conn.user.session.observed.copy():
                    g.unobserve(conn.user)
                assert(not conn.user.session.observed)

@ics_command('primary', 'n', admin.Level.user)
class Primary(Command):
    def run(self, args, conn):
        if args[0] is None:
            if not conn.user.session.observed:
                conn.write(_('You are not observing any games.\n'))
            else:
                conn.write('TODO: primary no param\n')
        else:
            g = game.from_name_or_number(args[0], conn)
            if g:
                if g in conn.user.session.observed:
                    if g == conn.user.session.observed.primary():
                        conn.write(_('Game %d is already your primary game.\n') %
                            g.number)
                    else:
                        conn.user.session.observed.make_primary(g)
                        conn.write(_('Game %d is now your primary game.\n') %
                            g.number)

                else:
                    conn.write('You are not observing game %d.\n' % conn)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

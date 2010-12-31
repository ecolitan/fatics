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

import examine

from command import *

@ics_command('examine', 'on')
class Examine(Command):
    def run(self, args, conn):
        if conn.user.session.game:
            if conn.user.session.game.gtype == game.EXAMINED:
                conn.write(_("You are already examining a game.\n"))
            else:
                conn.write(_("You are playing a game.\n"))
            return

        if args[0] is None:
            conn.write(_("Starting a game in examine (scratch) mode.\n"))
            examine.ExaminedGame(conn.user)
            return

        if args[0] == 'b':
            conn.write('TODO: EXAMINE SCRATCH BOARD\n')
            return

        u = user.find_by_prefix_for_user(args[0], conn, min_len=2)
        if not u:
            return

        if args[1] is None:
            conn.write('TODO: EXAMINE ADJOURNED GAME\n')
            return

        try:
            num = int(args[1])
            # history game
            h = u.get_history_game(num, conn)
            if h:
                examine.ExaminedGame(conn.user, h)
            return
        except ValueError:
            m = re.match(r'%(\d\d?)', args[1])
            if m:
                num = int(m.group(1))
                conn.write('TODO: EXAMINE JOURNAL GAME\n')
                return

            u2 = user.find_by_prefix_for_user(args[1], conn, min_len=2)
            if not u2:
                return
            conn.write('TODO: EXAMINE ADJOURNED GAME\n')

@ics_command('mexamine', 'w')
class Mexamine(Command):
    def run(self, args, conn):
        g = conn.user.session.game
        if not g or g.gtype != game.EXAMINED:
            conn.write(_("You are not examining a game.\n"))
            return

        u = user.find_by_prefix_for_user(args[0], conn, online_only=True)
        if not u:
            return

        g.mexamine(u, conn)

@ics_command('backward', 'p')
class Backward(Command):
    def run(self, args, conn):
        n = args[0] if args[0] is not None else 1
        g = conn.user.session.game
        if not g or g.gtype != game.EXAMINED:
            conn.write(_("You are not examining a game.\n"))
            return
        g.backward(n, conn)

@ics_command('forward', 'p', admin.Level.user)
class Forward(Command):
    def run(self, args, conn):
        n = args[0] if args[0] is not None else 1
        g = conn.user.session.game
        if not g or g.gtype != game.EXAMINED:
            conn.write(_("You are not examining a game.\n"))
            return
        g.forward(n, conn)

@ics_command('unexamine', '')
class Unexamine(Command):
    def run(self, args, conn):
        g = conn.user.session.game
        if not g or g.gtype != game.EXAMINED:
            conn.write(_("You are not examining a game.\n"))
            return
        g.leave(conn.user)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

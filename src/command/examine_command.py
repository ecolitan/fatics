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

@ics_command('examine', 'on', admin.Level.user)
class Examine(Command):
    def run(self, args, conn):
        if len(conn.user.session.games) != 0:
            if conn.user.session.games.current().gtype == game.EXAMINED:
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

        u = user.find.by_prefix_for_user(args[0], conn, min_len=2)
        if not u:
            return

        if args[1] is None:
            conn.write('TODO: EXAMINE ADJOURNED GAME\n')
            return

        try:
            num = int(args[1])
            if num < 0:
                conn.write('TODO: EXAMINE PREVIOUS GAME\n')
            else:
                # history game
                h = u.get_history_game(num, conn)
                examine.ExaminedGame(conn.user, h)
            return
        except ValueError:
            pass

        m = re.match(r'%(\d\d?)', args[1])
        if m:
            num = int(m.group(1))
            conn.write('TODO: EXAMINE JOURNAL GAME\n')
            return

@ics_command('backward', 'p', admin.Level.user)
class Backward(Command):
    def run(self, args, conn):
        n = args[0] if args[0] is not None else 1
        if not conn.user.session.games or conn.user.session.games.current().gtype != game.EXAMINED:
            conn.write(_("You are not examining a game.\n"))
            return
        g = conn.user.session.games.current()
        g.backward(n, conn)

@ics_command('forward', 'p', admin.Level.user)
class Forward(Command):
    def run(self, args, conn):
        n = args[0] if args[0] is not None else 1
        if not conn.user.session.games or conn.user.session.games.current().gtype != game.EXAMINED:
            conn.write(_("You are not examining a game.\n"))
            return
        g = conn.user.session.games.current()
        g.forward(n, conn)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

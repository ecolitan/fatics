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

class GameCommand(Command):
    pass

@ics_command('abort', 'n', admin.Level.user)
class Abort(GameCommand):
    def run(self, args, conn):
        if not conn.user.session.games or conn.user.session.games.primary().gtype != game.PLAYED:
            conn.write(_("You are not playing a game.\n"))
            return
        if len(conn.user.session.games) > 1:
            conn.write(_('Please use "simabort" for simuls.\n'))
            return
        g = conn.user.session.games.primary()
        if g.variant.pos.ply < 2:
            g.result('Game aborted on move 1 by %s' % conn.user.name, '*')
        else:
            offer.Abort(g, conn.user)

@ics_command('draw', 'o', admin.Level.user)
class Draw(Command):
    def run(self, args, conn):
        if args[0] is None:
            if len(conn.user.session.games) == 0:
                conn.write(_("You are not playing a game.\n"))
                return
            g = conn.user.session.games.primary()
            offer.Draw(g, conn.user)
        else:
            conn.write('TODO: DRAW PARAM\n')

@ics_command('resign', 'o', admin.Level.user)
class Resign(Command):
    def run(self, args, conn):
        if args[0] is not None:
            conn.write('TODO: RESIGN PLAYER\n')
            return
        if len(conn.user.session.games) == 0:
            conn.write(_("You are not playing a game.\n"))
            return
        g = conn.user.session.games.primary()
        g.resign(conn.user)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent


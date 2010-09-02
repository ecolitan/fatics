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

class GameParam(object):
    """ A mixin to find a game from a command argument, currently being
    played, examined, or observed, prioritized in that order. """
    def _game_param(self, param, conn):
        if param is not None:
            g = game.from_name_or_number(param, conn)
        else:
            if len(conn.user.session.games) > 0:
                g = conn.user.session.games.primary()
            elif conn.user.session.observed:
                g = list(conn.user.session.observed)[0]
            else:
                conn.write(_("You are not playing, examining, or observing a game.\n"))
                g = None
        return g

@ics_command('eco', 'oo', admin.Level.user)
class Eco(Command, GameParam):
    eco_pat = re.compile(r'[a-z][0-9][0-9][a-z]?')
    nic_pat = re.compile(r'[a-z][a-z]\.[0-9][0-9]')
    def run(self, args, conn):
        g = None
        if args[1] is not None:
            assert(args[0] is not None)
            rows = []
            if args[0] == 'e':
                if not self.eco_pat.match(args[1]):
                    conn.write(_("You haven't specified a valid ECO code.\n"))
                else:
                    rows = db.look_up_eco(args[1])
            elif args[0] == 'n':
                if not self.nic_pat.match(args[1]):
                    conn.write(_("You haven't specified a valid NIC code.\n"))
                else:
                    rows = db.look_up_nic(args[1])
            else:
                raise BadCommandError()
            for row in rows:
                if row['eco'] is None:
                    row['eco'] = 'A00'
                if row['nic'] is None:
                    row['nic'] = '-----'
                if row['long_'] is None:
                    row['long_'] = 'Unknown / not matched'
                assert(row['fen'] is not None)
                conn.write('\n')
                conn.write('  ECO: %s\n' % row['eco'])
                conn.write('  NIC: %s\n' % row['nic'])
                conn.write(' LONG: %s\n' % row['long_'])
                conn.write('  FEN: %s\n' % row['fen'])
        else:
            g = self._game_param(args[0], conn)

        if g:
            (ply, eco, long) = g.get_eco()
            (nicply, nic) = g.get_nic()
            conn.write(_('Eco for game %d (%s vs. %s):\n') % (g.number, g.white.name, g.black.name))
            conn.write(_(' ECO[%3d]: %s\n') % (ply, eco))
            conn.write(_(' NIC[%3d]: %s\n') % (nicply, nic))
            conn.write(_('LONG[%3d]: %s\n') % (ply, long))

@ics_command('moves', 'n', admin.Level.user)
class Moves(Command, GameParam):
    def run(self, args, conn):
        g = self._game_param(args[0], conn)
        if g:
            g.write_moves(conn)

@ics_command('refresh', 'n', admin.Level.user)
class Refresh(Command, GameParam):
    def run(self, args, conn):
        g = self._game_param(args[0], conn)
        if g:
            conn.user.send_board(g)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent


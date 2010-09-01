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

import speed_variant
from game import Game
from game_constants import *
from variant.variant_factory import variant_factory

class ExaminedGame(Game):
    def __init__(self, user, hist_game=None):
        super(ExaminedGame, self).__init__()
        self.gtype = EXAMINED
        self.white_time = 0
        self.black_time = 0
        self.inc = 0
        self.players = [user]
        user.session.games.add(self, '[examined]')
        self.speed_variant = speed_variant.from_names('untimed', 'chess')
        self.variant = variant_factory.get(self.speed_variant.variant.name,
            self)
        if hist_game is None:
            self.moves = []
            self.white_name = 'White'
            self.black_name = 'Black'
        else:
            self.moves = hist_game['movetext'].split(' ')
            self.white_name = hist_game['white_name']
            self.black_name = hist_game['black_name']
        self.send_boards()

    #def parse_move(self, s, t, conn):
    #    ret = super(ExaminedGame, self).parse_move(self, s, t, conn)

    def forward(self, n, conn):
        assert(self.variant.pos.ply <= len(self.moves))
        if self.variant.pos.ply >= len(self.moves):
            conn.write(_("You're at the end of the game.\n"))
            return
        for p in self.players + list(self.observers):
            p.write(N_('Game %d: %s goes forward %d move(s)\n') % (self.number, conn.user.name, n)) # XXX ngettext
        mv = self.variant.pos.move_from_san(self.moves[self.variant.pos.ply])
        mv.time = 0.0
        self.variant.do_move(mv)
        self.send_boards()

    def _check_result(self):
        if self.variant.pos.is_checkmate:
            if self.variant.get_turn() == WHITE:
                self.result('%s checkmated' % self.white_name, '0-1')
            else:
                self.result('%s checkmated' % self.black_name, '1-0')
        elif self.variant.pos.is_stalemate:
            self.result('Game drawn by stalemate', '1/2-1/2')
        elif self.variant.pos.is_draw_nomaterial:
            self.result('Game drawn because neither player has mating material', '1/2-1/2')

    def next_move(self, mv, t, conn):
        self.moves = self.moves[0:self.variant.pos.ply]
        self.moves.append(mv.to_san())
        #self.variant.pos.get_last_move().time = 0.0
        assert(self.variant.pos.get_last_move() == mv)
        mv.time = 0.0
        super(ExaminedGame, self).next_move(mv, t, conn)
        for p in self.players + list(self.observers):
            p.write(N_('Game %d: %s moves: %s\n') % (self.number, conn.user.name, mv.to_san()))
        if self.variant.pos.is_checkmate:
            if self.variant.get_turn() == WHITE:
                self.result('White checkmated', '0-1')
            else:
                self.result('Black checkmated', '1-0')
        elif self.variant.pos.is_stalemate:
            self.result('Game drawn by stalemate', '1/2-1/2')
        elif self.variant.pos.is_draw_nomaterial:
            self.result('Game drawn because neither player has mating material', '1/2-1/2')

    def leave(self, user):
        # user may be offline if he or she disconnected
        self.players.remove(user)
        if user.is_online:
            user.write(N_('You are no longer examining game %d.\n') % self.number)
        for p in self.players + list(self.observers):
            p.write(N_('%s has stopped examining game %d.\n') % (user.name, self.number))
        if not self.players:
            for p in self.observers:
                p.write(N_('Game %d (which you were observing) has no examiners.\n') % self.number)
            self.free()

    def result(self, msg, result_code):
        for p in self.players + list(self.observers):
            p.write(N_('Game %d: %s %s\n') % (self.number, msg, result_code))

    def free(self):
        super(ExaminedGame, self).free()
        for p in self.players:
            p.session.games.free('[examined]')

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

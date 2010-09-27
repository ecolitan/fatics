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

import time

import speed_variant
from game import Game
from game_constants import *
from variant.variant_factory import variant_factory

class ExaminedGame(Game):
    def __init__(self, user, hist_game=None):
        self.gtype = EXAMINED
        self.players = [user]
        super(ExaminedGame, self).__init__()

        self.white_time = 0
        self.black_time = 0
        self.inc = 0
        self.rated_str = 'unrated'
        assert(user.session.game is None)
        user.session.game = self
        self.start_time = time.time()
        if hist_game is None:
            self.speed_variant = speed_variant.from_names('untimed', 'chess')
            self.variant = variant_factory.get(self.speed_variant.variant.name,
                self)
            self.moves = []
            self.white_name = 'White'
            self.black_name = 'Black'
            self.result_code = None
        else:
            self.idn = hist_game['idn']
            variant_name = speed_variant.variant_abbrevs[hist_game['flags'][1]].name
            # XXX use the speed from history
            self.speed_variant = speed_variant.from_names('untimed',
                variant_name)
            self.variant = variant_factory.get(self.speed_variant.variant.name,
                self)
            self.moves = hist_game['movetext'].split(' ')
            self.white_name = hist_game['white_name']
            self.black_name = hist_game['black_name']
            self.result_code = hist_game['result']
            self.result_reason = hist_game['result_reason']
        self.send_boards()

    def forward(self, n, conn):
        assert(self.variant.pos.ply <= len(self.moves))
        if self.variant.pos.ply >= len(self.moves):
            conn.write(_("You're at the end of the game.\n"))
            return
        for p in self.players + list(self.observers):
            p.nwrite_('Game %d: %s goes forward %d move.\n',
                'Game %d: %s goes forward %d moves.\n', n,
                (self.number, conn.user.name, n))
        for i in range(0, n):
            mv = self.variant.pos.move_from_san(self.moves[self.variant.pos.ply])
            mv.time = 0.0
            self.variant.do_move(mv)
            if self.variant.pos.ply >= len(self.moves):
                # end of the game
                break
        self.send_boards()
        #self._check_result()
        # Trust the stored result, rather than using mates we detected,
        # ourselves, since we can't compute things like resignation and
        # agreed draws.
        if self.variant.pos.ply >= len(self.moves):
            assert(self.result_code)
            self.result(self._result_msg(self.result_reason, self.result_code),
                self.result_code)

    def _result_msg(self, reason, result_code):
        """ Convert an abbreviation for a result (like "Res") to a reason
        ("White resigns") """
        msg = None
        if result_code == '1-0':
            if reason == 'Res':
                msg = '%s resigns' % self.black_name
            elif reason == 'Mat':
                msg = '%s checkmated' % self.black_name
            elif reason == 'Dis':
                msg = '%s forfeits by disconnection' % self.black_name
        elif result_code == '0-1':
            if reason == 'Res':
                msg = '%s resigns' % self.white_name
            elif reason == 'Mat':
                msg = '%s checkmated' % self.white_name
            elif reason == 'Dis':
                msg = '%s forfeits by disconnection' % self.white_name
        elif result_code == '1/2-1/2':
            if reason == 'Agr':
                msg = 'Game drawn by agreement'
            elif reason == 'Sta':
                msg = 'Game drawn by stalemate'
            elif reason == 'Rep':
                msg = 'Game drawn by repetition'
        elif result_code == 'Adj':
            # TODO
            pass

        if not msg:
            raise RuntimeError('unable to get result message (%s//%s)' %
                (reason, result_code))
        return msg

    def backward(self, n, conn):
        assert(self.variant.pos.ply >= 0)
        if self.variant.pos.ply <= 0:
            conn.write(_("You're at the beginning of the game.\n"))
            return
        for p in self.players + list(self.observers):
            p.nwrite_('Game %d: %s backs up %d move.\n',
                'Game %d: %s backs up %d moves.\n', n,
                (self.number, conn.user.name, n))
        self.variant.undo_move()
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

    def next_move(self, mv, conn):
        self.moves = self.moves[0:self.variant.pos.ply]
        self.moves.append(mv.to_san())
        #self.variant.pos.get_last_move().time = 0.0
        assert(self.variant.pos.get_last_move() == mv)
        mv.time = 0.0
        super(ExaminedGame, self).next_move(mv, conn)
        for p in self.players + list(self.observers):
            p.write_('Game %d: %s moves: %s\n', (self.number, conn.user.name, mv.to_san()))
        self._check_result()

    def leave(self, user):
        self.players.remove(user)
        assert(user.session.game == self)
        user.session.game = None
        # user may be offline if he or she disconnected unexpectedly
        if user.is_online:
            user.write_('You are no longer examining game %d.\n', self.number)
        for p in self.players + list(self.observers):
            p.write_('%s has stopped examining game %d.\n', (user.name, self.number))
        if not self.players:
            for p in self.observers:
                p.write_('Game %d (which you were observing) has no examiners.\n', (self.number,))
            self.free()

    def result(self, msg, result_code):
        for p in self.players + list(self.observers):
            p.write_('Game %d: %s %s\n', (self.number, msg, result_code))

    def free(self):
        super(ExaminedGame, self).free()
        for p in self.players:
            assert(user.session.game == self)
            p.session.game = None

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

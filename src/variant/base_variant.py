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

import time_format

from game_constants import *

class BaseVariant(object):
    """ Methods common to all variants. """
    def to_style1(self, user):
        """ A human-readable board. """
        if self.game.gtype == PLAYED and user == self.game.black:
            side = BLACK
        else:
            side = WHITE
        if user.vars['flip']:
            side = opp(side)

        s = []
        s.append('\nGame %d: ' % self.game.number)
        s.append(self.game.info_str + '\n')

        # unlike original FICS, we display user titles here; why not?
        #conn.write(_('Game %(num)d (%(wname)s vs. %(bname)s)\n\n') % {
        #    'num': self.game.number, wname: self.game.white.get_display_name(),
        #    'bname': self.game.black.get_display_name()})

        full_moves = self.pos.ply // 2 + 1

        if self.name in ['crazyhouse', 'bughouse']:
            (holding_white, holding_black) = self.pos.get_holding_str()
            if side == WHITE:
                s.append('Black holding: [%s]\n' % holding_black)
            else:
                s.append('White holding: [%s]\n' % holding_white)
        s.append('\n       ---------------------------------\n')
        for r in range(0, 8):
            rank = 8 - r if side == WHITE else r + 1
            s.append('    %d  |' % rank)
            for f in range(0,  8):
                file_ = f + 1 if side == WHITE else 8 - f
                piece_char = self.pos.board[0x10 * (rank - 1) + file_ - 1]
                if piece_char == '-':
                    piece_char = ' '
                elif piece_char.islower():
                    piece_char = '*' + piece_char
                s.append(' %-2s|' % piece_char)

            if r == 0:
                s.append('     Move # : %d (%s)' %
                    (full_moves, 'White' if self.pos.wtm else 'Black'))
            elif r == 1:
                last_mv = self.pos.get_last_move()
                if last_mv is not None:
                    last_move_time_str = time_format.hms(last_mv.time, user)
                    side_str = 'Black' if self.pos.wtm else 'White'
                    s.append("     %s Moves : '%-7s (%s)'" % (side_str,
                        last_mv.to_san(), last_move_time_str))
            elif r == 3:
                if self.game.gtype == EXAMINED:
                    black_time = 0
                else:
                    black_time = self.game.clock.get_black_time()
                s.append('     Black Clock : %s' % time_format.hms(black_time, user))
            elif r == 4:
                if self.game.gtype == EXAMINED:
                    white_time = 0
                else:
                    white_time = self.game.clock.get_white_time()
                s.append('     White Clock : %s' % time_format.hms(white_time, user))
            elif r == 5:
                s.append('     Black Strength : %d' % self.pos.material[0])
            elif r == 6:
                s.append('     White Strength : %d' % self.pos.material[1])

            s.append('\n')
            if r < 7:
                s.append('       |---+---+---+---+---+---+---+---|\n')

        s.append('       ---------------------------------\n')
        if side == WHITE:
            s.append('         a   b   c   d   e   f   g   h\n')
        else:
            s.append('         h   g   f   e   d   c   b   a\n')
        if self.name in ['crazyhouse', 'bughouse']:
            if side == WHITE:
                s.append('White holding: [%s]\n' % holding_white)
            else:
                s.append('Black holding: [%s]\n' % holding_black)
        s.append('\n')
        return ''.join(s)

    def to_style12(self, user):
        """ returns a style12 string for a given user """
        # <12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 473 GuestPPMD GuestCWVQ -1 1 0 39 39 60000 60000 1 none (0:00.000) none 1 0 0
        board_str = ''
        for r in range(7, -1, -1):
            board_str += ' '
            for f in range(8):
                board_str += self.pos.board[0x10 * r + f]
        side_str = 'W' if self.pos.wtm else 'B'
        ep = -1 if not self.pos.ep else file(self.pos.ep)
        w_oo = int(self.pos.check_castle_flags(True, True))
        w_ooo = int(self.pos.check_castle_flags(True, False))
        b_oo = int(self.pos.check_castle_flags(False, True))
        b_ooo = int(self.pos.check_castle_flags(False, False))
        if self.game.gtype == EXAMINED:
            flip = 0
            if user in self.game.players:
                relation = 2
            elif user in self.game.observers:
                relation = -2
            else:
                relation = -3
            white_clock = 0
            black_clock = 0
            white_name = list(self.game.players)[0].name
            black_name = list(self.game.players)[0].name
            clock_is_ticking = 0
        elif self.game.gtype == PLAYED:
            if self.game.white == user:
                relation = 1 if self.pos.wtm else -1
                flip = 0
            elif self.game.black == user:
                relation = 1 if not self.pos.wtm else -1
                flip = 1
            elif user in self.game.observers:
                relation = 0
                flip = 0
            else:
                relation = -3
                flip = 0
            if user.session.ivars['ms']:
                white_clock = int(round(1000 * self.game.clock.get_white_time()))
                black_clock = int(round(1000 * self.game.clock.get_black_time()))
            else:
                white_clock = int(round(self.game.clock.get_white_time()))
                black_clock = int(round(self.game.clock.get_black_time()))
            white_name = self.game.white.name
            black_name = self.game.black.name
            clock_is_ticking = int(self.game.clock.is_ticking)
        else:
            assert(False)
        full_moves = self.pos.ply // 2 + 1
        last_mv = self.pos.get_last_move()
        if last_mv is None:
            last_move_time_str = time_format.hms(0.0, user)
            last_move_san = 'none'
            last_move_verbose = 'none'
            last_move_lag = 0
        else:
            assert(last_mv.time is not None)
            last_move_time_str = time_format.hms(last_mv.time, user)
            last_move_san = last_mv.to_san()
            last_move_verbose = last_mv.to_verbose_alg()
            last_move_lag = last_mv.lag

        # board_str begins with a space
        s = '\n\n<12>%s %s %d %d %d %d %d %d %d %s %s %d %d %d %d %d %d %d %d %s (%s) %s %d %d %d\n' % (
            board_str, side_str, ep, w_oo, w_ooo, b_oo, b_ooo,
            self.pos.fifty_count, self.game.number, white_name,
            black_name, relation, self.game.white_time,
            self.game.inc, self.pos.material[1], self.pos.material[0],
            white_clock, black_clock, full_moves, last_move_verbose,
            last_move_time_str, last_move_san, flip,
            clock_is_ticking, last_move_lag)

        if self.name in ['crazyhouse', 'bughouse']:
            # print additional <b1> lines
            # print an extra line for captures
            if last_mv and last_mv.is_capture:
                if last_mv.undo.holding_pc.isupper():
                    s = self.get_b1('W%s' % last_mv.undo.holding_pc) + s
                else:
                    s = self.get_b1('B%s' % last_mv.undo.holding_pc.upper()) + s

            s += self.get_b1()

        return s

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

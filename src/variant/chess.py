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

"""This implements routines for normal chess.  (I avoid the term
standard since that is used to describe the game speed on FICS.)
Maybe normal chess technically not a variant, but organizationally
I didn't want to privilege it over variants, so it is here."""

import re
import copy
import random
from array import array

from game_constants import *
from speed_variant import IllegalMoveError
from variant.base_variant import BaseVariant
"""
0x88 board representation; pieces are represented as ASCII,
the same as FEN. A blank square is '-'.
"""

class BadFenError(Exception):
    def __init__(self, reason=None):
        self.reason = reason

piece_moves = {
    'n': [-0x21, -0x1f, -0xe, -0x12, 0x12, 0xe, 0x1f, 0x21],
    'b': [-0x11, -0xf, 0xf, 0x11],
    'r': [-0x10, -1, 1, 0x10],
    'q': [-0x11, -0xf, 0xf, 0x11, -0x10, -1, 1, 0x10],
    'k': [-0x11, -0xf, 0xf, 0x11, -0x10, -1, 1, 0x10]
}
direction_table = array('i', [0 for i in range(0, 0x100)])
def dir(fr, to):
    """Returns the direction a queen needs to go to get from TO to FR,
    or 0 if it's not possible."""
    return direction_table[to - fr + 0x7f]

sliding_pieces = frozenset(['b', 'r', 'q', 'B', 'R', 'Q'])

piece_material = {
    '-': 0,
    'p': 1,
    'n': 3,
    'b': 3,
    'r': 5,
    'q': 9,
    'k': 0
}

def to_castle_flags(w_oo, w_ooo, b_oo, b_ooo):
    return (w_oo << 3) + (w_ooo << 2) + (b_oo << 1) + b_ooo

castle_mask = array('i', [0xf for i in range(0x80)])
castle_mask[A8] = to_castle_flags(True, True, True, False)
castle_mask[E8] = to_castle_flags(True, True, False, False)
castle_mask[H8] = to_castle_flags(True, True, False, True)
castle_mask[A1] = to_castle_flags(True, False, True, True)
castle_mask[E1] = to_castle_flags(False, False, True, True)
castle_mask[H1] = to_castle_flags(False, True, True, True)

def str_to_sq(s):
    return 'abcdefgh'.index(s[0]) + 0x10 * '12345678'.index(s[1])

def sq_to_str(sq):
    return 'abcdefgh'[file(sq)] + '12345678'[rank(sq)]

def piece_is_white(pc):
    assert(len(pc) == 1)
    assert(pc in 'pnbrqkPNBRQK')
    return pc.isupper()

class Zobrist(object):
    """Zobrist keys for low-overhead repetition detection"""
    _piece_index = {
        'p': 0, 'n': 1, 'b': 2, 'r': 3, 'q': 4, 'k': 5,
        'P': 6, 'N': 7, 'B': 8, 'R': 9, 'Q': 10, 'K': 11
    }

    # Note: using 64-bit hashes, the expected number of positions
    # before a collision is 2^32.  Given that a collision has to
    # occur within one game to be meaningful, and games are no
    # longer than 5949 moves, the chance of any affect should be
    # negligible.
    def __init__(self):
        random.seed(2010)
        self.side_hash = random.getrandbits(64)
        self._piece = self._rand_list(0x10 * 0x80)
        self._ep = self._rand_list(8)
        self._castle = self._rand_list(0x10)
        random.seed()

    def piece_hash(self, sq, pc):
        assert((0xf << 7) & sq == 0)
        assert(valid_sq(sq))
        #print 'hashing %s at %s' % (pc, sq_to_str(sq))
        return self._piece[(self._piece_index[pc] << 7) | sq]

    def ep_hash(self, ep):
        return self._ep[file(ep)]

    def castle_hash(self, flags):
        assert(flags & ~0xf == 0)
        return self._castle[flags]

    def _rand_list(self, len):
        return [random.getrandbits(64) for i in xrange(0, len)]

zobrist = Zobrist()

class Move(object):
    def __init__(self, pos, fr, to, prom=None, is_oo=False,
            is_ooo=False, is_ep=False, new_ep=None):
        self.pos = pos
        self.fr = fr
        self.to = to
        self.pc = self.pos.board[self.fr]
        self.prom = prom
        self.is_oo = is_oo
        self.is_ooo = is_ooo
        self.capture = pos.board[to]
        self.is_capture = self.capture != '-'
        self.is_ep = is_ep
        self.new_ep = new_ep
        self.time = None
        self._san = None
        self._verbose_alg = None
        self.lag = 0

        # if a promotion piece is not given, assume queen
        if not self.prom:
            if self.pc == 'p' and rank(to) == 0:
                self.prom = 'q'
            elif self.pc == 'P' and rank(to) == 7:
                self.prom = 'Q'

    def __str__(self):
        s = '%s%s' % (sq_to_str(self.fr), sq_to_str(self.to))
        if self.prom:
            s += '=%s' % self.prom
        return s

    def check_pseudo_legal(self):
        """Tests if a move is pseudo-legal, that is, legal ignoring the
        fact that the king cannot be left in check. Also sets en passant
        flags for this move. This is used for long algebraic moves,
        but not san, which does these checks implicitly."""

        if self.pc == '-' or piece_is_white(self.pc) != self.pos.wtm:
            raise IllegalMoveError('can only move own pieces')

        if self.is_capture and piece_is_white(self.capture) == self.pos.wtm:
            raise IllegalMoveError('cannot capture own piece')

        if self.is_oo or self.is_ooo:
            return

        diff = self.to - self.fr
        if self.pc == 'p':
            if self.pos.board[self.to] == '-':
                if diff == -0x10:
                    pass
                elif diff == -0x20 and rank(self.fr) == 6:
                    self.new_ep = self.fr - 0x10
                    if self.pos.board[self.new_ep] != '-':
                        raise IllegalMoveError('bad en passant')
                elif diff in [-0x11, -0xf] and self.to == self.pos.ep:
                    self.is_ep = True
                else:
                    raise IllegalMoveError('bad pawn push')
            else:
                if not diff in [-0x11, -0xf]:
                    raise IllegalMoveError('bad pawn capture')
        elif self.pc == 'P':
            if self.pos.board[self.to] == '-':
                if diff == 0x10:
                    pass
                elif diff == 0x20 and rank(self.fr) == 1:
                    self.new_ep = self.fr + 0x10
                    if self.pos.board[self.new_ep] != '-':
                        raise IllegalMoveError('bad en passant')
                elif diff in [0x11, 0xf] and self.to == self.pos.ep:
                    self.is_ep = True
                else:
                    raise IllegalMoveError('bad pawn push')
            else:
                if not diff in [0x11, 0xf]:
                    raise IllegalMoveError('bad pawn capture')
        else:
            if self.pc in sliding_pieces:
                d = dir(self.fr, self.to)
                if d == 0 or not d in piece_moves[self.pc.lower()]:
                    raise IllegalMoveError('piece cannot make that move')
                # now check if there are any pieces in the way
                cur_sq = self.fr + d
                while cur_sq != self.to:
                    assert(valid_sq(cur_sq))
                    if self.pos.board[cur_sq] != '-':
                        raise IllegalMoveError('sliding piece blocked')
                    cur_sq += d
            else:
                if not diff in piece_moves[self.pc.lower()]:
                    raise IllegalMoveError('piece cannot make that move')

    def check_legal(self):
        """Test whether a move leaves the king in check, or if
        castling if blocked or otherwise unavailable.  These
        tests are grouped together because they are common
        to all move formats."""
        if self.is_oo:
            if (self.pos.in_check
                    or not self.pos.check_castle_flags(self.pos.wtm, True)
                    or self.pos.board[self.fr + 1] != '-'
                    or self.pos.under_attack(self.fr + 1, not self.pos.wtm)
                    or self.pos.under_attack(self.to, not self.pos.wtm)):
                raise IllegalMoveError('illegal castling')
            return

        if self.is_ooo:
            if (self.pos.in_check
                    or not self.pos.check_castle_flags(self.pos.wtm, False)
                    or self.pos.board[self.fr - 1] != '-'
                    or self.pos.under_attack(self.fr - 1, not self.pos.wtm)
                    or self.pos.under_attack(self.to, not self.pos.wtm)):
                raise IllegalMoveError('illegal castling')
            return

        self.pos.make_move(self)
        try:
            if self.pos.under_attack(self.pos.king_pos[not self.pos.wtm],
                    self.pos.wtm):
                raise IllegalMoveError('leaves king in check')
        finally:
            self.pos.undo_move(self)

    def to_san(self):
        if self._san is None:
            self._san = self._to_san()
        return self._san

    def add_san_decorator(self):
        assert(self._san is not None)
        if self.pos.is_checkmate:
            self._san += '#'
        elif self.pos.in_check:
            self._san += '+'

    def _to_san(self):
        if self.is_oo:
            san = 'O-O'
        elif self.is_ooo:
            san = 'O-O-O'
        elif self.pc in ['P', 'p']:
            san = ''
            if self.is_capture or self.is_ep:
                san += 'abcdefgh'[file(self.fr)] + 'x'
            san += sq_to_str(self.to)
            if self.prom:
                san += '=' + self.prom.upper()
        else:
            assert(not self.is_ep)
            san = self.pc.upper()
            ambigs = self.pos.get_from_sqs(self.pc, self.to)
            assert(len(ambigs) >= 1)
            if len(ambigs) > 1:
                r = rank(self.fr)
                f = file(self.fr)
                # try disambiguating with file
                if len(filter(lambda sq: file(sq) == f, ambigs)) == 1:
                    san += 'abcdefgh'[f]
                elif len(filter(lambda sq: rank(sq) == r, ambigs)) == 1:
                    san += '12345678'[r]
                else:
                    san += sq_to_str(self.fr)
            if self.is_capture:
                san += 'x'
            san += sq_to_str(self.to)
        return san

    def to_verbose_alg(self):
        if self._verbose_alg is None:
            self._verbose_alg = self._to_verbose_alg()
        return self._verbose_alg

    def _to_verbose_alg(self):
        """convert to the verbose notation used in style12"""
        if self.is_oo:
            # why fics, why?
            ret = 'o-o'
        elif self.is_ooo:
            ret = 'o-o-o'
        else:
            ret = self.pc.upper() + '/'
            ret += sq_to_str(self.fr)
            ret += '-'
            ret += sq_to_str(self.to)
            if self.prom:
                ret += '=' + self.prom.upper()
        return ret

    def to_smith(self):
        """ Convert to Smith notation. """
        ret = []
        ret.append(sq_to_str(self.fr))
        ret.append(sq_to_str(self.to))
        if self.is_capture:
            ret.append(self.capture.lower())
        if self.prom:
            ret.append(self.prom.upper())
        if self.is_oo:
            ret.append('c')
        elif self.is_ooo:
            ret.append('C')
        elif self.is_ep:
            ret.append('E')
        return ''.join(ret)

    def is_legal(self):
        try:
            self.check_legal()
        except IllegalMoveError:
            return False
        else:
            return True

class Undo(object):
    """information needed to undo a move"""
    pass

class PositionHistory(object):
    """keeps past of past positions for repetition detection"""
    def __init__(self):
        self.hashes = [None] * 40
        self.moves = [None] * 40

    def set_hash(self, ply, hash):
        if ply >= len(self.hashes):
            self.hashes.extend([None] * (ply - len(self.hashes) + 1))
        self.hashes[ply] = hash

    def set_move(self, ply, mv):
        if ply >= len(self.moves):
            self.moves.extend([None] * (ply - len(self.moves) + 1))
        self.moves[ply] = mv

    def get_hash(self, ply):
        return self.hashes[ply]

    def get_move(self, ply):
        return self.moves[ply]

class Position(object):
    def __init__(self, fen):
        self.board = array('c', 0x80 * ['-'])
        self.castle_flags = 0
        self.king_pos = [None, None]
        self.history = PositionHistory()
        self.set_pos(fen)

    set_pos_re = re.compile(r'''^([1-8rnbqkpRNBQKP/]+) ([wb]) ([kqKQ]+|-) ([a-h][36]|-) (\d+) (\d+)$''')
    def set_pos(self, fen, detect_check=True):
        """Set the position from Forsyth-Fdwards notation.  The format
        is intentionally interpreted strictly; better to give the user an
        error than take in bad data."""
        try:
            # rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
            m = self.set_pos_re.match(fen)
            if not m:
                raise BadFenError('does not look like FEN')
            (pos, side, castle_flags, ep, fifty_count, full_moves) = [
                m.group(i) for i in range(1, 7)]

            ranks = pos.split('/')
            ranks.reverse()
            self.hash = 0
            self.material = [0, 0]
            for (r, rank_str) in enumerate(ranks):
                sq = 0x10 * r
                for c in rank_str:
                    d = '12345678'.find(c)
                    if d >= 0:
                        sq += d + 1
                    else:
                        assert(valid_sq(sq))
                        self.board[sq] = c
                        self.hash ^= zobrist.piece_hash(sq, c)
                        self.material[piece_is_white(c)] += \
                            piece_material[c.lower()]
                        if c == 'k':
                            if self.king_pos[0] != None:
                                # multiple kings
                                raise BadFenError()
                            self.king_pos[0] = sq
                        elif c == 'K':
                            if self.king_pos[1] != None:
                                # multiple kings
                                raise BadFenError()
                            self.king_pos[1] = sq
                        elif c.lower() == 'p':
                            if rank(sq) in [0, 7]:
                                # pawn on 1st or 8th rank
                                raise BadFenError()
                        sq += 1
                if sq & 0xf != 8:
                    # wrong row length
                    raise BadFenError()

            if None in self.king_pos:
                # missing king
                raise BadFenError()

            self.wtm = side == 'w'
            if self.wtm:
                self.hash ^= zobrist.side_hash

            if castle_flags == '-':
                self.castle_flags = 0
            else:
                (w_oo, w_ooo, b_oo, b_ooo) = (False, False, False, False)
                for c in castle_flags:
                    if c == 'K':
                        if self.board[E1] != 'K' or self.board[H1] != 'R':
                            raise BadFenError()
                        if w_oo:
                            raise BadFenError()
                        w_oo = True
                    elif c == 'Q':
                        if self.board[E1] != 'K' or self.board[A1] != 'R':
                            raise BadFenError()
                        if w_ooo:
                            raise BadFenError()
                        w_ooo = True
                    elif c == 'k':
                        if self.board[E8] != 'k' or self.board[H8] != 'r':
                            raise BadFenError()
                        if b_oo:
                            raise BadFenError()
                        b_oo = True
                    elif c == 'q':
                        if self.board[E8] != 'k' or self.board[A8] != 'r':
                            raise BadFenError()
                        if b_ooo:
                            raise BadFenError()
                        b_ooo = True
                self.castle_flags = to_castle_flags(w_oo, w_ooo,
                    b_oo, b_ooo)
            self.hash ^= zobrist.castle_hash(self.castle_flags)

            self.fifty_count = int(fifty_count, 10)
            self.ply = 2 * (int(full_moves, 10) - 1) + int(not self.wtm)
            self.start_ply = self.ply # 0 for new games

            if ep == '-':
                self.ep = None
            else:
                # only set ep if there is a legal capture
                # XXX: this is even stricter than X-FEN; maybe
                # we should not check for true legality, but only
                # whether there is an enemy pawn on an adjacent
                # square?
                self.ep = 'abcdefgh'.index(ep[0]) + \
                    0x10 * '1234567'.index(ep[1])
                if rank(self.ep) not in (2, 5):
                    raise BadFenError('bad en passant square')
                self.hash ^= zobrist.ep_hash(self.ep)
                # legality checking needs a value for in_check
                self.in_check = None
                if not self._is_legal_ep(self.ep):
                    # undo the en passant square
                    self.ep = None
                    self.hash ^= zobrist.ep_hash(self.ep)

            #assert(self.hash == self._compute_hash())
            self.history.set_hash(self.ply, self.hash)

            if detect_check:
                self.detect_check()
                if self.is_checkmate or self.is_stalemate \
                        or self.is_draw_nomaterial:
                    raise BadFenError('got a terminal position')


        except AssertionError:
            raise
        # Usually I don't like using a catch-all except, but it seems to
        # be the safest default action because the FEN is supplied by
        # the user.
        #except:
        #    raise BadFenError()

    def __iter__(self):
        for r in range(0, 8):
            for f in range(0, 8):
                sq = 0x10 * r + f
                yield (sq, self.board[sq])

    def make_move(self, mv):
        """make the move"""
        self.ply += 1

        mv.undo = Undo()
        mv.undo.ep = self.ep
        mv.undo.in_check = self.in_check
        mv.undo.castle_flags = self.castle_flags
        mv.undo.fifty_count = self.fifty_count
        mv.undo.material = self.material[:]
        mv.undo.hash = self.hash

        if self.ep:
            # clear old en passant hash
            self.hash ^= zobrist.ep_hash(self.ep)
            self.ep = None
        self.board[mv.fr] = '-'
        if not mv.prom:
            self.board[mv.to] = mv.pc
            self.hash ^= zobrist.piece_hash(mv.fr, mv.pc) ^ \
                zobrist.piece_hash(mv.to, mv.pc)
        else:
            self.board[mv.to] = mv.prom
            self.hash ^= zobrist.piece_hash(mv.fr, mv.pc) ^\
                zobrist.piece_hash(mv.to, mv.prom)
            self.material[self.wtm] += piece_material[mv.prom.lower()] \
                - piece_material['p']

        if mv.pc == 'k':
            self.king_pos[0] = mv.to
        elif mv.pc == 'K':
            self.king_pos[1] = mv.to

        if mv.pc in ['p', 'P'] or mv.is_capture:
            self.fifty_count = 0
        else:
            self.fifty_count += 1

        if mv.is_capture:
            self.hash ^= zobrist.piece_hash(mv.to, mv.capture)
            self.material[not self.wtm] -= piece_material[mv.capture.lower()]

        if mv.is_ep:
            self.material[not self.wtm] -= piece_material['p']
            # remove the captured pawn
            if self.wtm:
                assert(self.board[mv.to - 0x10] == 'p')
                self.hash ^= zobrist.piece_hash(mv.to - 0x10, 'p')
                self.board[mv.to - 0x10] = '-'
            else:
                assert(self.board[mv.to + 0x10] == 'P')
                self.hash ^= zobrist.piece_hash(mv.to + 0x10, 'P')
                self.board[mv.to + 0x10] = '-'
        elif mv.is_oo:
            # move the rook
            if self.wtm:
                assert(self.board[H1] == 'R')
                self.board[F1] = 'R'
                self.board[H1] = '-'
                self.hash ^= zobrist.piece_hash(F1, 'R') ^ \
                    zobrist.piece_hash(H1, 'R')
            else:
                assert(self.board[H8] == 'r')
                self.board[F8] = 'r'
                self.board[H8] = '-'
                self.hash ^= zobrist.piece_hash(F8, 'r') ^ \
                    zobrist.piece_hash(H8, 'r')
        elif mv.is_ooo:
            # move the rook
            if self.wtm:
                assert(self.board[A1] == 'R')
                self.board[D1] = 'R'
                self.board[A1] = '-'
                self.hash ^= zobrist.piece_hash(D1, 'R') ^ \
                    zobrist.piece_hash(A1, 'R')
            else:
                assert(self.board[A8] == 'r')
                self.board[D8] = 'r'
                self.board[A8] = '-'
                self.hash ^= zobrist.piece_hash(A8, 'r') ^ \
                    zobrist.piece_hash(D8, 'r')

        self.castle_flags &= castle_mask[mv.fr] & castle_mask[mv.to]
        if self.castle_flags != mv.undo.castle_flags:
            self.hash ^= zobrist.castle_hash(self.castle_flags) ^ \
                zobrist.castle_hash(mv.undo.castle_flags)
        self.wtm = not self.wtm
        self.hash ^= zobrist.side_hash
        #self._check_material()

        if mv.new_ep and self._is_legal_ep(mv.new_ep):
            self.ep = mv.new_ep
            self.hash ^= zobrist.ep_hash(self.ep)

        self.history.set_move(self.ply - 1 , mv)
        #assert(self.hash == self._compute_hash())
        self.history.set_hash(self.ply, self.hash)

    def _is_legal_ep(self, ep):
        # According to Geurt Gijssen's "An Arbiter's Notebook" #110,
        # if an en passant capture that is otherwise legal is not
        # permitted because it would leave the king in check,
        # then for the puposes of claiming a draw by repetition, the
        # position is identical to one where there is no such en
        # passant capture.  So we have to test the legality of
        # en passant captures.
        if self.wtm:
            if (valid_sq(ep - 0x11) and self.board[ep - 0x11] == 'P' and
                    Move(self, ep - 0x11, ep, is_ep=True).is_legal()):
                return True
            elif (valid_sq(ep - 0xf) and self.board[ep - 0xf] == 'P' and
                    Move(self, ep - 0xf, ep, is_ep=True).is_legal()):
                return True
        else:
            if (valid_sq(ep + 0xf) and self.board[ep + 0xf] == 'p' and
                    Move(self, ep + 0xf, ep, is_ep=True).is_legal()):
                return True
            elif (valid_sq(ep + 0x11) and self.board[ep + 0x11] == 'p' and
                    Move(self, ep + 0x11, ep, is_ep=True).is_legal()):
                return True
        return False

    def _compute_hash(self):
        hash = 0
        if self.wtm:
            hash ^= zobrist.side_hash
        for (sq, pc) in self:
            if pc != '-':
                hash ^= zobrist.piece_hash(sq, pc)
        if self.ep:
            hash ^= zobrist.ep_hash(self.ep)
        hash ^= zobrist.castle_hash(self.castle_flags)
        return hash

    def undo_move(self, mv):
        """undo the move"""
        self.wtm = not self.wtm
        self.ply -= 1
        self.ep = mv.undo.ep
        self.board[mv.to] = mv.capture
        self.board[mv.fr] = mv.pc
        self.in_check = mv.undo.in_check
        self.castle_flags = mv.undo.castle_flags
        self.fifty_count = mv.undo.fifty_count
        self.material = mv.undo.material
        self.hash = mv.undo.hash

        if mv.pc == 'k':
            self.king_pos[0] = mv.fr
        elif mv.pc == 'K':
            self.king_pos[1] = mv.fr

        if mv.is_ep:
            if self.wtm:
                assert(self.board[mv.to - 0x10] == '-')
                self.board[mv.to - 0x10] = 'p'
            else:
                assert(self.board[mv.to + 0x10] == '-')
                self.board[mv.to + 0x10] = 'P'
        elif mv.is_oo:
            if self.wtm:
                assert(self.board[F1] == 'R')
                self.board[H1] = 'R'
                self.board[F1] = '-'
            else:
                assert(self.board[F8] == 'r')
                self.board[H8] = 'r'
                self.board[F8] = '-'
        elif mv.is_ooo:
            if self.wtm:
                assert(self.board[D1] == 'R')
                self.board[A1] = 'R'
                self.board[D1] = '-'
            else:
                assert(self.board[D8] == 'r')
                self.board[A8] = 'r'
                self.board[D8] = '-'
        #self._check_material()
        #assert(self.hash == self._compute_hash())

    def _check_material(self):
        bmat = sum([piece_material[pc.lower()]
            for (sq, pc) in self if pc != '-' and not piece_is_white(pc)])
        assert(bmat == self.material[0])
        assert(self.material[1] == sum([piece_material[pc.lower()]
            for (sq, pc) in self if pc != '-' and piece_is_white(pc)]))

    def detect_check(self):
        """detect whether the player to move is in check, checkmated,
        or stalemated"""
        self.in_check = self.under_attack(self.king_pos[self.wtm],
            not self.wtm)

        any_legal = self._any_legal_moves()
        self.is_checkmate = self.in_check and not any_legal
        self.is_stalemate = not self.in_check and not any_legal

        self._check_mating_material()
        self.is_draw_nomaterial = (not self.white_has_mating_material and
            not self.black_has_mating_material)

    def _check_mating_material(self):
        self.white_has_mating_material = self.material[1] > 3
        self.black_has_mating_material = self.material[0] > 3
        if (not self.white_has_mating_material or
                not self.black_has_mating_material):
            for (sq, pc) in self:
                if pc == 'P':
                    self.white_has_mating_material = True
                elif pc == 'p':
                    self.black_has_mating_material = True


    def get_last_move(self):
        return self.history.get_move(self.ply - 1)

    def _any_legal_moves(self):
        if self.ep:
            return True
        ksq = self.king_pos[self.wtm]
        if self._any_pc_moves(ksq, self.board[ksq]):
            return True
        # it's slow to iterate over every square in the board, but it's
        # only necessary if the king has no legal moves
        for (sq, pc) in self:
            #if pc != '-' and piece_is_white(pc) == self.wtm:
            if pc not in ['-', 'K', 'k'] and piece_is_white(pc) == self.wtm:
                cur_sq = sq
                if self._any_pc_moves(sq, pc):
                    return True
        return False

    def _pawn_cap_at(self, sq):
        if not valid_sq(sq):
            return False
        pc = self.board[sq]
        return pc != '-' and piece_is_white(pc) != self.wtm

    def _any_pc_moves(self, sq, pc):
        if pc == 'P':
            if self.board[sq + 0x10] == '-':
                if Move(self, sq, sq + 0x10).is_legal():
                    return True
                if rank(sq) == 1 and self.board[sq + 0x20] == '-' and Move(
                        self, sq, sq + 0x20).is_legal():
                    return True
            if self._pawn_cap_at(sq + 0xf) and Move(
                    self, sq, sq + 0xf,
                    is_ep=sq + 0xf == self.ep).is_legal():
                return True
            if self._pawn_cap_at(sq + 0x11) and Move(
                    self, sq, sq + 0x11,
                    is_ep=sq + 0x11 == self.ep).is_legal():
                return True
        elif pc == 'p':
            if self.board[sq - 0x10] == '-':
                if Move(self, sq, sq - 0x10).is_legal():
                    return True
                if rank(sq) == 6 and self.board[sq - 0x20] == '-' and Move(
                        self, sq, sq - 0x20).is_legal():
                    return True
            if self._pawn_cap_at(sq - 0xf) and Move(
                    self, sq, sq - 0xf,
                    is_ep=sq - 0xf == self.ep).is_legal():
                return True
            if self._pawn_cap_at(sq - 0x11) and Move(
                    self, sq, sq - 0x11,
                    is_ep=sq - 0x11 == self.ep).is_legal():
                return True
        else:
            for d in piece_moves[pc.lower()]:
                cur_sq = sq + d
                # we don't need to check castling because if castling
                # is legal, some other king move must be also
                while valid_sq(cur_sq):
                    topc = self.board[cur_sq]
                    if topc == '-' or piece_is_white(topc) != self.wtm:
                        mv = Move(self, sq, cur_sq)
                        if mv.is_legal():
                            return True
                    if not pc in sliding_pieces or self.board[cur_sq] != '-':
                        break
                    cur_sq += d

    def _is_pc_at(self, pc, sq):
        return valid_sq(sq) and self.board[sq] == pc

    def under_attack(self, sq, wtm):
        """determine whether a square is attacked by the given side"""
        # pawn attacks
        if wtm:
            if (self._is_pc_at('P', sq - 0x11)
                    or self._is_pc_at('P', sq - 0xf)):
                return True
        else:
            if (self._is_pc_at('p', sq + 0x11)
                    or self._is_pc_at('p', sq + 0xf)):
                return True

        #  knight attacks
        npc = 'N' if wtm else 'n'
        for d in piece_moves['n']:
            if self._is_pc_at(npc, sq + d):
                return True

        # king attacks
        kpc = 'K' if wtm else 'k'
        for d in piece_moves['k']:
            if self._is_pc_at(kpc, sq + d):
                return True

        # bishop/queen attacks
        for d in piece_moves['b']:
            cur_sq = sq +d
            while valid_sq(cur_sq):
                if self.board[cur_sq] != '-':
                    if wtm:
                        if self.board[cur_sq] in ['B', 'Q']:
                            return True
                    else:
                        if self.board[cur_sq] in ['b', 'q']:
                            return True
                    # square blocked
                    break
                cur_sq += d


        # rook/queen attacks
        for d in piece_moves['r']:
            cur_sq = sq + d
            while valid_sq(cur_sq):
                if self.board[cur_sq] != '-':
                    if wtm:
                        if self.board[cur_sq] in ['R', 'Q']:
                            return True
                    else:
                        if self.board[cur_sq] in ['r', 'q']:
                            return True
                    # square blocked
                    break
                cur_sq += d

        return False

    lalg_re = re.compile(r'([a-h][1-8])([a-h][1-8])(?:=([NBRQ]))?$')
    def move_from_lalg(self, s):
        m = self.lalg_re.match(s)
        if not m:
            return None

        fr = str_to_sq(m.group(1))
        to = str_to_sq(m.group(2))
        prom = m.group(3)
        if prom == None:
            mv = Move(self, fr, to)
            if mv.pc == 'K' and fr == E1:
                if to == G1:
                    mv.is_oo = True
                elif to == C1:
                    mv.is_ooo = True
            elif mv.pc == 'k' and fr == E8:
                if to == G8:
                    mv.is_oo = True
                elif to == C8:
                    mv.is_ooo = True
        else:
            if self.wtm:
                assert(prom == prom.upper())
                mv = Move(self, fr, to, prom=prom)
            else:
                mv = Move(self, fr, to, prom=prom.lower())

        if mv:
            mv.check_pseudo_legal()
            mv.check_legal()

        return mv

    san_pawn_push_re = re.compile(r'^([a-h][1-8])(?:=([NBRQ]))?$')
    san_pawn_capture_re = re.compile(r'^([a-h])x([a-h][1-8])(?:=([NBRQ]))?$')
    san_piece_re = re.compile(r'([NBRQK])([a-h])?([1-8])?(x)?([a-h][1-8])$')
    decorator_re = re.compile(r'[\+#\?\!]+$')
    def move_from_san(self, s):
        s = self.decorator_re.sub('', s)
        matched = False
        mv = None

        # examples: e4 e8=Q
        m = self.san_pawn_push_re.match(s)
        if m:
            to = str_to_sq(m.group(1))
            if self.board[to] != '-':
                raise IllegalMoveError('pawn push blocked')
            prom = m.group(2)
            if prom:
                if self.wtm:
                    prom = m.group(2)
                    assert(prom == prom.upper())
                else:
                    prom = m.group(2).lower()
            new_ep = None
            if self.wtm:
                fr = to - 0x10
                if rank(to) == 3 and self.board[fr] == '-':
                    new_ep = fr
                    fr = to - 0x20
                if self.board[fr] != 'P':
                    raise IllegalMoveError('illegal white pawn move')
                if prom:
                    if rank(to) == 7:
                        mv = Move(self, fr, to, prom=prom)
                    else:
                        raise IllegalMoveError('illegal promotion')
                else:
                    mv = Move(self, fr, to, new_ep=new_ep)
            else:
                fr = to + 0x10
                if rank(to) == 4 and self.board[fr] == '-':
                    new_ep = fr
                    fr = to + 0x20
                if self.board[fr] != 'p':
                    raise IllegalMoveError('illegal black pawn move')
                if prom:
                    if rank(to) == 0:
                        mv = Move(self, fr, to, prom=prom)
                    else:
                        raise IllegalMoveError('illegal promotion')
                else:
                    mv = Move(self, fr, to, new_ep=new_ep)

        # examples: dxe4 dxe8=Q
        m = None
        if not mv:
            m = self.san_pawn_capture_re.match(s)
        if m:
            to = str_to_sq(m.group(2))
            prom = m.group(3)
            if prom:
                if self.wtm:
                    assert(prom == prom.upper())
                else:
                    prom = prom.lower()

            is_ep = to == self.ep
            if is_ep:
                assert(self.board[to] == '-')
            else:
                topc = self.board[to]
                if topc == '-' or piece_is_white(topc) == self.wtm:
                    raise IllegalMoveError('bad pawn capture')

            f = 'abcdefgh'.index(m.group(1))
            if f == file(to) - 1:
                if self.wtm:
                    fr = to - 0x11
                    if self.board[fr] != 'P':
                        raise IllegalMoveError('bad pawn capture')
                else:
                    fr = to + 0xf
                    if self.board[fr] != 'p':
                        raise IllegalMoveError('bad pawn capture')
            elif f == file(to) + 1:
                if self.wtm:
                    fr = to - 0xf
                    if self.board[fr] != 'P':
                        raise IllegalMoveError('bad pawn capture')
                else:
                    fr = to + 0x11
                    if self.board[fr] != 'p':
                        raise IllegalMoveError('bad pawn capture')
            else:
                raise IllegalMoveError('bad pawn capture file')

            mv = Move(self, fr, to, prom=prom, is_ep=is_ep)

        # examples: Nf3 Nxf3 Ng1xf3
        m = None
        if not mv:
            m = self.san_piece_re.match(s)
        if m:
            to = str_to_sq(m.group(5))
            if m.group(4):
                if self.board[to] == '-':
                    raise IllegalMoveError('capture on blank square')
            else:
                if self.board[to] != '-':
                    raise IllegalMoveError('missing "x" to indicate capture')

            pc = m.group(1) if self.wtm else m.group(1).lower()
            # TODO: it would be faster to disambiguate first, so we
            # do not check whether moves are legal unnecessarily
            froms = self.get_from_sqs(pc, to)

            if m.group(2):
                if len(froms) <= 1:
                    raise IllegalMoveError('unnecessary disambiguation')
                f = 'abcdefgh'.index(m.group(2))
                froms = filter(lambda sq: file(sq) == f, froms)

            if m.group(3):
                r = '12345678'.index(m.group(3))
                if len(froms) <= 1:
                    raise IllegalMoveError('unnecessary disambiguation')
                froms = filter(lambda sq: rank(sq) == r, froms)

            if len(froms) != 1:
                raise IllegalMoveError('illegal or ambiguous move %s: %d interpretations' % (s, len(froms)))

            mv = Move(self, froms[0], to)

        '''if mv:
            try:
                mv.check_pseudo_legal()
            except IllegalMoveError:
                raise RuntimeError('san inconsistency')
            mv.check_legal()'''

        return mv

    def move_from_castle(self, s):
        mv = None
        s = self.decorator_re.sub('', s)
        if not mv and s in ['O-O', 'OO', 'o-o']:
            if self.wtm:
                mv = Move(self, E1, G1, is_oo=True)
            else:
                mv = Move(self, E8, G8, is_oo=True)

        if not mv and s in ['O-O-O', 'OOO', 'o-o-o']:
            if self.wtm:
                mv = Move(self, E1, C1, is_ooo=True)
            else:
                mv = Move(self, E8, C8, is_ooo=True)

        if mv:
            mv.check_pseudo_legal()
            mv.check_legal()

        return mv

    def get_from_sqs(self, pc, sq):
        '''given a piece (not including a pawn) and a destination square,
        return a list of all legal source squares'''
        ret = []
        is_sliding = pc in sliding_pieces
        for d in piece_moves[pc.lower()]:
            cur_sq = sq
            while 1:
                cur_sq += d
                if not valid_sq(cur_sq):
                    break
                if self.board[cur_sq] == pc:
                    if Move(self, cur_sq, sq).is_legal():
                        ret.append(cur_sq)
                if not (self.board[cur_sq] == '-' and is_sliding):
                    break
        return ret

    def is_draw_fifty(self):
        # If we checkmate comes on the move that causes the fifty-move
        # counter to reach 100, the game is not a draw.  That shouldn't
        # be a problem because if a player is checkmated, he or she
        # won't have a chance to offer a draw and trigger this check.
        return self.fifty_count >= 100

    def is_draw_repetition(self, side):
        #assert(self.hash == self._compute_hash())
        """check for draw by repetition"""

        # Note that the most recent possible identical position is
        # 4 ply ago, and we only have to check every other move.
        # This is a well-known chess engine optimization.
        if self.ply < 8:
            return False
        stop = max(self.ply - self.fifty_count, self.start_ply)

        count = 0
        hash = self.history.get_hash(self.ply)
        i = self.ply - 4
        while i >= stop:
            if self.history.get_hash(i) == hash:
                count += 1
                if count == 2:
                    return True
            i -= 2

        # Also check the previous position, because unlike OTB chess,
        # we do not provide a way to write down a move and offer a draw
        # without actually executing the move.  (Well, we do: an argument to
        # the "draw" command, but few people know about it.)
        #
        # Previously, FICS allowed either player to claim a draw if the
        # current or previous position represented a threefold repetition,
        # regardless of which player's move it was.  (Note that this is
        # different from FIDE rules, which only consider the current
        # position and only allow a player to claim a draw on his or her
        # own turn.)  My idea is to only check the previous position
        # when the player making the draw offer has the move, to avoid
        # a situation like the following:
        # 
        # Player A has the move.  The current position represents a 
        # threefold repetition, so player A is entitled to claim a draw.
        # Instead, Player A decides to press on, and plays a blunder
        # that loses his queen.  Player A realizes the mistake before
        # the opponent has a chance to move, and claims a draw.
        #
        # The old fics grants the draw request, unreasonably in my 
        # opinion.  My change should close the loophole.
        if self.ply > 8 and (side == WHITE) == self.wtm:
            count = 0
            hash = self.history.get_hash(self.ply - 1)
            i = self.ply - 5
            while i >= stop:
                if self.history.get_hash(i) == hash:
                    count += 1
                    if count == 2:
                        return True
                i -= 2

        return False
    
    def to_xfen(self):
        p = []
        for r in range(7, -1, -1):
            num_empty = 0
            for f in range(0, 8):
                sq = 0x10 * r + f
                pc = self.board[sq]
                if pc == '-':
                    num_empty += 1
                else:
                    if num_empty > 0:
                        p.append(str(num_empty))
                        num_empty = 0
                    p.append(pc)
            if num_empty > 0:
                p.append(str(num_empty))
                num_empty = 0
            if r != 0:
                p.append('/')
        pos_str = ''.join(p)

        stm_str = 'w' if self.wtm else 'b'

        castling = ''
        if self.check_castle_flags(True, True):
            castling += 'K'
        if self.check_castle_flags(True, False):
            castling += 'Q'
        if self.check_castle_flags(False, True):
            castling += 'k'
        if self.check_castle_flags(False, False):
            castling += 'q'
        if castling == '':
            castling = '-'

        # we follow X-FEN rather than FEN: only print an en passant
        # square if there is a legal en passant capture
        if self.ep:
            ep_str = sq_to_str(self.ep)
            assert(ep_str[1] in ['3', '6'])
        else:
            ep_str = '-'

        full_moves = self.ply // 2 + 1
        return "%s %s %s %s %d %d" % (pos_str, stm_str, castling, ep_str, self.fifty_count, full_moves)

    def check_castle_flags(self, wtm, is_oo):
        return bool(self.castle_flags & (1 << (2 * int(wtm) + int(is_oo))))


class Chess(BaseVariant):
    """normal chess"""
    def __init__(self, game):
        self.game = game
        self.pos = copy.deepcopy(initial_pos)
        self.name = 'chess'

    def parse_move(self, s, conn):
        """Try to parse a move.  If it looks like a move but
        is erroneous or illegal, raise an exception.  Return the move if
        parsing was sucessful, or False if it does not look like a move
        and should be processed further."""

        mv = None

        try:
            # castling
            mv = self.pos.move_from_castle(s)

            # long algebraic
            if not mv:
                mv = self.pos.move_from_lalg(s)

            # san
            if not mv:
                mv = self.pos.move_from_san(s)
        except IllegalMoveError as e:
            #print e.reason
            raise

        return mv

    def do_move(self, mv):
        mv.to_san()
        self.pos.make_move(mv)
        self.pos.detect_check()
        mv.add_san_decorator()

    def undo_move(self):
        self.pos.undo_move(self.pos.get_last_move())

    def get_turn(self):
        return WHITE if self.pos.wtm else BLACK

    def to_deltaboard(self, user):
        """ Get the last move in the shortened format used by clients that
        set the "compressmove" ivar. """
        last_mv = self.pos.get_last_move()
        # delta boards should not be sent before the first move
        assert(last_mv is not None)
        assert(last_mv.time is not None)
        last_mv_time = int(round(1000 * last_mv.time))
        if self.pos.wtm:
            clock = int(round(1000 * self.game.clock.get_black_time()))
        else:
            clock = int(round(1000 * self.game.clock.get_white_time()))
        # <d1> 399 10 O-O e8g8c 922 168890 207
        s = '\n<d1> %d %d %s %s %d %d %d\n' % (
            self.game.number, self.pos.ply, last_mv.to_san(),
            last_mv.to_smith(), last_mv_time, clock, last_mv.lag)

        return s

def init_direction_table():
    for r in range(8):
        for f in range(8):
            sq = 0x10 * r + f
            for d in piece_moves['q']:
                cur_sq = sq + d
                while valid_sq(cur_sq):
                    assert(0 <= cur_sq - sq + 0x7f <= 0xff)
                    if direction_table[cur_sq - sq + 0x7f] != 0:
                        assert(d == direction_table[cur_sq - sq + 0x7f])
                    else:
                        direction_table[cur_sq - sq + 0x7f] = d
                    cur_sq += d
init_direction_table()

initial_pos = Position('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

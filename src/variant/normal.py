"""This implements routines for normal chess.  (I avoid the term
standard since that is used to describe the game speed on FICS.)
Maybe normal chess technically not a variant, but organizationally
I didn't want to privilege it over variants, so it is here. """

import re
import copy

from variant import Variant

class BadFenError(Exception):
    pass

(BP, BN, BB, BR, BQ, BK, WP, WN, WB, WR, WQ, WK, BLANK) = range(13)
class Board(object):
    """0x88 board representation"""

    char_to_piece = {
        'p': BP, 'n': BN, 'b': BB, 'r': BR, 'q': BQ, 'k': BK,
        'P': WP, 'N': WN, 'B': WB, 'R': WR, 'Q': WQ, 'K': WK
    }
    piece_to_char = dict([(p, c) for (c, p) in char_to_piece.iteritems()])

    def __init__(self, fen=None):
        self.board = 0x80 * [BLANK]
        if fen != None:
            self.set_pos(fen)
        else:
            assert(False)
            self.white_oo = False
            self.white_ooo = False

    def rank(self, sq):
        return sq / 0x10

    def file(self, sq):
        return sq % 8

    def valid_sq(self, sq):
        return not (sq & 0x88)

    def set_pos(self, fen):
        """Set the position from Forsyth-Fdwards notation.  The format
        is intentionally interpreted strictly; better to give the user an
        error than take in bad data."""
        try:
            # rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
            m = re.match(r'''^([1-8rnbqkpRNBQKP/]+) ([wb]) ([kqKQ]+|-) ([a-h][36]|-) (\d+) (\d+)$''', fen)
            if not m:
                raise BadFenError()
            (pos, side, castle_flags, ep, half_moves, full_moves) = (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6))

            ranks = pos.split('/')
            ranks.reverse()
            for (r, rank) in enumerate(ranks):
                assert(not '/' in rank)
                sq = 0x10 * r
                for c in rank:
                    d = '12345678'.find(c)
                    if d > 0:
                        sq += d + 1
                    else:
                        assert(self.valid_sq(sq))
                        self.board[sq] = self.char_to_piece[c]
                        sq += 1
                if sq & 0xf != 8:
                    raise BadFenError()

            self.wtm = side == 'w'

            # This doesn't give an error on repeated flags (like "qq"),
            # but I think that's OK, since it's still unambiguous.
            self.w_oo = 'K' in castle_flags
            self.w_ooo = 'Q' in castle_flags
            self.b_oo = 'k' in castle_flags
            self.b_ooo = 'K' in castle_flags

            if ep == '-':
                self.ep = None
            else:
                self.ep = ep[0].index('abcdefgh') + 0x10 * ep[1].index('012345678')
            
            self.half_moves = int(half_moves, 10)
            if int(full_moves, 10) != self.half_moves / 2 + 1:
                raise BadFenError()

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

    def to_fen(self):
        pos_str = ''
        for (sq, pc) in self:
            pos_str += self.piece_to_char[pc]
        stm_str = 'w' if self.wtm else 'b'
        castling = ''
        if self.white_oo:
            castling += 'K'
        if self.white_ooo:
            castling += 'Q'
        if self.black_oo:
            castling += 'k'
        if self.black_ooo:
            castling += 'q'
        if castling == '':
            castling = '-'

        if self.ep == None:
            ep_str = '-'
        else:
            ep_str = chr(ord('a') + ep)
            if self.wtm:
                ep_str += '3'
            else:
                ep_str += '6'
        move_num = self.half_moves / 2 + 1
        return "%s %s %s %s %d %d" % (pos_str, stm_str, castling, ep_str, self.half_moves, move_num)

class Normal(Variant):
    def __init__(self, fen=None):
        self.board = copy.copy(initial_pos)
        print 'this is normal chess'

    def get_move(s):
        """attempt to get the next move from s, returning None if it's
        not a move"""
        pass


initial_pos = Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

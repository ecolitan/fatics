"""This implements routines for normal chess.  (I avoid the term
standard since that is used to describe the game speed on FICS.)
Maybe normal chess technically not a variant, but organizationally
I didn't want to privilege it over variants, so it is here. """

import re
import copy
from array import array

from variant import Variant

class BadFenError(Exception):
    pass
class IllegalMoveError(Exception):
    pass

piece_moves = {
    'n': [-0x21, -0x1f, -0xe, -0x12, 0x12, 0xe, 0x1f, 0x21],
    'b': [-0x11, -0xf, 0xf, 0x11],
    'r': [-0x10, -1, 1, 0x10],
    'q': [-0x11, -0xf, 0xf, 0x11, -0x10, -1, 1, 0x10],
    'k': [-0x11, -0xf, 0xf, 0x11, -0x10, -1, 1, 0x10]
}
direction_table = array('i', [0 for i in range(0, 0x100)])
def init_direction_table():
    b = Board()
    for (sq, dummy) in b:
        for d in piece_moves['q']:
            cur_sq = sq + d
            while b.valid_sq(cur_sq):
                assert(0 <= cur_sq - sq + 0x7f <= 0xff)
                if direction_table[cur_sq - sq + 0x7f] != 0:
                    assert(d == direction_table[cur_sq - sq + 0x7f])
                else:
                    direction_table[cur_sq - sq + 0x7f] = d
                cur_sq += d
def dir(fr, to):
    """Returns the direction a queen needs to go to get from TO to FR,
    or 0 if it's not possible."""
    return direction_table[to - fr + 0x7f]

sliding_pieces = frozenset(['b', 'r', 'q', 'B', 'R', 'Q'])

class Board(object):
    """
    0x88 board representation; pieces are represented as ASCII,
    the same as FEN. A blank square is '-'.
    
    """

    def __init__(self, fen=None):
        self.board = 0x80 * ['-']
        if fen != None:
            self.set_pos(fen)
        else:
            pass
            #self.white_oo = False
            #self.white_ooo = False

    def rank(self, sq):
        return sq / 0x10

    def file(self, sq):
        return sq % 8

    def valid_sq(self, sq):
        return not (sq & 0x88)

    def sq_from_str(self, sq):
        return 'abcdefgh'.index(sq[0]) + 0x10 * '12345678'.index(sq[1])

    def piece_is_white(self, pc):
        assert(len(pc) == 1)
        assert(pc in 'pnbrqkPNBRQK')
        return pc.isupper()

    def _move_is_legal(self, pc, fr, to):
        diff = to - fr
        if pc == 'p':
            if self.board[to] == '-':
                if diff == -0x10:
                    return True
                elif diff == -0x20 and self.rank(fr) == 6:
                    return True
                elif to == self.ep:
                    return True
                else:
                    return False
            else:
                return diff in [-0x11, -0xf]
        elif pc == 'P':
            if self.board[to] == '-':
                if diff == 0x10:
                    return True
                elif diff == 0x20 and self.rank(fr) == 1:
                    return True
                elif to == self.ep:
                    return True
                else:
                    return False
            else:
                return diff in [0x11, 0xf]
        else:
            if pc in sliding_pieces:
                d = dir(fr, to)
                if d == 0 or not d in piece_moves[pc.lower()]:
                    # the piece cannot make that move
                    return False
                # now check if there are any pieces in the way
                for d in piece_moves[pc.lower()]:
                    cur_sq = fr + d
                    while cur_sq != to:
                        if self.board[cur_sq] != '-':
                            return False
                        cur_sq += d
                    return True
            else:
                return to - fr in piece_moves[pc.lower()]

    def make_move(self, fr, to, prom):
        """Raises IllegalMoveError when appropriate."""
        pc = self.board[fr]
        if pc == '-' or self.piece_is_white(pc) != self.wtm:
            raise IllegalMoveError()
        topc = self.board[to]
        if topc != '-' and self.piece_is_white(topc) == self.wtm:
            # cannot capture own piece
            raise IllegalMoveError()

        if not self._move_is_legal(pc, fr, to):
                raise IllegalMoveError()

        self.board[to] = self.board[fr]
        self.board[fr] = '-'

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
                        self.board[sq] = c
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
            pos_str += pc
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

    '''def is_move(self, s):
        """check whether is a move"""
    
        # long-algebraic (e.g. "e2e4", "b7a8=Q")
        m = re.match('([a-h][1-8])([a-h][1-8])(?:=([nbrq]))', s)
        return m'''

    def do_move(self, s, conn):
        """Try to parse a move and execute it.  If it looks like a move but
        is erroneous or illegal, raise an exception.  Return True if
        the move was handled, or False if it does not look like a move
        and should be processed further."""

        matched = False
        m = re.match(r'([a-h][1-8])([a-h][1-8])(?:=([NBRQ]))?', s)
        if m:
            fr = self.board.sq_from_str(m.group(1))
            to = self.board.sq_from_str(m.group(2))
            if m.group(3) != None:
                if self.board.wtm:
                    prom = m.group(3).upper()
                else:
                    prom = m.group(3).lower()
            else:
                prom = None
            matched = True

        if matched:
            if not conn.user.session.is_white == self.board.wtm:
                #conn.write('user %d, wtm %d\n' % conn.user.session.is_white, self.board.wtm)
                conn.write(_('It is not your move.\n'))
            else:
                try:
                    self.board.make_move(fr, to, prom)
                except IllegalMoveError:
                    conn.write('Illegal move (%s)\n' % s)

        return matched



initial_pos = Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
init_direction_table()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

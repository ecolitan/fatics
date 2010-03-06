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
    b = Position()
    for (sq, dummy) in b:
        for d in piece_moves['q']:
            cur_sq = sq + d
            while valid_sq(cur_sq):
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

C1 = 2
E1 = 4
G1 = 6
C8 = 0x72
E8 = 0x74
G8 = 0x76

def rank(sq):
    return sq / 0x10

def file(sq):
    return sq % 8

def valid_sq(sq):
    return not (sq & 0x88)

def sq_from_str(sq):
    return 'abcdefgh'.index(sq[0]) + 0x10 * '12345678'.index(sq[1])

def piece_is_white(pc):
    assert(len(pc) == 1)
    assert(pc in 'pnbrqkPNBRQK')
    return pc.isupper()


class Position(object):
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

    def attempt_move(self, mv):
        """Raises IllegalMoveError when appropriate."""

        topc = self.board[mv.to]
        if topc != '-' and piece_is_white(topc) == self.wtm:
            # cannot capture own piece
            raise IllegalMoveError()

        if not mv.is_legal():
            raise IllegalMoveError()

        self.make_move(mv)

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
                        assert(valid_sq(sq))
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
    
    def make_move(self, mv):
        """make the move"""
        self.wtm = not self.wtm
        self.half_moves += 1
        self.board[mv.fr] = '-'
        self.board[mv.to] = mv.pc if not mv.prom else mv.prom
        mv.make_extra()
    
    def undo_move(self, mv):
        """undo the move"""
        self.wtm = not self.wtm
        self.half_moves -= 1
        self.board[mv.to] = mv.cap
        self.board[mv.fr] = mv.pc
        mv.undo_extra()

class Move(object):
    def is_pseudo_legal(self):
        """Tests if a move is pseudo-legal, that is, legal ignoring the
        fact that the king cannot be left in check. Also sets en passant
        flags for this move."""
        diff = self.to - self.fr
        pc = self.pos.board[self.fr]
        if pc == 'p':
            if self.pos.board[self.to] == '-':
                if diff == -0x10:
                    return True
                elif diff == -0x20 and rank(self.fr) == 6:
                    self.new_ep = self.to + -0x10
                    return self.pos.board[self.new_ep] == '-'
                elif self.to == self.pos.ep:
                    return True
                else:
                    return False
            else:
                return diff in [-0x11, -0xf]
        elif pc == 'P':
            if self.pos.board[self.to] == '-':
                if diff == 0x10:
                    return True
                elif diff == 0x20 and rank(self.fr) == 1:
                    self.new_ep = self.to + 0x10
                    return self.pos.board[self.new_ep] == '-'
                elif self.to == self.pos.ep:
                    return True
                else:
                    return False
            else:
                return diff in [0x11, 0xf]
        else:
            if pc in sliding_pieces:
                d = dir(self.fr, self.to)
                if d == 0 or not d in piece_moves[pc.lower()]:
                    # the piece cannot make that move
                    return False
                # now check if there are any pieces in the way
                for d in piece_moves[pc.lower()]:
                    cur_sq = self.fr + d
                    while cur_sq != self.to:
                        if self.pos.board[cur_sq] != '-':
                            return False
                        cur_sq += d
                    return True
            else:
                return self.to - self.fr in piece_moves[pc.lower()]

    def is_legal(self):
        if not self.is_pseudo_legal():
            return False

        self.pos.make_move(self)

        self.pos.undo_move(self)
        return True

    def make_extra(self):
        """Extra things to do when making a move, like promoting a
        pawn or moving a rook when castling."""
        pass
    
    def undo_extra(self):
        """Counterpart of make_extra()."""
        pass

class Move(Move):
    def __init__(self, pos, fr, to, prom=None, is_oo=False, is_ooo=False):
        self.pos = pos
        self.fr = fr
        self.to = to
        self.prom = prom
        self.is_oo = is_oo
        self.is_ooo = is_ooo
        self.is_capture = pos.board[to] != '-'
        self.pc = self.pos.board[self.fr]
        self.cap = self.pos.board[self.to]

'''class OOMove(Move):
    def __init__(self, pos):
        self.pos = pos
        if pos.wtm:
            (self.fr, self.to) = (E1, G1)
        else:
            (self.fr, self.to) = (E8, G8)
        self.pc = self.pos.board[self.fr]
        self.cap = '-'

class OOOMove(Move):
    def __init__(self, pos):
        self.pos = pos
        if pos.wtm:
            (self.fr, self.to) = (E1, C1)
        else:
            (self.fr, self.to) = (E8, C8)
        self.pc = self.pos.board[self.fr]
        self.cap = '-' '''

class Normal(Variant):
    """normal chess"""
    def __init__(self, fen=None):
        self.pos = copy.copy(initial_pos)

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

        mv = None

        m = re.match(r'([a-h][1-8])([a-h][1-8])(?:=([NBRQ]))?', s)
        if m:
            fr = sq_from_str(m.group(1))
            to = sq_from_str(m.group(2))
            prom = m.group(3)
            if prom == None:
                mv = Move(self.pos, fr, to)
            else:
                if self.pos.wtm:
                    mv = Move(self.pos, fr, to, prom=prom.upper())
                else:
                    mv = Move(self.pos, fr, to, prom=prom.lower())

        if not mv and s in ['O-O', 'OO']:
            if self.pos.wtm:
                mv = Move(self.pos, E1, G1, is_oo=True)
            else:
                mv = Move(self.pos, E8, G8, is_ooo=True)
        
        if not mv and s in ['O-O-O', 'OOO']:
            if self.pos.wtm:
                mv = Move(self.pos, E1, C1, is_oo=True)
            else:
                mv = Move(self.pos, E8, C8, is_ooo=True)

        if mv:
            if not conn.user.session.is_white == self.pos.wtm:
                #conn.write('user %d, wtm %d\n' % conn.user.session.is_white, self.pos.wtm)
                conn.write(_('It is not your move.\n'))
            else:
                try:
                    self.pos.attempt_move(mv)
                except IllegalMoveError:
                    conn.write('Illegal move (%s)\n' % s)

        return mv != None



initial_pos = Position('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
init_direction_table()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

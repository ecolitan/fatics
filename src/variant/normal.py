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

class Move(object):
    def __init__(self, pos, fr, to, prom=None, is_oo=False, is_ooo=False):
        self.pos = pos
        self.fr = fr
        self.to = to
        self.pc = self.pos.board[self.fr]
        self.prom = prom
        self.is_oo = is_oo
        self.is_ooo = is_ooo
        self.is_capture = pos.board[to] != '-'

    def is_pseudo_legal(self):
        """Tests if a move is pseudo-legal, that is, legal ignoring the
        fact that the king cannot be left in check. Also sets en passant
        flags for this move."""
        diff = self.to - self.fr
        if self.pc == 'p':
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
        elif self.pc == 'P':
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
            if self.pc in sliding_pieces:
                d = dir(self.fr, self.to)
                if d == 0 or not d in piece_moves[self.pc.lower()]:
                    # the piece cannot make that move
                    return False
                # now check if there are any pieces in the way
                for d in piece_moves[self.pc.lower()]:
                    cur_sq = self.fr + d
                    while cur_sq != self.to:
                        if self.pos.board[cur_sq] != '-':
                            return False
                        cur_sq += d
                    return True
            else:
                return self.to - self.fr in piece_moves[self.pc.lower()]

    def is_legal(self):
        if self.is_oo:
            return (not self.pos.in_check
                and self.oo[int(self.pos.wtm)]
                and self.pos.board[self.fr + 1] == '-'
                and not self.pos.under_attack(self.fr + 1, not self.pos.wtm)
                and not self.pos.under_attack(self.to, not self.pos.wtm))

        if self.is_ooo:
            return (not self.pos.in_check
                and self.ooo[int(self.pos.wtm)]
                and self.pos.board[self.fr - 1] == '-'
                and not self.pos.under_attack(self.fr - 1, not self.pos.wtm)
                and not self.pos.under_attack(self.to, not self.pos.wtm))

        if not self.is_pseudo_legal():
            return False

        legal = True
        self.pos.make_move(self)
        if self.pos.under_attack(self.pos.kpos[int(not self.pos.wtm)],
                self.pos.wtm):
            legal = False
        self.pos.undo_move(self)
        return legal


class Position(object):
    """
    0x88 board representation; pieces are represented as ASCII,
    the same as FEN. A blank square is '-'.
    
    """

    def __init__(self, fen):
        self.board = 0x80 * ['-']
        self.oo = [None, None]
        self.ooo = [None, None]
        self.kpos = [None, None]
        self.set_pos(fen)

    def attempt_move(self, mv):
        """Raises IllegalMoveError when appropriate."""

        topc = self.board[mv.to]
        if topc != '-' and piece_is_white(topc) == self.wtm:
            # cannot capture own piece
            raise IllegalMoveError()

        if not mv.is_legal():
            raise IllegalMoveError()

        self.make_move(mv)
        self._detect_check()

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
                        if c == 'k':
                            if self.kpos[0] != None:
                                # multiple kings
                                raise BadFenError()
                            self.kpos[0] = sq
                        elif c == 'K':
                            if self.kpos[1] != None:
                                # multiple kings
                                raise BadFenError()
                            self.kpos[1] = sq
                        sq += 1
                if sq & 0xf != 8:
                    raise BadFenError()

            if None in self.kpos:
                # missing king
                raise BadFenError()

            self.wtm = side == 'w'

            # This doesn't give an error on repeated flags (like "qq"),
            # but I think that's OK, since it's still unambiguous.
            self.oo[0] = 'k' in castle_flags
            self.ooo[0] = 'K' in castle_flags
            self.oo[1] = 'K' in castle_flags
            self.ooo[1] = 'Q' in castle_flags

            if ep == '-':
                self.ep = None
            else:
                self.ep = ep[0].index('abcdefgh') + 0x10 * ep[1].index('012345678')
            
            self.half_moves = int(half_moves, 10)
            if int(full_moves, 10) != self.half_moves / 2 + 1:
                raise BadFenError()
            
            self._detect_check()

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

        mv.undo = Undo()
        mv.undo.cap = self.board[mv.to]
        mv.undo.in_check = self.in_check

        self.board[mv.fr] = '-'
        self.board[mv.to] = mv.pc if not mv.prom else mv.prom

        if mv.pc == 'k':
            self.kpos[0] = mv.to
        elif mv.pc == 'k':
            self.kpos[1] = mv.to
    
    def undo_move(self, mv):
        """undo the move"""
        self.wtm = not self.wtm
        self.half_moves -= 1
        self.board[mv.to] = mv.undo.cap
        self.board[mv.fr] = mv.pc
        self.in_check = mv.undo.in_check
        
        if mv.pc == 'k':
            self.kpos[0] = mv.fr
        elif mv.pc == 'k':
            self.kpos[1] = mv.fr

    def _detect_check(self):
        self.in_check = self.under_attack(self.kpos[int(self.wtm)],
            not self.wtm)
    
    def _is_pc_at(self, pc, sq):
        return valid_sq(sq) and self.board[sq] == pc

    def under_attack(self, sq, wtm):
        # pawn attacks
        if wtm:
            if (self._is_pc_at('P', sq + -0x11)
                    or self._is_pc_at('P', sq + -0xf)):
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
            cur_sq = sq
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
            cur_sq = sq
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

class Undo(object):
    """information needed to undo a move"""
    pass

class Normal(Variant):
    """normal chess"""
    def __init__(self, fen=None):
        self.pos = copy.copy(initial_pos)

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

def init_direction_table():
    pos = copy.copy(initial_pos)
    for (sq, dummy) in pos:
        for d in piece_moves['q']:
            cur_sq = sq + d
            while valid_sq(cur_sq):
                assert(0 <= cur_sq - sq + 0x7f <= 0xff)
                if direction_table[cur_sq - sq + 0x7f] != 0:
                    assert(d == direction_table[cur_sq - sq + 0x7f])
                else:
                    direction_table[cur_sq - sq + 0x7f] = d
                cur_sq += d

initial_pos = Position('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
init_direction_table()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

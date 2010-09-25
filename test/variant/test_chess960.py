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

from test.test import *

import random

from pgn import Pgn
from db import db

class TestChess960(Test):
    def test_bad_idn(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_admin()

        t.write('match admin white 1 0 fr idn=960\n')
        self.expect('idn must be between', t)

        self.close(t)
        self.close(t2)

    def test_checkmate(self):
        moves = ['b4', 'b6', 'Bb2', 'Bb7', 'Bxg7', 'Bxg2', 'Bxh8',
            'Bxh1', 'Qg7#' ]
        self._assert_game_is_legal(moves, 100, 'admin checkmated} 1-0')


    def test_stalemate(self):
        moves = ['h3', 'Nb6', 'Bh2', 'e6', 'e4', 'Bd6', 'e5', 'Be7', 'd4',
            'd6', 'Bb5', 'a6', 'Bxe8', 'Qxe8', 'exd6', 'Bxd6', 'Bxd6',
            'cxd6', 'Qg4', 'g6', 'Ned3', 'f5', 'Qg3', 'O-O-O', 'Nb3', 'Bf7',
            'O-O-O', 'Qc6', 'Nb4', 'Qc7', 'Rd3', 'Kb8', 'Rc3', 'Qe7', 'Re1',
            'Ka8', 'd5', 'e5', 'Qe3', 'Nxd5', 'Nxd5', 'Bxd5', 'Qb6', 'Rc8',
            'f3', 'Rxc3', 'bxc3', 'Rc8', 'Rd1', 'Rc6', 'Qe3', 'Bxb3', 'cxb3',
            'Qc7', 'Kb2', 'b5', 'Rd5', 'Kb7', 'g4', 'Rc5', 'Rxc5', 'Qxc5',
            'gxf5', 'Qxe3', 'fxg6', 'hxg6', 'Ka3', 'Qxf3', 'h4', 'Qxc3',
            'h5', 'gxh5']

        self._assert_game_is_legal(moves, 734, 'drawn by stalemate} 1/2-1/2')

    def test_examine(self):
        moves = ['b4', 'b6', 'Bb2', 'Bb7', 'Bxg7', 'Bxg2', 'Bxh8',
            'Bxh1', 'Qg7#' ]
        self._assert_game_is_legal(moves, 100, 'admin checkmated} 1-0',
            clear_hist=False)

        t = self.connect_as_admin()
        t.write('exl\n')
        self.expect('<12> qbbnrnkr pppppppp -------- -------- -------- -------- PPPPPPPP QBBNRNKR W -1 1 1 1 1 0 1 admin admin 2 0 0 39 39 0 0 1 none (0:00) none 0 0 0', t)
        t.write('forward 9999\n')
        self.expect('admin goes forward 9999', t)
        self.expect('admin checkmated 1-0', t)
        t.write('back\n')
        self.expect('admin backs up 1 move.', t)
        t.write('Qg7\n')
        self.expect('admin checkmated 1-0', t)

        t.write('unex\n')
        self.expect('You are no longer examining', t)

        t.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t)

        self.close(t)

    def test_rematch_same_idn(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_admin()
        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match admin white 1 0 fr idn=404\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')
        self.expect('<12> rbbqnnkr pppppppp -------- -------- -------- -------- PPPPPPPP RBBQNNKR W -1 1 1 1 1 0 1 GuestABCD admin 1 1 0 39 39 60 60 1 none (0:00) none 0 0 0', t)
        self.expect('<12> rbbqnnkr pppppppp -------- -------- -------- -------- PPPPPPPP RBBQNNKR W -1 1 1 1 1 0 1 GuestABCD admin -1 1 0 39 39 60 60 1 none (0:00) none 1 0 0', t2)
        t.write('res\n')
        self.expect('GuestABCD resigns} 0-1', t)
        self.expect('GuestABCD resigns} 0-1', t2)

        t.write('rem\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')
        self.expect('<12> rbbqnnkr pppppppp -------- -------- -------- -------- PPPPPPPP RBBQNNKR W -1 1 1 1 1 0 1 admin GuestABCD -1 1 0 39 39 60 60 1 none (0:00) none 1 0 0', t)
        self.expect('<12> rbbqnnkr pppppppp -------- -------- -------- -------- PPPPPPPP RBBQNNKR W -1 1 1 1 1 0 1 admin GuestABCD 1 1 0 39 39 60 60 1 none (0:00) none 0 0 0', t2)
        t.write('res\n')
        self.expect('GuestABCD resigns} 1-0', t)
        self.expect('GuestABCD resigns} 1-0', t2)

        # this test is expected to fail 1 out of every 960 runs :)
        """
        t.write('rem\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')
        self.expect_not('<12> rbbqnnkr ', t)
        t.write('abort\n')
        self.expect('aborted on move 1', t)
        self.expect('aborted on move 1', t2)
        """

        t2.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t2)

        self.close(t)
        self.close(t2)

    def _assert_game_is_legal(self, moves, idn, result=None, clear_hist=True):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_admin()
        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match admin white 1 0 fr idn=%d\n' % idn)
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm
        if result is not None:
            if 'by repetition' in result:
                t2.write('draw\n')
            self.expect(result, t)
            self.expect(result, t2)
            if clear_hist:
                t2.write('aclearhist admin\n')
                self.expect('History of admin cleared.', t2)
        else:
            t.write('abort\n')
            t2.write('abort\n')

        self.close(t)
        self.close(t2)


class TestPgn(Test):
    def test_pgn(self):
        self._skip('slow test')
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as('GuestEFGH', '')

        t.write('set style 12\n')
        t2.write('set style 12\n')

        f = open('../data/chess960.pgn', 'r')

        pgn = Pgn(f)
        for g in pgn:
            print 'game %s' % g
            assert(g.tags['FEN'])
            idn = db.idn_from_fen(g.tags['FEN'])
            if idn is None:
                print('could not get idn for fen %s' % g.tags['FEN'])
                assert(False)
            t.write('match GuestEFGH white 5 0 chess960 idn=%d\n' % idn)
            self.expect('Issuing:', t)
            self.expect('Challenge:', t2)
            t2.write('accept\n')
            self.expect('<12> ', t)
            self.expect('<12> ', t2)

            wtm = True
            for mv in g.moves:
                if wtm:
                    #print 'sending %s to white' % mv.text
                    t.write('%s%s\n' % (mv.text, mv.decorator))
                else:
                    #print 'sending %s to black' % mv.text
                    t2.write('%s%s\n' % (mv.text, mv.decorator))
                self.expect('<12> ', t)
                self.expect('<12> ', t2)
                wtm = not wtm

            if g.result == '1-0' and g.is_checkmate:
                self.expect('GuestEFGH checkmated} 1-0', t)
                self.expect('GuestEFGH checkmated} 1-0', t2)
            elif g.result == '0-1' and g.is_checkmate:
                self.expect('GuestABCD checkmated} 0-1', t)
                self.expect('GuestABCD checkmated} 0-1', t2)
            elif g.result == '1/2-1/2' and g.is_stalemate:
                self.expect('drawn by stalemate} 1/2-1/2', t)
                self.expect('drawn by stalemate} 1/2-1/2', t2)
            elif g.result == '1/2-1/2' and g.is_draw_nomaterial:
                self.expect('neither player has mating material} 1/2-1/2', t)
                self.expect('neither player has mating material} 1/2-1/2', t2)
            elif g.result == '1/2-1/2' and g.is_repetition:
                """ Old FICS does not consider holding when detecting
                repetitions, so a FICS draw by repetition won't necessarily
                be a draw by our rules. """
                if wtm:
                    t.write('draw\n')
                else:
                    t2.write('draw\n')
                self.expect('drawn by repetition} 1/2-1/2', t)
                self.expect('drawn by repetition} 1/2-1/2', t2)
                """t.write('abort\n')
                t2.write('abort\n')
                self.expect('Game aborted', t)
                self.expect('Game aborted', t2)"""
            elif g.result == '1/2-1/2' and g.is_fifty:
                random.choice([t, t2]).write('draw\n')
                self.expect('drawn by the 50 move rule} 1/2-1/2', t)
                self.expect('drawn by the 50 move rule} 1/2-1/2', t2)
            else:
                t.write('abort\n')
                t2.write('abort\n')
                # don't depend on the abort message, in case the PGN
                # omits the comment explaining why the game was drawn
                #self.expect('Game aborted', t)
                #self.expect('Game aborted', t2)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

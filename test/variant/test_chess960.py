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

from pgn import Pgn
from db import db

"""class TestChess960(Test):
    def test_chess960(self):
        pass"""

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

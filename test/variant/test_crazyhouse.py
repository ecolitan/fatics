from test.test import *

from pgn import Pgn

class TestCrazyhouse(Test):
    def test_crazyhouse(self):
        moves = ['e4', 'e6', 'Nc3', 'd6', 'd4', 'Nf6', 'Nf3', 'Nc6', 'Bg5', 'Be7', 'Bd3', 'h6', 'Bxf6', 'Bxf6', 'N@h5', 'B@g4', 'Nxf6+', 'Qxf6', 'B@h4', 'Qg6', 'e5', 'Bxf3', 'Bxg6', 'fxg6', 'Qxf3', 'B@e7', 'Q@f7+', 'Kd7', 'd5', 'Nxe5', 'Qxe6+', 'Kd8', 'Qxe7#']
        self._assert_game_is_legal(moves, 'admin checkmated} 1-0')

    def test_crazyhouse_draw(self):
        # Credit for this test game: http://www.tonyjh.com/chess/zh_notes.html
        moves = ['d4', 'd5', 'Bh6', 'Nxh6', 'e4', 'c6', 'Be2', 'B@a6', 'Bxa6', 'Qc7', 'Be2', 'Qd7', 'Ba6', 'Qd8', 'Be2', 'Qd6', 'Ba6', 'Qd8', 'Be2', 'Qd6', 'Ba6', 'Qd8']
        self._assert_game_is_legal(moves, 'drawn by repetition} 1/2-1/2')

    def _assert_game_is_legal(self, moves, result=None):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match admin white 1 0 crazyhouse\n')
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
        else:
            t.write('abort\n')
            t2.write('abort\n')

        self.close(t)
        self.close(t2)

class TestPgn(Test):
    def test_pgn(self):
        #raise unittest.SkipTest
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_user('GuestEFGH', '')

        t.write('set style 12\n')
        t2.write('set style 12\n')

        f = open('../data/zh.pgn', 'r')

        pgn = Pgn(f)
        for g in pgn:
            print 'game %s' % g
            t.write('match GuestEFGH white 5 0 crazyhouse\n')
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

            assert(not g.is_draw_nomaterial)
            if g.result == '1-0' and g.is_checkmate:
                self.expect('GuestEFGH checkmated} 1-0', t)
                self.expect('GuestEFGH checkmated} 1-0', t2)
            elif g.result == '0-1' and g.is_checkmate:
                self.expect('GuestABCD checkmated} 0-1', t)
                self.expect('GuestABCD checkmated} 0-1', t2)
            elif g.result == '1/2-1/2' and g.is_stalemate:
                self.expect('drawn by stalemate} 1/2-1/2', t)
                self.expect('drawn by stalemate} 1/2-1/2', t2)
            elif g.result == '1/2-1/2' and g.is_repetition:
                if wtm:
                    t.write('draw\n')
                else:
                    t2.write('draw\n')
                self.expect('drawn by repetition} 1/2-1/2', t)
                self.expect('drawn by repetition} 1/2-1/2', t2)
                #t.write('abort\n')
                #t2.write('abort\n')
                #self.expect('Game aborted', t)
                #self.expect('Game aborted', t2)
            elif g.result == '1/2-1/2' and g.is_fifty:
                # probably never happens
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

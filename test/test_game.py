from test import *

from pgn import Pgn

class TestGame(Test):
    def test_game_basics(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t2.write('e7e5\n')
        self.expect('not your move', t2)

        # plain illegal move
        t.write('e2e5\n')
        self.expect('Illegal move (e2e5)', t)
        
        t.write('e7e5\n')
        self.expect('Illegal move (e7e5)', t)
        
        t.write('e3e4\n')
        self.expect('Illegal move (e3e4)', t)

        # square occpied by own piece
        t.write('a1a2\n')
        self.expect('Illegal move (a1a2)', t)
       
        # path blocked by own piece
        t.write('a1a3\n')
        self.expect('Illegal move (a1a3)', t)

        # legal move
        t.write('e2e4\n')
        self.expect_not('Illegal move', t)
        
        t2.write('e7e5\n')
        self.expect_not('Illegal move', t2)
        
        t.write('g1f3\n')
        self.expect_not('Illegal move', t)
        
        t2.write('b8c6\n')
        self.expect_not('Illegal move', t2)
       
        # castling blocked
        t.write('O-O\n')
        self.expect('Illegal move', t)
        t.write('O-O-O\n')
        self.expect('Illegal move', t)
        
        t.write('f1c4\n')
        self.expect_not('Illegal move', t2)
        
        t2.write('g8f6\n')
        self.expect_not('Illegal move', t2)
        
        t.write('O-O\n')
        self.expect_not('Illegal move', t2)

        self.close(t)
        self.close(t2)
    

    def test_san(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        
        t.write('e5\n')
        self.expect('Illegal move', t)

        t.write('e4\n')
        self.expect_not('Illegal move', t)

        self.close(t)
        self.close(t2)
    
    def test_games(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        
        f = open('../data/test1.pgn', 'r')

        pgn = Pgn(f.read())
        for g in pgn.games:
            print 'game %s' % g
            t.write('match admin white 1 0\n')
            self.expect('Issuing:', t)
            self.expect('Challenge:', t2)
            t2.write('accept\n')
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
    
            wtm = True
            for mv in g.moves:                
                if wtm:
                    #print 'sending %s to white' % mv.text
                    t.write('%s\n' % mv.text)
                else:
                    #print 'sending %s to black' % mv.text
                    t2.write('%s\n' % mv.text)
                self.expect('<12> ', t)
                self.expect('<12> ', t2)
                wtm = not wtm 
        
            if g.result == '1-0' and g.is_checkmate:
                self.expect('admin checkmated} 1-0', t)
                self.expect('admin checkmated} 1-0', t2)
            elif g.result == '0-1' and g.is_checkmate:
                self.expect('GuestABCD checkmated} 0-1', t)
                self.expect('GuestABCD checkmated} 0-1', t2)
            elif g.result == '1/2-1/2' and g.is_stalemate:
                self.expect('drawn by stalemate} 1/2-1/2', t)
                self.expect('drawn by stalemate} 1/2-1/2', t2)
            elif g.result == '1/2-1/2' and g.is_draw_nomaterial:
                self.expect('neither player has mating material} 1/2-1/2', t)
                self.expect('neither player has mating material} 1/2-1/2', t2)
            else:
                t.write('abort\n')
                t2.write('abort\n')
                self.expect('Game aborted', t)
                self.expect('Game aborted', t2)

        self.close(t)
        self.close(t2)

class TestAbort(Test):
    def test_abort_ply_0(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.write('abort\n')
        self.expect('Game aborted on move 1 by Guest', t)
        self.expect('Game aborted on move 1 by Guest', t2)

        self.close(t)
        self.close(t2)
    
    def test_abort_ply_1(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.write('e4\n')
        self.expect('P/e2-e4', t2)
        t2.write('abort\n')
        self.expect('Game aborted on move 1 by admin', t)
        self.expect('Game aborted on move 1 by admin', t2)

        self.close(t)
        self.close(t2)
    
    def test_abort_agreement(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.write('e4\n')
        t2.write('e5\n')
        t.write('abort\n')

        self.expect('requests to abort the game', t2)

        t2.write('abort\n')
        self.expect('Game aborted by agreement', t)
        self.expect('Game aborted by agreement', t2)

        self.close(t)
        self.close(t2)
        
# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

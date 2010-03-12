from test import *

class TestGame(Test):
    def test_game_basics(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: GuestABCD (++++) admin (----) unrated lightning 1 0', t)
        self.expect('Creating: GuestABCD (++++) admin (----) unrated lightning 1 0', t2)

        self.expect('{Game 1 (GuestABCD vs. admin) Creating unrated lightning match.}', t)
        self.expect('{Game 1 (GuestABCD vs. admin) Creating unrated lightning match.}', t2)

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
    
class TestResign(Test):
    def test_resign_white(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.write('resign\n')
        self.expect('{Game 1 (GuestABCD vs. admin) GuestABCD resigns} 0-1', t)
        self.expect('{Game 1 (GuestABCD vs. admin) GuestABCD resigns} 0-1', t2)
        self.close(t)
        self.close(t2)
    
    def test_resign_black(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t2.write('resign\n')
        self.expect('{Game 1 (GuestABCD vs. admin) admin resigns} 1-0', t)
        self.expect('{Game 1 (GuestABCD vs. admin) admin resigns} 1-0', t2)
        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

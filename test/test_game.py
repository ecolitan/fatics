from test import *

class TestGame(Test):
    def test_game(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        
        t.write('match admin white\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t2.write('e7e5\n')
        self.expect('not your move', t2)

        t.write('e2e5\n')
        self.expect('Illegal move (e2e5)', t)
        
        t.write('a1a2\n')
        self.expect('Illegal move (a1a2)', t)
        
        t.write('a1a3\n')
        self.expect('Illegal move (a1a3)', t)
        
        t.write('c1b2\n')
        self.expect('Illegal move (c1b2)', t)
        
        t.write('e2e4\n')
        self.expect_not('Illegal move', t)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

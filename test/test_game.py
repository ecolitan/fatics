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
    
    def test_lalg(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()

        t.write('match admin white 1 0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        moves = ['g2g3', 'b7b6', 'f1g2', 'b8c6', 'g1f3', 'c8b7', 'e1g1',
            'e7e6', 'd2d4', 'd8e7', 'c1f4', 'e8c8']
    
        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm
        t.write('abort\n')
        t2.write('abort\n')

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
    
    def test_draw_repetition(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        moves = ['Nf3', 'Nf6', 'Ng1', 'Ng8', 'Nf3', 'Nf6',
            'Ng1', 'Ng8']
    
        wtm = True
        for mv in moves:
            if wtm:
                #print 'sending %s to white' % mv.text
                t.write('%s\n' % mv)
            else:
                #print 'sending %s to black' % mv.text
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm 

        t.write('draw\n')
        self.expect('{Game 1 (GuestABCD vs. admin) Game drawn by repetition} 1/2-1/2', t)
        self.expect('{Game 1 (GuestABCD vs. admin) Game drawn by repetition} 1/2-1/2', t2)

        self.close(t)
        self.close(t2)
    
    def test_draw_repetition_claim_later(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        moves = ['Nf3', 'Nf6', 'd3', 'Nc6', 'Nc3', 'Nb8', 'Nb1', 'Nc6',
            'Nc3', 'Nb8', 'Nb1', 'Ne4']
    
        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm 

        # Old fics allows either white or black to claim a draw here.
        # We only allow white to claim a draw; black should have
        # claimed it before he or she moved.
        t.write('draw\n')
        self.expect('{Game 1 (GuestABCD vs. admin) Game drawn by repetition} 1/2-1/2', t)
        self.expect('{Game 1 (GuestABCD vs. admin) Game drawn by repetition} 1/2-1/2', t2)

        self.close(t)
        self.close(t2)
    
    def test_draw_repetition_claim_too_late(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        moves = ['Nf3', 'Nf6', 'd3', 'Nc6', 'Nc3', 'Nb8', 'Nb1', 'Nc6',
            'Nc3', 'Nb8', 'Nb1', 'Ne4']
    
        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm 

        t2.write('draw\n')
        # see note in test_draw_repetition_claim_later()
        self.expect('Offering a draw', t2)
        self.expect_not('drawn by repetition', t)

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

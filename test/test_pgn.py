import random

from test import *

from pgn import Pgn

class TestPgn(Test):
    def test_pgn(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_user('GuestEFGH', '')

        t.write('set style 12\n')
        t2.write('set style 12\n')

        f = open('../data/test.pgn', 'r')
        #f = open('../data/draw.pgn', 'r')
        #f = open('/home/wmahan/chess/fics-2009-12.pgn', 'r')

        pgn = Pgn(f)
        for g in pgn:
            print 'game %s' % g
            t.write('match GuestEFGH white 1 0\n')
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
                random.choice([t, t2]).write('draw\n')
                self.expect('drawn by the 50 move rule} 1/2-1/2', t)
                self.expect('drawn by the 50 move rule} 1/2-1/2', t2)
            else:
                t.write('abort\n')
                t2.write('abort\n')
                self.expect('Game aborted', t)
                self.expect('Game aborted', t2)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

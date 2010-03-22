# coding=utf-8

from test import *

class TestEco(Test):
    def test_eco(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        moves = ['d4', 'd5', 'e4', 'dxe4', 'Nc3', 'Bd7']
    
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

        t.write('eco\n')
        self.expect('Eco for game 1 (GuestABCD vs. admin):', t)
        self.expect(' ECO[   ]: D00l', t)
        self.expect('LONG[   ]: Blackmar-Diemer: Grosshans Defence', t)

        self.close(t)
        self.close(t2)
    
    def test_eco_utf8(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        moves = ['e4', 'e6', 'd4', 'd5', 'Nc3', 'Bb4', 'Bd2']
    
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

        t.write('eco\n')
        self.expect('Eco for game 1 (GuestABCD vs. admin):', t)
        self.expect(' ECO[   ]: C15h', t)
        self.expect('LONG[   ]: French: Winawer, Müller-Zhuravlev Gambit', t)
        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

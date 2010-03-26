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
        self.expect(' ECO[  6]: D00l', t)
        self.expect(' NIC[  2]: QP.08', t)
        self.expect('LONG[  6]: Blackmar-Diemer: Grosshans Defence', t)

        self.close(t)
        self.close(t2)

    def test_eco_out_of_book(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        moves = ['e4', 'd5', 'Qg4']
    
        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm 

        t.write('eco\n')
        self.expect('Eco for game 1 (GuestABCD vs. admin):', t)
        self.expect(' ECO[  2]: B01a', t)
        self.expect(' NIC[  1]: VO.17', t)
        self.expect('LONG[  2]: Scandinavian (Centre Counter)', t)

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
                t.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t)
            self.expect('<12> ', t2)
            wtm = not wtm 

        t.write('eco\n')
        self.expect('Eco for game 1 (GuestABCD vs. admin):', t)
        self.expect(' ECO[  7]: C15h', t)
        self.expect(' NIC[  6]: FR.08', t)
        self.expect('LONG[  7]: French: Winawer, Müller-Zhuravlev Gambit', t)
        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

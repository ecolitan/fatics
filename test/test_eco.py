# coding=utf-8

from test import *

class TestEco(Test):
    def test_eco(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()

        t.write('eco\n')
        self.expect('You are not playing, examining, or observing a game.', t)

        t.write('eco admin\n')
        self.expect('admin is not playing or examining a game.', t)

        t.write('eco testplayer\n')
        self.expect('No user named "testplayer" is logged in.', t)

        t.write('eco 100\n')
        self.expect('There is no such game.', t)

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

        t.write('eco 1\n')
        self.expect('Eco for game 1 (GuestABCD vs. admin):', t)
        self.expect(' ECO[  6]: D00l', t)
        self.expect(' NIC[  2]: QP.08', t)
        self.expect('LONG[  6]: Blackmar-Diemer: Grosshans Defence', t)

        t.write('eco admin\n')
        self.expect('Eco for game 1 (GuestABCD vs. admin):', t)
        self.expect(' ECO[  6]: D00l', t)
        self.expect(' NIC[  2]: QP.08', t)
        self.expect('LONG[  6]: Blackmar-Diemer: Grosshans Defence', t)

        self.close(t)
        self.close(t2)

    def test_eco_search(self):
        t = self.connect_as_guest()

        t.write('eco n\n')
        self.expect('No user named "n" is logged in', t)
        t.write('eco e\n')
        self.expect('No user named "e" is logged in', t)
        t.write('eco a b\n')
        self.expect('Usage:', t)
        t.write('eco A00\n')
        self.expect('"a00" is not a valid handle', t)
        t.write('eco e a0\n')
        self.expect("You haven't specified a valid ECO code", t)
        t.write('eco n si\n')
        self.expect("You haven't specified a valid NIC code", t)

        t.write('eco e a98\n')
        self.expect('  ECO: A98\r\n  NIC: -----\r\n LONG: Dutch: Ilyin-Zhenevsky, 8.Qc2\r\n  FEN: rnb1qrk1/ppp1b1pp/3ppn2/5p2/2PP4/2N2NP1/PPQ1PPBP/R1B2RK1 b - -\r\n\r\n  ECO: A98\r\n  NIC: -----\r\n LONG: Dutch: Ilyin-Zhenevsky, 8.Qc2 Nc6\r\n  FEN: r1b1qrk1/ppp1b1pp/2nppn2/5p2/2PP4/2N2NP1/PPQ1PPBP/R1B2RK1 w - -\r\n\r\n  ECO: A98\r\n  NIC: -----\r\n LONG: Dutch: Ilyin-Zhenevsky, 8.Qc2 Qh5\r\n  FEN: rnb2rk1/ppp1b1pp/3ppn2/5p1q/2PP4/2N2NP1/PPQ1PPBP/R1B2RK1 w - -', t)

        t.write('eco n VO.11\n')
        self.expect('  ECO: A00n\r\n  NIC: VO.11\r\n LONG: Grob\r\n  FEN: rnbqkbnr/pppppppp/8/8/6P1/8/PPPPPP1P/RNBQKBNR b KQkq -', t)

        self.close(t)

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

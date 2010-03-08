from test import *

class TestStyle12(Test):
    def test_style12(self):
        self.adduser('testplayer', 'testpass')
        t = self.connect_as_user('testplayer', 'testpass')
        t2 = self.connect_as_admin()
        
        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        #<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 270 GuestJJCG Chessstyles 1 1 0 39 39 60000 60000 1 none (0:00.000) none 0 0 0
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 60000 60000 1 none (0:00.000) none 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60000 60000 1 none (0:00.000) none 0 0 0', t2)

        t.write('d4\n')

        #<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B 3 1 1 1 1 0 270 GuestJJCG Chessstyles -1 1 0 39 39 60000 60000 1 P/d2-d4 (0:00.000) d4 0 0 0
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B 3 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60000 60000 1 P/d2-d4 (0:00.000) d4 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B 3 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 60000 60000 1 P/d2-d4 (0:00.000) d4 0 0 0', t2)

        self.close(t)
        self.close(t2)

        self.deluser('testplayer')


        #<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B 3 1 1 1 1 0 270 GuestJJCG Chessstyles -1 1 0 39 39 60000 60000 1 P/d2-d4 (0:00.000) d4 0 0 0

        #<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W 3 1 1 1 1 0 270 GuestJJCG Chessstyles 1 1 0 39 39 60000 60000 2 P/d7-d5 (0:00.000) d5 0 1 0

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

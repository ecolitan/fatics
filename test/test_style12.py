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

        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 60 60 1 none (0:00.000) none 0 0 0\r\n', t)
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60 60 1 none (0:00.000) none 1 0 0\r\n', t2)

        t.write('d4\n')

        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B 3 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60 60 1 P/d2-d4 (0:00.000) d4 0 0 0\r\n', t)
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B 3 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 60 60 1 P/d2-d4 (0:00.000) d4 1 0 0\r\n', t2)
        
        t2.write('d5\n')
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W 3 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 60 60 2 P/d7-d5 (0:00.000) d5 0 1 0\r\n', t)
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W 3 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60 60 2 P/d7-d5 (0:00.000) d5 1 1 0\r\n', t2)

        self.close(t)
        self.close(t2)

        self.deluser('testplayer')



# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

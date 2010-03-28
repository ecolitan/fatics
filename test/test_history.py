from test import *

class TestHistory(Test):
    def test_history_guest(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_user('GuestEFGH', '')
        t.write('match GuestEFGH 2 12 white u\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')

        self.expect('Creating:', t)
        self.expect('Creating:', t2)
        t.write('e4\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        t2.write('c5\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        t.write('resign\n')

        self.expect('GuestABCD resigns', t)
        self.expect('GuestABCD resigns', t2)

        t.write('history\n')
        self.expect('History for GuestABCD:\r\n                  Opponent      Type         ECO End Date', t)
        self.expect(' 1: - ++++ W ++++ GuestEFGH     [bnu  2  12] B20 Res ', t)
        
        t2.write('hi\n')
        self.expect('History for GuestEFGH:\r\n                  Opponent      Type         ECO End Date', t2)
        self.expect(' 1: + ++++ B ++++ GuestABCD     [bnu  2  12] B20 Res ', t2)

        t.write('hi GuestEFGH\n')
        self.expect('History for GuestEFGH:\r\n                  Opponent      Type         ECO End Date', t)
        self.expect(' 1: + ++++ B ++++ GuestABCD     [bnu  2  12] B20 Res ', t)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

from test import *

class TestDate(Test):
    def test_date(self):
        t = self.connect_as_guest()
        t.write('date\n')
        self.expect('Server time', t, "date")
        self.expect('GMT', t, "date")
        t.close()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

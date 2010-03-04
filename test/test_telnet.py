from test import *

class TelnetTest(Test):
    def test_telnet(self):
        t = self.connect()
        t.read_until('fics%', 2)
        os.write(t.fileno(), chr(255) + chr(244))
        self.expect_EOF(t, "interrupt connection")
        t.close()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

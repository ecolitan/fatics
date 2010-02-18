from test import *

class TelnetTest(Test):
        def testTelnet(self):
                t = self.connect()
                t.read_until('fics%', 2)
                os.write(t.fileno(), chr(255) + chr(244))
                self.expect_EOF(t, "interrupt connection")
                t.close()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

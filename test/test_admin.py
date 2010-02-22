from test import *

class AddplayerTest(Test):
        def test_addplayer(self):
                t = self.connect_as_admin()
                t.write('addplayer testplayer nobody@example.com Foo Bar\r\n')
                self.expect('Added:', t, 'addplayer')
                t.write('addplayer testplayer nobody@example.com Foo Bar\r\n')
                self.expect('already registered', t, 'addplayer duplicate player')
                t.write('remplayer testplayer\r\n')
                t.close()

class AnnounceTest(Test):
        def test_announce(self):
                t = self.connect_as_admin()
                t2 = self.connect_as_guest()

                t.write("announce foo bar baz\r\n")
                self.expect('(1) **ANNOUNCEMENT** from admin: foo bar baz', t)
                self.expect('**ANNOUNCEMENT** from admin: foo bar baz', t2)

"""not stable
class AreloadTest(Test):
        def runTest(self):
                self.skip()
                t = self.connect()
                t.write('areload\r\n')
                self.expect('reloaded online', t, "server reload")
                t.close()
"""

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

#from twisted.trial import unittest
from test import *

class TellTest(Test):
        def testTell(self):
                t = self.connect_as_admin()
                t.write('tell admin Hello!\r\n')
                self.expect('admin(*) tells you: Hello!', t, "tell self")

               
                t2 = self.connect_as_guest()
                t2.write('tell admin Guest tell\r\n')
                self.expect('(U) tells you: Guest tell\r\n', t, 'guest tell')
                t2.close()

                t.close()


# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

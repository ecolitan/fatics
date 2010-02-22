#from twisted.trial import unittest
from test import *

class TellTest(Test):
        def test_tell(self):
                t = self.connect_as_admin()
                t.write('tell admin Hello there!\n')
                self.expect('admin(*) tells you: Hello there!', t, "tell self")

               
                t2 = self.connect_as_guest()
                t2.write('tell admin Guest tell\n')
                self.expect('(U) tells you: Guest tell', t, 'guest tell')
                self.close(t2)

                self.close(t)
        
        def test_bad_tell(self):
                t = self.connect_as_guest()
                t.write('tell nonexistentname foo\n')
                self.expect('There is no player matching', t)
                
                t.write('tell admin foo\n')
                self.expect('is not logged in', t)

                t.write('tell admin1 too\n')
                self.expect('not a valid handle', t)

                self.close(t)


class QtellTest(Test):
        def test_qtell(self):
                self.adduser('tdplayer', 'tdplayer', ['td'])
                t = self.connect_as_user('tdplayer', 'tdplayer')
                t.write('qtell nonexistentname test\n')
                self.expect('*qtell nonexistentname 1*', t)
                
                t2 = self.connect_as_admin()
                t.write('qtell admin simple test\n')
                self.expect(':simple test', t2)
                self.expect('*qtell admin 0*', t)
                
                t.write('qtell admin \\bthis\\nis a \\Hmore complicated\\h test\n')
                self.expect(':\x07this', t2)
                self.expect(':is a \x1b[7mmore complicated\x1b[0m test', t2)
                self.expect('*qtell admin 0*', t)
                
                self.close(t2)
                self.close(t)
                self.deluser('tdplayer')

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

from test import *

class TestLang(Test):
    def test_lang_guest(self):
        t = self.connect_as_guest()
        t.write("who\n")
        self.expect("1 player displayed", t)
        
        t.write('set lang arst\n')
        self.expect('Bad value', t)

        t.write('set lang compat\n')
        t.write("who\n")
        self.expect("1 Players Displayed.", t)

        self.close(t)
    
    def test_lang_admin(self):
        t = self.connect_as_admin()
        t.write('set lang en\n')
        t.write("who\n")
        self.expect("1 player displayed", t)
        t.write('set lang compat\n')
        self.close(t)

        t = self.connect_as_admin()
        t.write("who\n")
        self.expect("1 Players Displayed.", t)

        t2 = self.connect_as_guest()
        t2.write("who\n")
        self.expect("2 players displayed.", t2)
        self.close(t2)

        t.write('set lang en\n')
        self.close(t)
        
# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

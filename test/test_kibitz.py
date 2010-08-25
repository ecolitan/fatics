from test import *

class TestKibitz(Test):
    def test_kibitz(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_admin()
        t3 = self.connect_as_guest()

        t.write('kibitz hello\n')
        self.expect('You are not playing, examining, or observing a game', t)

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        t3.write('o 1\n')
        self.expect('now observing game 1', t3)


        t.write("kibitz This is a test kibitz!\n")
        self.expect('GuestABCD(U)(++++)[1] kibitzes: This is a test kibitz!', t)
        self.expect('GuestABCD(U)(++++)[1] kibitzes: This is a test kibitz!', t2)
        self.expect('GuestABCD(U)(++++)[1] kibitzes: This is a test kibitz!', t3)
        self.expect('(kibitzed to 2 players)', t)


        t.write('set kibitz 0\n')
        self.expect('You will not hear kibitzes', t)
        t2.write("kibitz Another test...\n")
        self.expect('admin(*)(----)[1] kibitzes: Another test...', t2)
        self.expect('admin(*)(----)[1] kibitzes: Another test...', t3)
        self.expect_not('admin(*)(----)[1] kibitzes: Another test...', t)
        self.expect('(kibitzed to 1 player)', t2)

        t.write('set kibitz 1\n')
        self.expect('You will now hear kibitzes', t)
        t3.write("kibitz Third-party kib\n")
        self.expect('(++++)[1] kibitzes: Third-party kib', t)
        self.expect('(++++)[1] kibitzes: Third-party kib', t2)
        self.expect('(++++)[1] kibitzes: Third-party kib', t3)
        self.expect('(kibitzed to 2 players)', t3)

        t.write('abort\n')
        t2.write('abort\n')

        self.close(t)
        self.close(t2)
        self.close(t3)

    def test_kiblevel(self):
        t = self.connect_as_user('GuestEFGH', '')
        t2 = self.connect_as_admin()

        t2.write('asetrating admin lightning normal 0 0 0 0 0 0\n')
        self.expect('Cleared lightning normal rating for admin.', t2)

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.write('set kiblevel 1000\n')
        self.expect('kiblevel set to 1000.', t)
        t2.write('ki .\n')
        self.expect('(kibitzed to 0 players)', t2)
        t2.write('asetrating admin lightning normal 1001 350 .01 0 0 0\n')
        self.expect('Set lightning normal rating for admin.', t2)
        t2.write('ki .\n')
        self.expect('admin(*)(1001)[1] kibitzes: .', t)
        self.expect('admin(*)(1001)[1] kibitzes: .', t2)
        self.expect('(kibitzed to 1 player)', t2)

        t.write('abort\n')
        t2.write('abort\n')

        t2.write('asetrating admin lightning normal 0 0 0 0 0 0\n')
        self.expect('Cleared lightning normal rating for admin.', t2)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

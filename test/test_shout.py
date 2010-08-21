from test import *

class TestShout(Test):
    def test_shout(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()
        t3 = self.connect_as_guest()

        t.write('set shout 1\n')
        t.read_until('fics%', 2)
        t2.write('set shout 1\n')
        t2.read_until('fics%', 2)
        t3.write('set shout 0\n')
        t3.read_until('fics%', 2)

        t.write('shout test shout\n')
        self.expect("shouts: test shout", t)
        self.expect("shouts: test shout", t2)
        self.expect("(shouted to 2 players)", t)
        self.close(t)
        self.close(t2)
        self.close(t3)

    def test_guest_shout(self):
        t = self.connect_as_guest()
        t.write('shout test shout\n')
        self.expect("Only registered players can use the shout command.", t)
        self.close(t)

    def test_shout_not_listening(self):
        t = self.connect_as_admin()
        t.write('set shout 0\n')
        t.write('shout test shout\n')
        self.expect("not listening", t)
        t.write('set shout 1\n')
        self.close(t)

class TestCshout(Test):
    def test_cshout(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()
        t3 = self.connect_as_guest()

        t.write('set cshout 1\n')
        t.read_until('fics%', 2)
        t2.write('set cshout 1\n')
        t2.read_until('fics%', 2)
        t3.write('set cshout 0\n')
        t3.read_until('fics%', 2)

        t.write('cshout test cshout\n')
        self.expect("c-shouts: test cshout", t)
        self.expect("c-shouts: test cshout", t2)
        self.expect("(c-shouted to 2 players)", t)
        self.close(t)
        self.close(t2)
        self.close(t3)

    def test_guest_cshout(self):
        t = self.connect_as_guest()
        t.write('cshout test cshout\n')
        self.expect("Only registered players can use the cshout command.", t)
        self.close(t)

    def test_cshout_not_listening(self):
        t = self.connect_as_admin()
        t.write('set cshout 0\n')
        t.write('cshout test cshout\n')
        self.expect("not listening", t)
        t.write('set cshout 1\n')
        self.close(t)

class TestIt(Test):
    def test_it(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()

        t2.write('it is testing\n')
        self.expect('Only registered players', t2)

        t.write('it is testing\n')
        self.expect('--> admin(*) is testing\r\n', t)
        self.expect('--> admin(*) is testing\r\n', t2)
        self.expect('(it-shouted to 2 players)\r\n', t)

        t2.write('set shout 0\n')
        t.write('it is testing\n')
        self.expect('(it-shouted to 1 player)\r\n', t)
        self.expect_not('is testing', t2)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

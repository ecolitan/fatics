from test import *

class TestShout(Test):
    def test_shout(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()
        t3 = self.connect_as_guest()

        t.write('set shout 1\r\n')
        t.read_until('fics%', 2)
        t2.write('set shout 1\r\n')
        t2.read_until('fics%', 2)
        t3.write('set shout 0\r\n')
        t3.read_until('fics%', 2)

        t.write('shout test shout\r\n')
        self.expect("shouts: test shout", t)
        self.expect("shouts: test shout", t2)
        self.expect("(shouted to 2", t)
        self.close(t)
        self.close(t2)
        self.close(t3)

    def test_guest_shout(self):
        t = self.connect_as_guest()
        t.write('shout test shout\r\n')
        self.expect("Only registered players can use the shout command.", t)
        self.close(t)

    def test_shout_not_listening(self):
        t = self.connect_as_admin()
        t.write('set shout 0\r\n')
        t.write('shout test shout\r\n')
        self.expect("not listening", t)
        t.write('set shout 1\r\n')
        self.close(t)

class TestCshout(Test):
    def test_cshout(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()
        t3 = self.connect_as_guest()

        t.write('set cshout 1\r\n')
        t.read_until('fics%', 2)
        t2.write('set cshout 1\r\n')
        t2.read_until('fics%', 2)
        t3.write('set cshout 0\r\n')
        t3.read_until('fics%', 2)

        t.write('cshout test cshout\r\n')
        self.expect("c-shouts: test cshout", t)
        self.expect("c-shouts: test cshout", t2)
        self.expect("(c-shouted to 2", t)
        self.close(t)
        self.close(t2)
        self.close(t3)

    def test_guest_cshout(self):
        t = self.connect_as_guest()
        t.write('cshout test cshout\r\n')
        self.expect("Only registered players can use the cshout command.", t)
        self.close(t)

    def test_cshout_not_listening(self):
        t = self.connect_as_admin()
        t.write('set cshout 0\r\n')
        t.write('cshout test cshout\r\n')
        self.expect("not listening", t)
        t.write('set cshout 1\r\n')
        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

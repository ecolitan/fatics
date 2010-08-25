import sys
import telnetlib
import socket
import os
from twisted.trial import unittest

host = '127.0.0.1'
port = '5000'
admin_passwd = 'admin'

sys.path.append('src/')

def connect():
    try:
        t = telnetlib.Telnet(host, port, 120)
    except socket.gaierror:
        t = None
    except socket.error:
        t = None
    return t

class Test(unittest.TestCase):
    def expect(self, s, t, msg=None, timeout=2):
        ret = t.read_until(s, timeout)
        if not s in ret:
            print("\ngot {{%s}}\nexp {{%s}}\n" % (repr(ret), repr(s)))
        self.assert_(s in ret)

    def expect_re(self, s, t, timeout=2):
        ret = t.expect([s], timeout)
        self.assert_(ret[0] == 0)
        return ret[1]

    def expect_command_prints_nothing(self, cmd, t, timeout=0.2):
        t.read_very_eager()
        t.write(cmd)
        ret = t.read_until('foo', timeout)
        if ret != 'fics% ':
            print("\ngot {{%s}}" % repr(ret))
        self.assert_(ret == 'fics% ')

    def expect_not(self, str, t):
        ret = t.read_until(str, 0.3)
        if str in ret:
            print "got {{%s}}" % (ret + t.read_lazy())
        self.assert_(not str in ret)

    def expect_EOF(self, t, msg):
        def read_some(unused):
            t.read_very_eager()
            t.read_until('not-seen', 2)
        self.assertRaises(EOFError, read_some, msg)

    def connect(self):
        return connect()

    def connect_as_guest(self):
        t = connect()
        t.write("guest\n\n")
        t.read_until('fics%', 5)
        return t

    def connect_as_admin(self):
        t = connect()
        t.write("admin\n%s\n" % admin_passwd)
        s = t.read_until('fics%', 5)
        assert('fics%' in s)
        return t

    def connect_as_user(self, name, passwd):
        t = connect()
        t.write("%s\n%s\n" % (name, passwd))
        s = t.read_until('fics%', 5)
        assert('fics%' in s)
        return t

    def close(self, t):
        t.write('quit\n')
        t.read_until('Thank you for using')
        t.close()

    def adduser(self, name, passwd, lists=None):
        t = self.connect_as_admin()
        t.write('addplayer %s fakeemail@example.com Test Player\n' % name)
        t.write('asetpass %s %s\n' % (name, passwd))
        if lists:
            for lname in lists:
                t.write('addlist %s %s\n' % (lname, name))
        self.close(t)

    def deluser(self, name):
        t = self.connect_as_admin()
        t.write('remplayer %s\n' % name)
        self.close(t)

class OneConnectionTest(Test):
    def setUp(self):
        self.t = self.connect()

    def tearDown(self):
        self.t.close()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

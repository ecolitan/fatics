import sys
import telnetlib
import socket
import os
from twisted.trial import unittest

host = '127.0.0.1'
port = '5001'
admin_passwd = 'admin'

def connect():
        try:
                t = telnetlib.Telnet(host, port, 120)
        except socket.gaierror:
                t = None
        except socket.error:
                t = None
        return t

class Test(unittest.TestCase):
        def expect(self, str, t, msg=None, timeout=2):
                ret = t.read_until(str, timeout)
                if not str in ret:
                        print "got {{%s}}" % ret
                self.assert_(str in ret)
        
        def expect_not(self, str, t):
                ret = t.read_until(str, 0.3)
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
                t.read_until('fics%', 2)
                return t
        
        def connect_as_admin(self):
                t = connect()
                t.write("admin\n%s\n" % admin_passwd)
                t.read_until('fics%', 6)
                return t
        
        def connect_as_user(self, name, passwd):
                t = connect()
                t.write("%s\n%s\n" % (name, passwd))
                t.read_until('fics%', 6)
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

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent

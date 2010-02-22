import sys
import telnetlib
import socket
import os
from twisted.trial import unittest

host = 'localhost'
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
        
        def expect_EOF(self, t, msg):
                def read_some(unused):
                        t.read_very_eager()
                        t.read_until('not-seen', 2)
                self.assertRaises(EOFError, read_some, msg)

        def connect(self):
                return connect()
        
        def connect_as_guest(self):
                t = connect()
                t.write("guest\r\n\r\n")
                t.read_until('fics%', 2)
                return t
        
        def connect_as_admin(self):
                t = connect()
                t.write("admin\r\n%s\r\n" % admin_passwd)
                t.read_until('fics%', 6)
                return t

        def close(self, t):
                t.write('quit\r\n')
                t.read_until('Thank you for using')
                t.close()

class OneConnectionTest(Test):
        def setUp(self):
                self.t = self.connect()

        def tearDown(self):
                self.t.close()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

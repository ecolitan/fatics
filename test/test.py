# Copyright (C) 2010  Wil Mahan <wmahan+fatics@gmail.com>
#
# This file is part of FatICS.
#
# FatICS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FatICS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with FatICS.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import telnetlib
import socket
import os
import re

from twisted.trial import unittest

host = '127.0.0.1'
#host = 'sheila'
port = '5000'
admin_passwd = 'admin'
LOCAL_IP = '127.0.0.1'

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
        ret = t.expect([re.compile(s)], timeout)
        if ret[0] != 0:
            print("\ngot {{%r}}\nexp {{%r}}\n" % (ret, s))
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

    def expect_EOF(self, t):
        def read_some():
            t.read_very_eager()
            t.read_until('not-seen', 2)
        self.assertRaises(EOFError, read_some)

    def connect(self):
        return connect()

    def connect_as_guest(self, name=None):
        t = connect()
        if name:
            t.write("%s\n" % name)
            self.expect('is not a registered name', t)
            t.write('\n')
        else:
            t.write("guest\n\n")
        t.read_until('fics%', 5)
        return t

    def connect_as_admin(self):
        t = connect()
        t.write("admin\n%s\n" % admin_passwd)
        s = t.read_until('fics%', 5)
        assert('fics%' in s)
        return t

    def connect_as(self, name, passwd):
        t = connect()
        t.write('%s\n' % name)
        self.expect('is a registered name', t)
        t.write('%s\n' % passwd)
        s = t.read_until('fics%', 5)
        assert('fics%' in s)
        return t

    def close(self, t):
        t.write('quit\n')
        t.read_until('Thank you for using')
        t.read_all()
        t.close()

    def adduser(self, name, passwd, lists=None):
        t = self.connect_as_admin()
        t.write('addplayer %s fakeemail@example.com Test Player\n' % name)
        self.expect('Added: ', t)
        t.write('asetpass %s %s\n' % (name, passwd))
        if lists:
            for lname in lists:
                t.write('addlist %s %s\n' % (lname, name))
        self.close(t)

    def deluser(self, name):
        t = self.connect_as_admin()
        t.write('remplayer %s\n' % name)
        self.expect('removed', t)
        self.close(t)

    def _skip(self, reason):
        raise unittest.SkipTest(reason)


# test decorators
"""def with_guest(f):
    def new_f(self):
        t = self.connect_as_guest()
        f(self, t)
        self.close(t)

    new_f.__name__ = f.__name__
    new_f.__dict__.update(f.__dict__)
    return new_f

def with_admin(f):
    def new_f(self):
        t = self.connect_as_admin()
        f(self, t)
        self.close(t)

    new_f.__name__ = f.__name__
    new_f.__dict__.update(f.__dict__)
    return new_f"""

def with_player(pname, ppass, ptitles=None):
    def wrap(f):
        def new_f(self):
            self.adduser(pname, ppass, ptitles)
            try:
                f(self)
            finally:
                try:
                    self.deluser(pname)
                except:
                    pass
        new_f.__name__ = f.__name__
        new_f.__dict__.update(f.__dict__)
        return new_f
    return wrap

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

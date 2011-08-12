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
import re
import random
import string

from twisted.trial import unittest

LOCAL_IP = '127.0.0.1'

sys.path.append('src/')

from local_config import admin_passwd, host, port


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
        if s not in ret:
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
            t.read_until('not-seen', 1)
            t.read_very_eager()
        self.assertRaises(EOFError, read_some)
        t.close()

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
        s = t.read_until('fics% ', 5)
        if 'fics%' not in s:
            print 'got {%s}' % s
        self.assert_('fics% ' in s)
        self.set_nowrap(t)
        return t

    def set_nowrap(self, t):
        """ Turn off line wrapping for a connection, to make messages
        in test cases more readable. """
        t.write('iset nowrap 1\n')
        self.expect('nowrap set.', t)

    def set_style_12(self, t):
        """ Set style 12 for a connection. """
        t.write('set style 12\n')
        self.expect('Style 12 set.', t)

    def connect_as(self, name, passwd=None):
        t = connect()
        t.write('%s\n' % name)
        self.expect('is a registered name', t)
        if passwd is None:
            passwd = tpasswd
        t.write('%s\n' % passwd)
        s = t.read_until('fics% ', 5)
        if 'fics%' not in s:
            print 'got {%s}' % s
        assert('fics% ' in s)
        return t

    def close(self, t):
        t.write('quit\n')
        t.read_until('Thank you for using')
        t.read_all()
        t.close()

    def _adduser(self, name, passwd, lists=[]):
        t = self.connect_as_admin()
        # in case the user already exists due to a failed test
        t.write('remplayer %s\n' % name)
        t.write('addplayer %s fakeemail@example.com Test Player\n' % name)
        self.expect('Added: ', t)
        t.write('asetpass %s %s\n' % (name, passwd))
        self.expect('Password of %s changed' % name, t)
        for lname in lists:
            t.write('addlist %s %s\n' % (lname, name))
            self.expect('added', t)
        self.close(t)

    def _deluser(self, name):
        t = self.connect_as_admin()
        #t.write('nuke %s\n' % name) # in case an error prevented clean logout
        t.write('remplayer %s\n' % name)
        self.expect('removed', t)
        self.close(t)

    def _skip(self, reason):
        raise unittest.SkipTest(reason)

    def setUp(self):
        pass

    def _nuke_all_players(self):
        try:
            t = self.connect_as_admin()
            t.write('who\n')
            # will have to be redone when 'who' output is finished
            while True:
                m = self.expect_re(r'^(.*?)\r\n', t)
                line = m.group(1)
                if line == '':
                    continue
                elif ' displayed.' in line:
                    break
                else:
                    m2 = re.match('^(\w+)(?:\(.*?\))*$', line)
                    self.assert_(m2)
                    name = m2.group(1)
                    if name != 'admin':
                        t.write('nuke %s\n' % name)
            self.close(t)
        except unittest.FailTest:
            # this is only called from within an exception handler, so
            # there's no need to raise another
            pass

    def tearDown(self):
        pass
        """ Make sure that all tests shut down cleanly. """
        """t = self.connect_as_guest('GuestWXYZ')
        t.write('who\n')
        try:
            self.expect('1 player displayed.', t)
        except unittest.FailTest:
            # The test left open connections lying around.
            # Nuke all players to give the remaining tests a clean
            # environment.
            self.close(t)
            self._nuke_all_players()
            raise

        self.close(t)"""

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

try:
    tpasswd
except NameError:
    tpasswd = (''.join(random.choice(string.letters + string.digits)
        for n in range(8)))
def with_player(pname, ptitles=[]):
    assert(isinstance (ptitles, (list, tuple)))
    def wrap(f):
        def new_f(self):
            self._adduser(pname, tpasswd, ptitles)
            try:
                f(self)
            finally:
                try:
                    self._deluser(pname)
                except:
                    pass
        new_f.__name__ = f.__name__
        new_f.__dict__.update(f.__dict__)
        return new_f
    return wrap

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

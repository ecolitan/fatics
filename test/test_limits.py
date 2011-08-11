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

from test import *

import random
import string

class TestMaxplayer(Test):
    # if we call this 50 times, the probability of a collision should be
    # approximately
    # 1 - ((26^8 - 1) / 26^8)^(50*49/2) = 5.9x10^-9
    def _random_name(self):
        name = []
        for i in range(8):
            name.append(random.choice(string.ascii_lowercase))
        return ''.join(name)

    def test_maxplayer(self):
        maxplayer = 50
        admin_reserve = 5
        names = []
        passwds = []

        t = self.connect_as_admin()

        t.write('who\n')
        # XXX we should probably not count admins
        m = self.expect_re(r'(\d+) players? displayed', t)
        user_count = int(m.group(1)) - 1

        t.write('asetmaxplayer %d\n' % maxplayer)
        self.expect('Total allowed connections: %d' % maxplayer, t)

        for i in range(0, maxplayer - user_count - admin_reserve):
            name = self._random_name()
            #print 'creating #%d: %s' % (i, name)
            names.append(name)
            t.write('addplayer %s nobody@example.com Test Player\n' % name)
            m = self.expect_re(r'Added: >.*?< >.*?< >.*?< >(.*?)<', t)
            passwds.append(m.group(1))

        self.close(t)

        conns = []

        for (name, passwd) in zip(names, passwds):
            #print('connecting as %s' % name)
            conns.append(self.connect_as(name, passwd))

        assert(len(conns) == len(names))

        t1 = self.connect()
        t1.write('g\n')
        self.expect('Sorry, the server has reached its limit for players', t1)
        self.expect_EOF(t1)

        # but an admin can still log in
        t = self.connect_as_admin()

        for (t2, name) in zip(conns, names):
            self.close(t2)
            t.write('remplayer %s\n' % name)
            self.expect('removed', t)

        self.close(t)

class TestMaxguest(Test):
    def test_maxguest(self):
        maxguest = 10

        t = self.connect_as_admin()

        # count guests already present
        t.write('annunreg Test please ignore\n')
        m = self.expect_re(r'\((\d+)\) ', t)
        guest_count = int(m.group(1))

        t.write('asetmaxguest %d\n' % maxguest)
        self.expect('Allowed guest connections: %d' % maxguest, t)
        self.close(t)

        conns = []
        for i in range(0, maxguest - guest_count):
            conns.append(self.connect_as_guest())

        t1 = self.connect()
        t1.write('g\n')
        self.expect('Sorry, the server has reached its limit for guests', t1)
        self.expect_EOF(t1)

        for t2 in conns:
            self.close(t2)

class TestLimitsCommand(Test):
    def test_limits(self):
        t = self.connect_as_guest()
        t.write("limits\n")
        self.expect("Current hardcoded limits:", t)
        self.expect("  Server:", t)
        self.expect("    Channels: ", t)
        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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

class TestBugwho(Test):
    def test_bugwho_none(self):
        t = self.connect_as_guest()

        t.write('bugwho foo\n')
        self.expect('Usage:', t)

        t.write('bugwho g\n')
        self.expect('Bughouse games in progress', t)
        self.expect(' 0 games displayed.', t)

        t.write('bugwho p\n')
        self.expect('Partnerships not playing bughouse', t)
        self.expect(' 0 partnerships displayed.', t)

        t.write('bugwho u\n')
        self.expect('Unpartnered players with bugopen on', t)
        self.expect('0 players displayed (of 1).', t)

        self.close(t)

    def test_bugwho(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')
        t3 = self.connect_as_guest('GuestIJKL')
        t4 = self.connect_as_guest('GuestMNOP')

        t.write('set bugopen 1\n')
        self.expect('You are now open for bughouse.', t)
        t2.write('set bugopen 1\n')
        self.expect('You are now open for bughouse.', t2)
        t3.write('set bugopen 1\n')
        self.expect('You are now open for bughouse.', t3)
        t4.write('set bugopen 1\n')
        self.expect('You are now open for bughouse.', t4)

        t.write('part guestefgh\n')
        self.expect('GuestABCD offers to be your bughouse partner.', t2)
        t2.write('a\n')
        self.expect('GuestEFGH accepts', t)

        t.write('bugwho\n')
        self.expect('Bughouse games in progress', t)
        self.expect(' 0 games displayed.', t)
        self.expect('Partnerships not playing bughouse', t)
        self.expect('++++ GuestABCD(U) / ++++ GuestEFGH(U)', t)
        self.expect(' 1 partnership displayed.', t)
        self.expect('Unpartnered players with bugopen on', t)
        self.expect('++++ GuestIJKL(U)\r\n++++ GuestMNOP(U)', t)
        self.expect('2 players displayed (of 4).', t)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

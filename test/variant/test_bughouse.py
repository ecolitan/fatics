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

from test.test import *

class TestBughouse(Test):
    def test_match(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as('GuestEFGH', '')
        t3 = self.connect_as('GuestIJKL', '')
        t4 = self.connect_as('GuestMNOP', '')

        t.write('match guestijkl bughouse\n')
        self.expect('You have no partner for bughouse.', t)

        t2.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t2)
        t.write('part guestefgh\n')
        self.expect('GuestABCD offers', t2)
        t2.write('part guestabcd\n')
        self.expect('GuestEFGH accepts', t)

        t.write('match guestijkl bughouse\n')
        self.expect('Your opponent has no partner for bughouse.', t)

        t4.write('set bugopen\n')
        self.expect('You are now open for bughouse.', t4)
        t3.write('part guestmnop\n')
        self.expect('GuestIJKL offers', t4)
        t4.write('a\n')
        self.expect('GuestMNOP accepts', t3)

        t2.write('set open\n')
        self.expect('You are no longer open to receive match requests.', t2)
        t.write('match guestijkl bughouse 3+0\n')
        self.expect('Your partner is not available to play right now.', t)
        t2.write('set open\n')
        self.expect('You are now open to receive match requests.', t2)

        t4.write('ex\n')
        self.expect('Starting a game in examine (scratch) mode', t4)
        t.write('match guestijkl bughouse 3+0\n')
        self.expect("Your opponent's partner is not available to play right now.", t)
        t4.write('unex\n')
        self.expect('You are no longer examining', t4)

        t.write('match guestefgh bughouse 3+0\n')
        self.expect('You cannot challenge your own partner for bughouse.', t)

        t4.write('set open\n')
        self.expect('You are no longer open to receive match requests.', t4)
        t4.write('set open\n')
        self.expect('You are now open to receive match requests.', t4)

        t.write('match guestijkl bughouse 3+0\n')
        self.expect('Issuing: GuestABCD (++++) GuestIJKL (++++) unrated blitz bughouse 3 0', t)

        '''t5 = self.connect_as_admin()
        t5.write('match guestmnop 1+0\n')
        self.expect('Challenge: admin', t4)
        t4.write('a\n')
        self.expect("Your opponent's partner has started another game.", t)
        t5.write('abort\n')
        self.expect('aborted on move 1', t4)
        self.close(t5)

        t.write('match guestijkl bughouse 3+0\n')
        self.expect('Issuing: GuestABCD (++++) GuestIJKL (++++) 3 0 unrated bughouse', t)
        t2.write('ex\n')
        self.expect("Your partner has started another game.", t)
        t2.write('unex\n')'''

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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

class TestObserve(Test):
    def test_observe_unobserve(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_user('GuestEFGH', '')
        t3 = self.connect_as_user('GuestIJKL', '')

        t.write('set style 12\n')
        t.write('observe\n')
        self.expect('Usage:', t)
        t.write('unobserve\n')
        self.expect('You are not observing any games', t)

        t.write('observe GuestABCD\n')
        self.expect('GuestABCD is not playing or examining a game', t)

        t.write('unobserve GuestABCD\n')
        self.expect('GuestABCD is not playing or examining a game', t)

        t.write('observe admin\n')
        self.expect('No user named "admin" is logged in', t)

        t2.write('match guestijkl 1 0 w\n')
        self.expect('Challenge:', t3)
        t3.write('a\n')
        self.expect('Creating:', t2)
        self.expect('Creating:', t3)

        t2.write('o 1\n')
        self.expect('You cannot observe yourself', t2)
        t3.write('o 1\n')
        self.expect('You cannot observe yourself', t3)

        t.write('o Guestijkl\n')
        self.expect('<12>', t)

        t2.write('h4\n')
        self.expect('<12>', t)
        self.expect('P/h2-h4', t)

        t.write('unobserve\n')
        self.expect('Removing game 1 from observation list.', t)
        t.write('unobserve guestefgh\n')
        self.expect('You are not observing game 1', t)

        t.write('o 1\n')
        self.expect('You are now observing game 1.', t)
        self.expect('<12> ', t)
        t.write('o guestefgh\n')
        self.expect('You are already observing game 1.', t)

        t.write('unob 1\n')
        self.expect('Removing game 1 from observation list.', t)
        t.write('ob 1\n')
        self.expect('You are now observing game 1.', t)
        self.expect('<12> ', t)
        t.write('unob Guestefgh\n')
        self.expect('Removing game 1 from observation list.', t)
        t.write('ob guestijkl\n')
        self.expect('You are now observing game 1.', t)
        self.expect('<12> ', t)

        t2.write('res\n')
        self.expect('GuestEFGH resigns} 0-1', t)
        self.expect('Removing game 1 from observation list.', t)

        self.close(t)
        self.close(t2)
        self.close(t3)

class TestAllobservers(Test):
    def test_allobservers(self):
        t = self.connect_as_user('GuestABCD', '')
        t2 = self.connect_as_user('GuestEFGH', '')
        t3 = self.connect_as_user('GuestIJKL', '')
        t4 = self.connect_as_user('GuestMNOP', '')

        self.expect_command_prints_nothing("allobservers\n", t)

        t2.write('allob 1\n')
        self.expect('There is no such game', t2)

        t2.write('allob nosuchuser\n')
        self.expect('No user named "nosuchuser" is logged in', t2)

        t2.write('allob i18n\n')
        self.expect('"i18n" is not a valid handle', t2)

        t2.write('allob guestabcd\n')
        self.expect('GuestABCD is not playing or examining a game', t2)

        t.write('match guestefgh 1 0 w\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')
        self.expect('Creating:', t)
        self.expect('Creating:', t2)

        t3.write('match guestmnop 1 0 w\n')
        self.expect('Challenge:', t4)
        t4.write('a\n')
        self.expect('Creating:', t3)
        self.expect('Creating:', t4)

        self.expect_command_prints_nothing("allobservers\n", t)

        t.write('o 2\n')
        self.expect('now observing', t)
        t3.write('o 1\n')
        self.expect('now observing', t3)
        t.write('allob\n')
        self.expect('Observing 1 [GuestABCD vs. GuestEFGH]: GuestIJKL(U) (1 user)', t)
        self.expect('Observing 2 [GuestIJKL vs. GuestMNOP]: GuestABCD(U) (1 user)', t)

        t4.write('o 1\n')
        self.expect('now observing', t4)
        t.write('allob guestefgh\n')
        self.expect('Observing 1 [GuestABCD vs. GuestEFGH]: GuestIJKL(U) GuestMNOP(U) (2 users)', t)
        t2.write('allob 1\n')
        self.expect('Observing 1 [GuestABCD vs. GuestEFGH]: GuestIJKL(U) GuestMNOP(U) (2 users)', t2)
        t3.write('unob guestabcd\n')
        self.expect('Removing', t3)
        t4.write('unob 1\n')
        self.expect('Removing', t4)
        t.write('allob 1\n')
        self.expect('No one is observing game 1.', t)

        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

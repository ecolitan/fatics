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

class TestMatch(Test):
    def test_match(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()

        t.write('match guest\n')
        self.expect("can't match yourself", t)

        t.write('match nonexistentname\n')
        self.expect('No player named "nonexistentname"', t)

        t.write('match admin 1 0 r\n')
        self.expect('Only registered players can play rated games', t)
        t2.write('match Guest 1 0 r\n')
        self.expect('Only registered players can play rated games', t2)

        t.write('set open 0\n')
        t2.write('set open 0\n')
        t.write('match admin\n')
        self.expect('admin is not open to match requests', t)

        t2.write('set open 1\n')
        self.expect('now open', t2)
        t.write('match admin\n')
        self.expect('now open to receive match requests', t)
        self.expect('Issuing: ', t)
        self.expect('Challenge: ', t2)

        self.close(t)
        self.close(t2)

    def test_bad_match(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()

        t.write('match admin b c d e\n')
        self.expect('Usage: ', t)

        t.write('match admin 1 2 3 4 5\n')
        self.expect('Usage: ', t)

        # conflicting colors
        t.write('match admin white black\n')
        self.expect('Usage: ', t)

        # conflicting variants
        t.write('match admin chess crazyhouse\n')
        self.expect('Usage: ', t)

        # conflicting ratedness
        t.write('match admin rated unrated\n')
        self.expect('Usage: ', t)

        self.close(t)
        self.close(t2)

    def test_default_match(self):
        """ Test default time controls using the 'time' and 'inc'
        vars. """
        t = self.connect_as_admin()
        t2 = self.connect_as('GuestABCD', '')

        t2.write('match admin\n')
        self.expect('Challenge:', t)
        self.expect('rated blitz 2 12', t)

        self.close(t)
        self.close(t2)

    @with_player('testplayer', 'testpass')
    def test_match_case(self):
        """ Test default time controls using the 'time' and 'inc'
        vars. """
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t2.write('match admin 3 0 R cRaZyHousE\n')
        self.expect('Challenge:', t)
        self.expect('rated blitz crazyhouse 3 0', t)

        self.close(t)
        self.close(t2)

    def test_plus_syntax(self):
        """ Test syntax like 'match admin 3+0' """
        t = self.connect_as_admin()
        t2 = self.connect_as('GuestABCD', '')

        t2.write('match admin 3+1 white\n')
        self.expect('Challenge: GuestABCD (++++) [white] admin (----) unrated blitz 3 1', t)

        self.close(t)
        self.close(t2)

    def test_withdraw_logout(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        t2.write('match guest\n')
        t2.write('quit\n')
        self.expect('Withdrawing your match offer to Guest', t2)
        self.expect('Thank you for using', t2)
        t2.close()

        self.expect('admin, who was challenging you, has departed', t)
        self.close(t)

    def test_decline_logout(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_admin()

        t.write('match admin\n')
        self.expect('Challenge:', t2)
        t2.write('quit\n')
        self.expect('Declining the match offer from Guest', t2)
        t2.close()

        self.expect('admin, whom you were challenging, has departed', t)
        self.close(t)

    def test_decline_unclean_logout(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_admin()

        t.write('match admin\n')
        self.expect('Challenge:', t2)
        t2.close()

        self.expect('admin, whom you were challenging, has departed', t)
        self.close(t)

    def test_accept(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()
        t2.write('set open 1\n')

        t.write('match admin\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Accepting the match offer', t2)
        self.expect('accepts your match offer', t)

        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.write('match admin\n')
        self.expect("You can't challenge while you are playing", t)

        self.close(t)
        self.close(t2)

    def test_withdraw(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()

        t.write('match admin\n')
        self.expect('Challenge:', t2)
        t.write('withdraw\n')
        self.expect('Withdrawing your match offer', t)
        self.expect('withdraws the match offer', t2)

        self.close(t)
        self.close(t2)

    def test_decline(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()

        t.write('match admin\n')
        self.expect('Challenge:', t2)
        t2.write('decline\n')
        self.expect('Declining the match offer', t2)
        self.expect('declines your match offer', t)

        self.close(t)
        self.close(t2)

    def test_counteroffer(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_admin()

        t.write('match admin 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('match Guest 2 0\n')
        self.expect('Declining the offer from GuestABCD and proposing a counteroffer', t2)
        self.expect('admin declines your offer and proposes a counteroffer', t)

        self.close(t)
        self.close(t2)

    def test_update_offer(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_admin()

        t.write('match admin 1 0\n')
        self.expect('Challenge:', t2)
        t.write('match admin 1 0 white\n')
        self.expect('Updating the offer already made to admin', t)
        self.expect('GuestABCD updates the offer', t2)

        self.close(t)
        self.close(t2)

    def test_update_offer_clock(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_admin()

        t.write('match admin 2+12\n')
        self.expect('Challenge:', t2)
        t.write('match admin 2 12 bronstein\n')
        self.expect('Updating the offer already made to admin', t)
        self.expect('GuestABCD updates the offer', t2)

        self.close(t)
        self.close(t2)

    def test_offer_identical(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()

        t.write('match admin 1 0 black\n')
        t.write('match admin 1 0 black\n')
        self.expect('already offering an identical match to admin', t)

        self.close(t)
        self.close(t2)

    def test_intercept(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_admin()

        t.write('match admin 1 2 white\n')
        self.expect('Challenge:', t2)
        t2.write('match Guestabcd 1 2 black\n')
        self.expect("Your challenge intercepts GuestABCD's challenge.", t2)
        self.expect("admin's challenge intercepts your challenge.", t)
        #self.expect('Accepting the match offer', t2)
        #self.expect('accepts your match offer', t)

        self.close(t)
        self.close(t2)

    def test_match_order(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t.write('withdraw\n')

        t.write('match 1 0 admin white\n')
        self.expect('"1" is not a valid handle', t)

        self.close(t)
        self.close(t2)

class TestRmatch(Test):
    @with_player('testplayer', 'testplayer')
    @with_player('tdplayer', 'tdplayer', ['td'])
    def test_rmatch(self):
        t = self.connect_as('testplayer', 'testplayer')
        t2 = self.connect_as_admin()
        t3 = self.connect_as('tdplayer', 'tdplayer')

        t.write('rmatch testplayer admin 3 0\n')
        self.expect('Only TD programs', t)

        t3.write('rmatch testplayer admin 3 0 white r\n')
        self.expect('Issuing: testplayer (----) [white] admin (----) rated blitz 3 0', t)
        self.expect('Challenge: testplayer (----) [white] admin (----) rated blitz 3 0', t2)

        t2.write('a\n')
        self.expect('Creating:', t)
        self.expect('Creating:', t2)
        t.write('abort\n')

        self.close(t)
        self.close(t2)
        self.close(t3)

class TestRematch(Test):
    def test_rematch(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('GuestABCD', '')

        t.write('match guestabcd 1 0 unrated white\n')
        self.expect('Challenge: ', t2)
        t2.write('a\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        t.write('res\n')
        self.expect('admin resigns} 0-1', t)
        self.expect('admin resigns} 0-1', t2)

        t.write('rematch\n')
        self.expect('Challenge: admin (----) GuestABCD (++++) unrated lightning 1 0', t2)
        t2.write('a\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        t.write('res\n')
        self.expect('admin resigns} 1-0', t)
        self.expect('admin resigns} 1-0', t2)

        t2.write('rem\n')
        self.expect('Challenge: GuestABCD (++++) admin (----) unrated lightning 1 0', t)
        t.write('a\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        t.write('res\n')
        self.expect('admin resigns} 0-1', t)
        self.expect('admin resigns} 0-1', t2)

        t.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t)

        self.close(t)

        t2.write('rematch\n')
        self.expect('Your last opponent, admin, is not logged in.', t2)

        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

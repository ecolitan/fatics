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

class TestList(Test):
    def test_list_error(self):
        t = self.connect_as_guest()

        t.write('addlist foo bar\n')
        self.expect("does not match any list", t)

        t.write('sublist foo bar\n')
        self.expect("does not match any list", t)

        t.write('+g admin\n')
        self.expect("You don't have permission", t)

        self.close(t)

    def test_list_persistence(self):
        # see also test_title; this tests persistence
        t = self.connect_as_admin()

        t.write('+sr admin\n')
        self.expect("admin added to the SR list.", t)

        try:
            t.write('t admin foo bar\n')
            self.expect('admin(SR)(*) tells you: foo bar', t)
            self.close(t)

            t = self.connect_as_admin()
            t.write('t admin foo bar\n')
            self.expect('admin(SR)(*) tells you: foo bar', t)
        finally:
            t.write('-sr admin\n')

        self.expect("admin removed from the SR list.", t)
        self.close(t)

        t = self.connect_as_admin()
        t.write('t admin foo bar\n')
        self.expect('admin(*) tells you: foo bar', t)
        self.close(t)

class TestTitle(Test):
    def test_bad_name(self):
        t = self.connect_as_admin()
        t.write('+gm nonexistentname\n')
        self.expect("no player matching", t)
        self.close(t)

    def test_title(self):
        t2 = self.connect_as_guest()
        t2.write('+gm admin\n')
        self.expect("You don't have permission", t2)

        t = self.connect_as_admin()
        t.write('+gm guest\n')
        self.expect('nly registered users may', t)
        self.close(t2)

        t.write('+gm admin\n')
        self.expect("admin added to the GM list", t)

        t.write('=gm\n')
        self.expect("GM list:", t)
        self.expect("admin", t)

        t.write('t admin a b c\n')
        self.expect("admin(GM)(*) tells you: a b c", t)

        t.write('+gm admin\n')
        self.expect("admin is already on the GM list", t)

        t.write('-gm admin\n')
        self.expect("admin removed from the GM list", t)

        t.write('-gm admin\n')
        self.expect("admin is not on the GM list", t)

        t.write('t admin d e f\n')
        self.expect("admin(*) tells you: d e f", t)

        self.close(t)

class TestAbuser(Test):
    def test_show_abusers(self):
        t = self.connect_as_guest()
        t.write('=abuser\n')
        self.expect("You don't have permission", t)
        self.close(t)

    @with_player('TestPlayer', 'testpass')
    def test_abuser(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t.write('=abuser\n')
        self.expect('abuser list: ', t)

        t.write('+abuser testplayer\n')
        self.expect('TestPlayer added to the abuser list.', t)
        self.expect('admin has added you to the abuser list.', t2)

        # abuser status should not affect user's display name
        t.write('f testplayer\n')
        self.expect('Finger of TestPlayer:\r\n', t)

        t.write('match testplayer 1 0\n')
        self.expect('--** TestPlayer is an abuser **--', t)
        t.write('withdraw\n')
        self.expect('admin withdraws', t2)

        t2.write('match admin 1 0\n')
        self.expect('--** TestPlayer is an abuser **--', t)
        t.write('decline\n')
        self.expect('admin declines', t2)

        t.write('-abuser testplaye\n')
        self.expect('TestPlayer removed from the abuser list.', t)
        self.expect('admin has removed you from the abuser list.', t2)

        self.close(t)
        self.close(t2)

class TestCensor(Test):
    def test_censor_guest(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as('GuestDEFG', '')

        t.write('+cen Nosuchplayer\n')
        self.expect('There is no player matching the name "nosuchplayer".', t)

        t.write('-cen admin\n')
        self.expect('admin is not on your censor list.', t)

        t.write('+cen guestdefg\n')
        self.expect('GuestDEFG added to your censor list.', t)

        t.write("=cens\n")
        self.expect('censor list: 1 name', t)
        self.expect('GuestDEFG', t)

        t2.write('t guestABCD hi\n')
        self.expect('GuestABCD is censoring you.', t2)

        t2.write('m guestabcd\n')
        self.expect('GuestABCD is censoring you.', t2)

        t.write('-cen guestdefg\n')
        self.expect('GuestDEFG removed from your censor list.', t)

        t2.write('t guestabcd hi again\n')
        self.expect('(told GuestABCD)', t2)
        self.expect('GuestDEFG(U) tells you: hi again', t)
        self.close(t2)

        t2 = self.connect_as_admin()
        t.write('+cen admin\n')
        self.expect('admin added to your censor list', t)

        t2.write("t guestabcd You can't censor me\n")
        self.expect("You can't censor me", t)

        self.close(t2)
        self.close(t)

    @with_player('TestPlayer', 'test')
    def test_censor_user(self):
        t = self.connect_as_admin()
        t.write('+cen nosuchplayer\n')
        self.expect('no player matching the name "nosuchplayer"', t)

        t.write('+cen TestPlayer\n')
        self.expect('TestPlayer added to your censor list.', t)

        t.write('+cen TestPlayer\n')
        self.expect('TestPlayer is already on your censor list.', t)

        t.write("=cen\n")
        self.expect('censor list: 1 name', t)
        self.expect('TestPlayer', t)
        self.close(t)

        t = self.connect_as_admin()
        t2 = self.connect_as('TestPlayer', 'test')
        t.write('+ch 5\n')
        t2.write('+ch 5\n')

        t2.write('t Admin hey there!\n')
        self.expect("admin is censoring you.", t2)

        t2.write('mess admin test\n')
        self.expect("admin is censoring you.", t2)

        t2.write('shout anybody there?\n')
        self.expect("shouted to 1 player", t2)

        t2.write('cshout or there?\n')
        self.expect("c-shouted to 1 player", t2)

        t2.write('tell 5 or in ch 1\n')
        self.expect("(told 1 player in channel 5)", t2)

        t.write('-cen testplayer\n')
        self.expect('TestPlayer removed from your censor list.', t)

        t.write('-cen testplayer\n')
        self.expect('TestPlayer is not on your censor list.', t)

        t2.write('shout test 123\n')
        self.expect("(shouted to 2 players)", t2)
        self.expect('test 123', t)

        t2.write('tell 5 456 789\n')
        self.expect("(told 2 players in channel 5)", t2)
        self.expect('TestPlayer(5): 456 789', t)

        self.close(t)

        t = self.connect_as_admin()
        t2.write('t admin test 123\n')
        self.expect('test 123', t)

        t.write('-ch 5\n')
        t2.write('-ch 5\n')
        t.write('-cen testplayer\n')
        self.close(t)
        self.close(t2)

    @with_player('TestPlayer', 'testpass')
    def test_censor_persistence(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')
        t.write('+cen testplayer\n')
        self.expect('TestPlayer added to your censor list.', t)
        self.close(t)
        self.close(t2)

        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')
        t2.write('t admin hi\n')
        self.expect('admin is censoring you.', t2)
        t.write('-cen testplayer\n')
        self.expect('TestPlayer removed from your censor list.', t)
        self.close(t)
        self.close(t2)

class TestNoplay(Test):
    def test_noplay_guest(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as('GuestDEFG', '')

        t.write('+noplay GuestDEFG\n')
        self.expect('GuestDEFG added to your noplay list.', t)

        t.write("=noplay\n")
        self.expect('noplay list: 1 name', t)
        self.expect('GuestDEFG', t)

        t2.write('match guestabcd\n')
        self.expect("You are on GuestABCD's noplay list", t2)

        t.write('-noplay GuestDEFG\n')
        self.expect('GuestDEFG removed from your noplay list.', t)

        t2.write('match guestabcd\n')
        self.expect("Issuing:", t2)
        self.expect("Challenge:", t)

        self.close(t)
        self.close(t2)

    @with_player('TestPlayer', 'test')
    def test_noplay_user(self):
        t = self.connect_as_admin()
        t.write('+noplay nosuchplayer\n')
        self.expect('no player matching the name "nosuchplayer"', t)

        t.write('+noplay TestPlayer\n')
        self.expect('TestPlayer added to your noplay list.', t)

        t.write('+noplay TestPlayer\n')
        self.expect('TestPlayer is already on your noplay list.', t)

        t.write("=noplay\n")
        self.expect('noplay list: 1 name', t)
        self.expect('TestPlayer', t)
        self.close(t)

        t = self.connect_as_admin()
        t2 = self.connect_as('TestPlayer', 'test')

        t2.write('match admin\n')
        self.expect("You are on admin's noplay list", t2)

        t.write('-noplay testplayer\n')
        self.expect('TestPlayer removed from your noplay list.', t)

        t.write('-noplay testplayer\n')
        self.expect('TestPlayer is not on your noplay list.', t)

        t2.write('match admin\n')
        self.expect("Issuing:", t2)
        self.expect("Challenge:", t)

        self.close(t)

        t = self.connect_as_admin()
        t2.write('match admin\n')
        self.expect("Issuing:", t2)
        self.expect("Challenge:", t)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

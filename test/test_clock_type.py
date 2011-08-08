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

import time

class TestFischer(Test):
    @with_player('testplayer', 'testpass')
    def test_fischer(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')
        t.write('set style 12\n')
        self.expect('Style 12 set.', t)

        t2.write('match admin 3 5 chess fischer white\n')
        self.expect('Challenge:', t)
        t.write('a\n')

        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 3 5 39 39 180 180 1 none (0:00) none 1 0 0\r\n', t)

        t2.write('d4\n')
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin 1 3 5 39 39 180 180 1 P/d2-d4 (0:00) d4 1 0 0\r\n', t)

        t.write('d5\n')
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 3 5 39 39 180 180 2 P/d7-d5 (0:00) d5 1 1 0\r\n', t)

        # now the 5-second increment should be added
        time.sleep(2.0)
        t2.write('c4\n')
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- --PP---- -------- PP--PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin 1 3 5 39 39 183 180 2 P/c2-c4 (0:02) c4 1 1 0\r\n', t)

        t.write('abort\n')
        t2.write('abort\n')
        self.expect('aborted by agreement', t)

        self.close(t)
        self.close(t2)

class TestBronstein(Test):
    def test_bad_bronstein(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()
        t2.write('match admin 3 0 bronstein\n')
        self.expect('Games using a Bronstein clock must have an increment.', t2)
        self.close(t)
        self.close(t2)

    @with_player('testplayer', 'testpass')
    def test_bronstein(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')
        t.write('set style 12\n')
        self.expect('Style 12 set.', t)

        t2.write('match admin 3 2 chess bronstein white\n')
        self.expect('Challenge:', t)
        self.expect('bronstein', t)
        t.write('a\n')

        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 3 2 39 39 180 180 1 none (0:00) none 1 0 0\r\n', t)

        t2.write('d4\n')
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin 1 3 2 39 39 180 180 1 P/d2-d4 (0:00) d4 1 0 0\r\n', t)

        t.write('d5\n')
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 3 2 39 39 180 180 2 P/d7-d5 (0:00) d5 1 1 0\r\n', t)

        # 1-second move time should leave clock unchanged
        time.sleep(1.0)
        t2.write('c4\n')
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- --PP---- -------- PP--PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin 1 3 2 39 39 180 180 2 P/c2-c4 (0:01) c4 1 1 0\r\n', t)

        # 4-second move time should subtract 2 seconds
        time.sleep(4.0)
        t.write('e5\n')
        self.expect('\r\n<12> rnbqkbnr ppp--ppp -------- ---pp--- --PP---- -------- PP--PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 3 2 39 39 180 178 3 P/e7-e5 (0:04) e5 1 1 0\r\n', t)

        t.write('abort\n')
        t2.write('abort\n')
        self.expect('aborted by agreement', t)

        self.close(t)
        self.close(t2)

class TestHourglass(Test):
    @with_player('testplayer', 'testpass')
    def test_bad_hourglass(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t2.write('match admin 1 1 hourglass\n')
        self.expect('Games using an hourglass clock may not have an increment.', t2)
        t2.write('match admin r hourglass\n')
        self.expect('This clock type cannot be used in rated', t2)

        self.close(t)
        self.close(t2)

    @with_player('testplayer', 'testpass')
    def test_hourglass(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')
        t.write('set style 12\n')
        self.expect('Style 12 set.', t)

        t2.write('match admin 1 chess hourglass white\n')
        self.expect('Challenge:', t)
        self.expect('hourglass', t)
        t.write('a\n')

        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60 60 1 none (0:00) none 1 0 0\r\n', t)

        t2.write('d4\n')
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 60 60 1 P/d2-d4 (0:00) d4 1 0 0\r\n', t)

        t.write('d5\n')
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60 60 2 P/d7-d5 (0:00) d5 1 1 0\r\n', t)

        # 2-second move time should subtract from moving player and add to opp
        time.sleep(2.0)
        t2.write('c4\n')
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- --PP---- -------- PP--PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 58 62 2 P/c2-c4 (0:02) c4 1 1 0\r\n', t)

        t.write('abort\n')
        t2.write('abort\n')
        self.expect('aborted by agreement', t)

        self.close(t)
        self.close(t2)

class TestStandardClock(Test):
    def test_bad_standard_clock(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()

        t2.write('match admin 40/90\n')
        self.expect('Usage:', t2)
        t2.write('match admin 40/90 sd/30\n')
        self.expect('Usage:', t2)
        t2.write('match admin 40/90,sd/0\n')
        self.expect('must have a positive overtime', t2)
        t2.write('match admin 40/0,sd/30\n')
        self.expect('must have a positive initial time', t2)
        t2.write('match admin 1/90,sd/30\n')
        self.expect('Invalid', t2)

        self.close(t)
        self.close(t2)

    @with_player('testplayer', 'testpass')
    def test_standard_clock(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t.write('set style 12\n')

        t2.write('match admin 40/90,sd/30+30\n')
        self.expect('Challenge:', t)
        self.expect('40/90,SD/30+30', t)
        t.write('decl\n')
        self.expect('admin declines', t2)

        t2.write('match admin 3/90,SD/10+15 white\n')
        self.expect('Challenge:', t)
        self.expect('3/90,SD/10+15', t)
        t.write('a\n')

        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 90 15 39 39 5400 5400 1 none (0:00) none 1 0 0\r\n', t)

        t2.write('d4\n')
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin 1 90 15 39 39 5400 5400 1 P/d2-d4 (0:00) d4 1 0 0\r\n', t)

        t.write('d5\n')
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 90 15 39 39 5400 5400 2 P/d7-d5 (0:00) d5 1 1 0\r\n', t)

        # 15-second increment only
        time.sleep(1.0)
        t2.write('c4\n')
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- --PP---- -------- PP--PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin 1 90 15 39 39 5414 5400 2 P/c2-c4 (0:01) c4 1 1 0\r\n', t)

        t.write('e5\n')
        self.expect('\r\n<12> rnbqkbnr ppp--ppp -------- ---pp--- --PP---- -------- PP--PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 90 15 39 39 5414 5415 3 P/e7-e5 (0:00) e5 1 1 0\r\n', t)

        # 10-minute bonus after 3rd move (plus usual 15s increment)
        time.sleep(1.0)
        t2.write('dxe5\n')
        self.expect('\r\n<12> rnbqkbnr ppp--ppp -------- ---pP--- --P----- -------- PP--PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin 1 90 15 39 38 6028 5415 3 P/d4-e5 (0:01) dxe5 1 1 0\r\n', t)

        # likewise
        t.write('d4\n')
        self.expect('\r\n<12> rnbqkbnr ppp--ppp -------- ----P--- --Pp---- -------- PP--PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 90 15 39 38 6028 6030 4 P/d5-d4 (0:00) d4 1 1 0\r\n', t)

        t.write('abort\n')
        t2.write('abort\n')
        self.expect('aborted by agreement', t)

        self.close(t)
        self.close(t2)

class TestUntimed(Test):
    @with_player('testplayer', 'testpass')
    def test_bad_untimed(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t2.write('match admin 0 0 fischer\n')
        self.expect('Usage:', t2)
        t2.write('match admin 1 0 untimed\n')
        self.expect('Usage:', t2)
        t2.write('match admin 0+1 untimed\n')
        self.expect('Usage:', t2)
        t2.write('match admin untimed rated\n')
        self.expect('This clock type cannot be used in rated', t2)

        self.close(t)
        self.close(t2)

    @with_player('testplayer', 'testpass')
    def test_untimed(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        self.set_style_12(t)

        t2.write('match admin untimed white\n')
        self.expect('Issuing: testplayer (----) [white] admin (----) unrated untimed.\r\n', t2)
        self.expect('Challenge: testplayer (----) [white] admin (----) unrated untimed.\r\n', t)
        t.write('a\n')
        self.expect('Creating: testplayer (----) admin (----) unrated untimed 0 0\r\n', t)

        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 0 0 39 39 0 0 1 none (0:00) none 1 0 0\r\n', t)

        t2.write('d4\n')
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin 1 0 0 39 39 0 0 1 P/d2-d4 (0:00) d4 1 0 0\r\n', t)

        t.write('d5\n')
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 0 0 39 39 0 0 2 P/d7-d5 (0:00) d5 1 1 0\r\n', t)

        t.write('abort\n')
        t2.write('abort\n')
        self.expect('aborted', t)

        # with 'untimed' keyword and zero time and inc
        t2.write('match admin untimed 0 0\n')
        self.expect('Challenge:', t)
        self.expect('untimed', t)
        t.write('decl\n')
        self.expect('admin declines', t2)

        # without 'untimed' keyword
        t2.write('match admin 0 0\n')
        self.expect('Challenge:', t)
        self.expect('untimed', t)
        t.write('decl\n')
        self.expect('admin declines', t2)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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

class TestClock(Test):
    @with_player('testplayer', 'testpass')
    def test_fischer(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')
        t.write('set style 12\n')
        self.expect('style set', t)

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

    @with_player('testplayer', 'testpass')
    def test_bronstein(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')
        t.write('set style 12\n')
        self.expect('style set', t)

        t2.write('match admin 3 2 chess bronstein white\n')
        self.expect('Challenge:', t)
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

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

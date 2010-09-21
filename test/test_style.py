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

class TestStyle12(Test):
    def test_style12(self):
        self.adduser('testplayer', 'testpass')
        t = self.connect_as('testplayer', 'testpass')
        t2 = self.connect_as_admin()
        t.write('set style 12\n')
        t.write('iset ms 1\n')
        t2.write('set style 12\n')

        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 60000 60000 1 none (0:00.000) none 0 0 0\r\n', t)
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60 60 1 none (0:00) none 1 0 0\r\n', t2)

        t.write('d4\n')

        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60000 60000 1 P/d2-d4 (0:00.000) d4 0 0 0\r\n', t)
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B -1 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 60 60 1 P/d2-d4 (0:00) d4 1 0 0\r\n', t2)

        t2.write('d5\n')
        #m = self.expect_re(r'\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 (\d+) 60000 2 P/d7-d5 (0:00.000) d5 0 1 0\r\n', t)
        m = self.expect_re(r'\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin 1 1 0 39 39 (\d+)', t)
        # on slow machines a ms may tick away
        self.assert_(59999 <= int(m.group(1)) <= 60000)
        self.expect('\r\n<12> rnbqkbnr ppp-pppp -------- ---p---- ---P---- -------- PPP-PPPP RNBQKBNR W -1 1 1 1 1 0 1 testplayer admin -1 1 0 39 39 60 60 2 P/d7-d5 (0:00) d5 1 1 0\r\n', t2)
        self.expect

        self.close(t)
        self.close(t2)

        self.deluser('testplayer')

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

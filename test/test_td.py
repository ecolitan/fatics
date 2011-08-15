# -*- coding: utf-8 -*-
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

class TestGetpi(Test):
    @with_player('tdplayer', ['td'])
    @with_player('TestPlayer')
    def test_getpi(self):
        t = self.connect_as('tdplayer')
        t2 = self.connect_as('TestPlayer')

        t.write('getpi doesnotexist\n')
        self.expect_not('getpi', t)

        t3 = self.connect_as_guest('GuestTest')
        t.write('getpi guesttest\n')
        self.expect('*getpi GuestTest -1 -1 -1*', t)
        self.close(t3)

        t3 = self.connect_as_admin()
        t3.write('asetrating testplayer blitz chess 1500 250 .01 0 0 0\n')
        self.expect('Set blitz chess rating', t3)
        t3.write('asetrating testplayer standard chess 1600 260 .01 0 0 0\n')
        self.expect('Set standard chess rating', t3)
        t3.write('asetrating testplayer lightning chess 1700 270 .01 0 0 0\n')
        self.expect('Set lightning chess rating', t3)
        self.close(t3)

        t.write('getpi testplayer\n')
        self.expect('*getpi TestPlayer 0 1500 1600 1700*', t)

        self.close(t)
        self.close(t2)

class TestGetgi(Test):
    @with_player('tdplayer', ['td'])
    @with_player('TestOne')
    @with_player('TestTwo')
    def test_getgi(self):
        t = self.connect_as('testone')
        t2 = self.connect_as('testtwo')
        t3 = self.connect_as('tdplayer')

        t3.write('getgi doesnotexist\n')
        self.expect_not('getgi', t3)

        t4 = self.connect_as_guest('GuestTest')
        t3.write('getgi guesttest\n')
        self.expect_not('getgi', t3)
        self.close(t4)

        t3.write('getgi testone\n')
        self.expect('TestOne is not playing a game.', t3)

        # examining doesn't count as playing
        t.write('e\n')
        self.expect('Starting a game', t)
        t3.write('getgi testone\n')
        self.expect('TestOne is not playing a game.', t3)
        t.write('unex\n')
        self.expect('You are no longer examining', t)

        t.write('match testtwo! 3 2 white\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        m = self.expect_re(r'\{Game (\d+)', t2)
        num = int(m.group(1))

        t3.write('getgi testone\n')
        self.expect('*getgi TestOne TestOne TestTwo %d 3 2 1 0*' % num, t3)

        t.write('abort\n')
        self.expect('aborted', t2)

        self.close(t)
        self.close(t2)
        self.close(t3)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

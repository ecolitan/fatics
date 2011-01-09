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

class TestTimezone(Test):
    def test_timezone_guest(self):
        t = self.connect_as_guest()

        t.write('set tzone EST\n')
        self.expect('Bad value given for variable "tzone"', t)

        t.write('set tzone +2\n')
        self.expect('Bad value given for variable "tzone"', t)

        t.write('set tzone US/Eastern\n')
        self.expect('Time zone set to "US/Eastern"', t)
        self.expect_re('\(E[DS]T, UTC-0[45]00\).', t)

        t.write('date\n')
        self.expect('Local time', t)
        self.expect_re('E[DS]T', t)
        self.expect('Server time', t)

        t.write('set tzone\n')
        self.expect('Time zone set to "UTC"', t)

        self.close(t)

    def test_timezone_moves(self):
        t = self.connect_as_guest()
        t.write('set tzone Pacific/Fiji\n')
        self.expect('Time zone set to "Pacific/Fiji"', t)
        t.write('ex\n')
        self.expect('Starting a game', t)
        t.write('moves\n')
        self.expect_re(' FJS?T', t)
        t.write('unex\n')
        self.close(t)

    def test_timezone_persistence(self):
        t = self.connect_as_admin()

        t.write('set tzone America/Caracas\n')
        self.expect('Time zone set to "America/Caracas"', t)

        t.write('date\n')
        self.expect(' VET', t)

        self.close(t)

        t = self.connect_as_admin()

        t.write('date\n')

        self.expect(' VET', t)
        t.write('set tzone\n')
        self.expect('Time zone set to "UTC"', t)
        t.write('date\n')
        self.expect_not(' VET', t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

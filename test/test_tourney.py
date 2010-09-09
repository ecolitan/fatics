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

class TestTourney(Test):
    @with_player('tdplayer', 'tdpass', ['td'])
    def test_tournset(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('tdplayer', 'tdpass')

        t.write("tournset admin 1\n")
        self.expect('Only TD programs', t)

        t2.write("tournset admin foo\n")
        self.expect('Usage: ', t2)

        t2.write("tournset admin 1\n")
        self.expect('tdplayer has set your tourney variable to ON.', t)
        t2.write("tournset admin 0\n")
        self.expect('tdplayer has set your tourney variable to OFF.', t)

        self.close(t)
        self.close(t2)

    def test_tourney_var(self):
        t = self.connect_as_guest()
        t.write('set tourney 1\n')
        self.expect('Your tournament variable is now set.', t)
        t.write('set tourney 0\n')
        self.expect('Your tournament variable is no longer set.', t)
        self.close(t)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

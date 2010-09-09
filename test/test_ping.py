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

import time

from test import *

# XXX this doesn't actually test ping, since we don't have a
# way of testing through zipseal yet

class TestPing(Test):
    def test_ping(self):
        t = self.connect_as_guest()
        t.write('ping\n')
        self.expect('not using zipseal', t)

        t.write('ping guest\n')
        self.expect('not using zipseal', t)

        t.write('ping admin\n')
        self.expect('No player named "admin" is online.', t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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

class TestShowadmins(Test):
    def test_showadmins(self):
        t = self.connect_as_guest()
        t.write('showa\n')
        self.expect('0 admins logged in.', t)

        t2 = self.connect_as_admin()
        t.write('showa\n')
        self.expect('Name              Status       Idle time', t)
        self.expect_re('admin             Available    \d second', t)
        self.expect('1 admin logged in.', t)

        t2.write('admin\n')
        self.expect('(*) is now not shown', t2)
        t.write('showa\n')
        self.expect_re('admin             Off_duty     \d second', t)

        t.write('match admin 1+0 u\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')
        self.expect('Creating:', t2)
        t.write('showa\n')
        self.expect_re('admin             Playing      \d second', t)

        t.write('abo\n')
        self.expect('aborted', t2)
        t2.write('admin\n')
        self.expect('(*) is now shown', t2)

        t.write('showadmins\n')
        self.expect_re('admin             Available    \d second', t)

        self.close(t2)
        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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
        m = self.expect_re(r'(\d+) admins? logged in\.', t)
        count = int(m.group(1))

        t2 = self.connect_as_admin()
        t.write('showa\n')
        self.expect('Name              Status       Idle time', t)
        self.expect_re(r'admin             Available    \d second', t)
        self.expect_re(r'%d admins? logged in\.' % (count + 1), t)

        t2.write('admin\n')
        self.expect('(*) is now not shown', t2)
        t.write('showa\n')
        self.expect_re(r'admin             Off_duty     \d second', t)

        t.write('match admin 1+0 u\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')
        self.expect('Creating:', t2)
        t.write('showa\n')
        self.expect_re(r'admin             Playing      \d second', t)

        t.write('abo\n')
        self.expect('aborted', t2)
        t2.write('admin\n')
        self.expect('(*) is now shown', t2)

        t.write('showadmins\n')
        self.expect_re(r'admin             Available    \d second', t)

        self.close(t2)
        self.close(t)

class TestShowsrs(Test):
    @with_player('srplayer', ['sr'])
    def test_showsrs(self):
        t = self.connect_as_guest()
        t.write('showsrs\n')
        m = self.expect_re(r'(\d+) SRs? logged in\.', t)
        count = int(m.group(1))

        t2 = self.connect_as('srplayer')
        t.write('showsr\n')
        self.expect_re(r'srplayer          Available    \d second', t)
        self.expect_re(r'%d SRs? logged in\.' % (count + 1), t)

        t.write('match srplayer 1+0 u\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')
        self.expect('Creating:', t2)
        t.write('showsr\n')
        self.expect_re(r'srplayer          Playing      \d second', t)

        # XXX test on/off duty

        t.write('abo\n')
        self.expect('aborted', t2)
        self.close(t2)

        self.close(t)

class TestShowtms(Test):
    @with_player('tmplayer', ['tm'])
    def test_showtms(self):
        t = self.connect_as_guest()
        t.write('showtms\n')
        m = self.expect_re(r'(\d+) TMs? logged in\.', t)
        count = int(m.group(1))

        t2 = self.connect_as('tmplayer')
        t.write('showtm\n')
        self.expect_re(r'tmplayer          Available    \d second', t)
        m = self.expect_re(r'(\d+) TMs? logged in\.', t)
        self.assert_(int(m.group(1)) == count + 1)

        t.write('match tmplayer 1+0 u\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')
        self.expect('Creating:', t2)
        t.write('showtm\n')
        self.expect_re(r'tmplayer          Playing      \d second', t)

        # XXX test on/off duty

        t.write('abo\n')
        self.expect('aborted', t2)
        self.close(t2)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

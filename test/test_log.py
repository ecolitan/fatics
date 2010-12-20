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

class TestLogons(Test):
    @with_player('TestPlayer', 'testpass')
    def test_logons_user_admin(self):
        time.sleep(1.0)
        t = self.connect_as_admin()
        t.write('log testplayer\n')
        self.expect('TestPlayer has not logged on.', t)

        t2 = self.connect_as('TestPlayer', 'testpass')
        time.sleep(1.0)

        t.write('log testplayer\n')
        self.expect(': TestPlayer           login  from %s\r\n' % LOCAL_IP, t)

        self.close(t2)
        t.write('log testplayer\n')
        self.expect(': TestPlayer           login  from %s\r\n' % LOCAL_IP, t)
        self.expect(': TestPlayer           logout from %s\r\n' % LOCAL_IP, t)

        self.close(t)

    @with_player('TestPlayer', 'testpass')
    def test_logons_user(self):
        t = self.connect_as_guest()
        t.write('log testplayer\n')
        self.expect('TestPlayer has not logged on.', t)

        t2 = self.connect_as('TestPlayer', 'testpass')
        time.sleep(1.0)

        t.write('log testplayer\n')
        self.expect(': TestPlayer           login \r\n', t)

        self.close(t2)
        t.write('log testplayer\n')
        self.expect(': TestPlayer           login \r\n', t)
        self.expect(': TestPlayer           logout\r\n', t)

        self.close(t)

    def test_logons_guest(self):
        t = self.connect_as_guest('GuestABCD')
        t.write('log\n')
        self.expect_re(': GuestABCD            login \r\n', t)
        self.close(t)

class TestLlogons(Test):
    def test_llogons(self):
        # in case a previous test logged out in the past second, we make
        # sure this login is clearly ordered after it
        time.sleep(1.0)
        t = self.connect_as_admin()
        t.write('llogons -1\n')
        self.expect('Usage:', t)
        t.write('llogons\n')
        self.expect(': admin                login  from %s\r\n' % LOCAL_IP, t)
        t.write('llogons 1\n')
        self.expect(': admin                login  from %s\r\n' % LOCAL_IP, t)
        time.sleep(1)

        t2 = self.connect_as_guest('GuestABCD')
        t.write('llogons 1\n')
        self.expect(': GuestABCD            login  from %s\r\n' % LOCAL_IP, t)
        self.close(t2)
        t.write('llogons 1\n')
        self.expect(': GuestABCD            logout from %s\r\n' % LOCAL_IP, t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

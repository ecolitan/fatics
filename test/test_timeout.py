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

class TestLoginTimeout(Test):
    def setUp(self):
        self._skip('slow test')

    def test_timeout(self):
        t = self.connect()
        self.expect('TIMEOUT', t, timeout=65)
        t.close()

    def test_guest_timeout_password(self):
        t = self.connect()
        t.write("guest\n")
        self.expect('TIMEOUT', t, timeout=65)
        t.close()

    def test_guest_timeout(self):
        t = self.connect()
        t.write("guest\n")
        self.expect('TIMEOUT', t, timeout=65)
        t.close()

class TestIdleTimeout(Test):
    def test_idle_logout(self):
        t = self.connect_as_guest()
        self.expect("**** Auto-logout", t, timeout=60*60*2)
        t.close()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

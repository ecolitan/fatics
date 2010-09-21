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

class TestPassword(Test):
    def test_password(self):
        t = self.connect_as_guest()
        t.write('password foo bar\r\n')
        self.expect("only for registered", t)
        self.close(t)

        t = self.connect_as_admin()
        t.write('password wrongpass test\r\n')
        self.expect("Incorrect", t)

        t.write('password %s test\r\n' % admin_passwd)
        self.expect("changed", t)
        self.close(t)

        t = self.connect()
        t.write("admin\r\ntest\r\n")
        self.expect("fics%", t)
        t.write("password test %s\r\n" % admin_passwd)
        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

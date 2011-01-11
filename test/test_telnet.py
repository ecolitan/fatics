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

import os

class TelnetTest(Test):
    def test_telnet_interrupt(self):
        t = self.connect_as_guest()
        # IAC Interrupt Process should break connection
        os.write(t.fileno(), chr(255) + chr(244))
        self.expect_EOF(t)
        t.close()

    def _option_callback(self, sock, cmd, option):
        self._last_cmd = cmd + option

    def test_hide_passwd(self):
        t = self.connect()
        self._last_cmd = None
        t.set_option_negotiation_callback(self._option_callback)
        self.expect('login: ', t)
        self.assert_(self._last_cmd == None)
        t.write('admin\n')
        self.expect_re('password:.*', t)
        self.assert_(self._last_cmd == telnetlib.WILL + telnetlib.ECHO)
        t.write(admin_passwd + '\n')
        self.expect('**** Starting', t)
        self.assert_(self._last_cmd == telnetlib.WONT + telnetlib.ECHO)
        t.set_option_negotiation_callback(None)
        self.close(t)

    def test_tab(self):
        """ Check that a tab is converted to spaces. """
        t = self.connect_as_admin()
        t.write('t admin a\tb\n')
        self.expect('tells you: a    b', t)
        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

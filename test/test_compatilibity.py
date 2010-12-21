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

compatibility_port = 5003

class TestCompatibility(Test):
    """ Test the compatibility port used for old clients that don't support
    FatICS's newline order and non-ASCII characters. """
    def test_compatibility(self):
        t = telnetlib.Telnet(host, compatibility_port)
        self.expect('??? FatICS', t)
        t.write("guest\n\n")
        self.expect('fics% ', t)
        t.write('quit\n')
        self.expect('??? Thank you', t)
        t.close()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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

class TestCommand(Test):
    def test_command(self):
        t = self.connect_as_guest()
        t.write('badcommand\n')
        self.expect('Command not found', t)

        # abbreviate command
        t.write('fin\n')
        self.expect('Finger of ', t)

        # don't update idle time
        t.write('$$finger\n')
        self.expect('Finger of ', t)

        # commands are case-insensitive
        t.write('DATE\n')
        self.expect('Server time', t)

        # ignore extranous whitespace
        t.write(' \t  date  \t \n')
        self.expect('Server time', t)

        t.write('   \t \n')
        self.expect_not('Bad command', t)
        
        t.write('tell\n')
        self.expect('Usage: ', t)

        t.close()
    

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

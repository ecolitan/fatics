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

# GuestFXLR (++++) seeking 5 0 unrated blitz m ("play 37" to respond)

class TestSeek(Test):
    def test_seek_guest(self):
        t = self.connect_as('GuestABCD', '')

        t.write('seek 3 0\n')
        self.expect('GuestABCD(U) (++++) seeking 3 0 unrated blitz ("play 1" to respond)', t)
        self.expect('Your seek has been posted with index 1.', t)
        self.expect('(1 player saw the seek.)', t)

        t.write('seek 15+5\n')
        self.expect('GuestABCD(U) (++++) seeking 15 5 unrated standard ("play 2" to respond)', t)
        self.expect('Your seek has been posted with index 2.', t)
        self.expect('(1 player saw the seek.)', t)

        t.write('unseek\n')
        self.expect('Your seeks have been removed.', t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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

class TestWrap(Test):
    """ test word wrapping """
    def test_wrap(self):
        t = self.connect_as_guest('GuestABCD')
        t.write('t guestabcd Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.\n')
        self.expect('GuestABCD(U) tells you: Four score and seven years ago our fathers brought \r\n\\   forth on this continent, a new nation, conceived in Liberty, and dedicated \r\n\\   to the proposition that all men are created equal.', t)
        self.close(t)

    def test_nowrap(self):
        t = self.connect_as_guest('GuestABCD')
        t.write('iset nowrap 1\n')
        self.expect('nowrap set.', t)
        t.write('t guestabcd Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.\n')
        self.expect('GuestABCD(U) tells you: Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.\r\n', t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

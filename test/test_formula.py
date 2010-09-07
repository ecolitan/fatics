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

class TestFormula(Test):
    def test_formula_guest(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_guest()

        t.write('set formula !blitz && time > 1\n')
        self.expect('formula set to "!blitz && time > 1".', t)

        t2.write('match guestabcd 1 0\n')
        self.expect('Ignoring (formula)', t)
        self.expect('Match request does not meet formula', t2)

        t2.write('match guestabcd 2 1\n')
        self.expect('Issuing: ', t2)
        self.expect('Challenge: ', t)
        t2.write('withdraw\n')
        self.expect('withdraws', t)

        t2.write('match guestabcd 3 0\n')
        self.expect('Ignoring (formula)', t)
        self.expect('Match request does not meet formula', t2)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

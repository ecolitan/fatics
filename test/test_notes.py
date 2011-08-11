# -*- coding: utf-8 -*-
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

class TestNotes(Test):
    def test_notes_guest(self):
        t = self.connect_as_guest('GuestABCD')
        t.write("set 1 Jeg kan spise glas, det gør ikke ondt på mig.\n")
        self.expect('Note 1 set: Jeg kan spise glas, det gør ikke ondt på mig.', t)

        t.write('fi\n')
        self.expect(' 1: Jeg kan spise glas, det gør ikke ondt på mig.', t)

        t2 = self.connect_as_admin()
        t2.write('fi guestabcd\n')
        self.expect(' 1: Jeg kan spise glas, det gør ikke ondt på mig.', t2)
        self.close(t2)

        t.write('set 10 Meg tudom enni az üveget, nem lesz tőle bajom.\n')
        t.write('fi\n')
        self.expect(' 1: Jeg kan spise glas, det gør ikke ondt på mig.', t)
        self.expect(' 2:', t)
        self.expect(' 3:', t)
        self.expect(' 4:', t)
        self.expect(' 5:', t)
        self.expect(' 6:', t)
        self.expect(' 7:', t)
        self.expect(' 8:', t)
        self.expect(' 9:', t)
        self.expect('10: Meg tudom enni az üveget, nem lesz tőle bajom.', t)

        t.write('set 5 Я можу їсти шкло, й воно мені не пошкодить.\n')
        t.write('fi\n')
        self.expect(' 1: Jeg kan spise glas, det gør ikke ondt på mig.', t)
        self.expect(' 2:', t)
        self.expect(' 3:', t)
        self.expect(' 4:', t)
        self.expect(' 5: Я можу їсти шкло, й воно мені не пошкодить.', t)
        self.expect(' 6:', t)
        self.expect(' 7:', t)
        self.expect(' 8:', t)
        self.expect(' 9:', t)
        self.expect('10: Meg tudom enni az üveget, nem lesz tőle bajom.', t)

        t.write('set 10\n')
        self.expect('Note 10 unset', t)
        t.write('fi\n')
        self.expect_not('6:', t)

        self.close(t)
    
    def test_notes_persistence(self):
        t = self.connect_as_admin()

        t.write('set 1 The quick brown fox jumps over the lazy dog.\n')
        self.expect('Note 1 set: The quick brown fox jumps over the lazy dog.', t)
        t.write('fi\n')
        self.expect(' 1: The quick brown fox jumps over the lazy dog.', t)

        self.close(t)

        t = self.connect_as_guest()
        t.write('fi admin\n')
        self.expect(' 1: The quick brown fox jumps over the lazy dog.', t)
        self.close(t)

        t = self.connect_as_admin()
        t.write('set 1\n')
        self.expect('Note 1 unset', t)

        t.write('fi\n')
        self.expect_not('1:', t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

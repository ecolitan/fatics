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

from datetime import datetime

from test import *

class TestHistory(Test):
    def test_history_guest(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as('GuestEFGH', '')

        t.write('history\n')
        self.expect('GuestABCD has no history games', t)

        t.write('match GuestEFGH 2 12 white u\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')

        self.expect('Creating:', t)
        self.expect('Creating:', t2)
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        t.write('e4\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        t2.write('c5\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        t.write('resign\n')

        self.expect('GuestABCD resigns', t)
        self.expect('GuestABCD resigns', t2)

        t.write('match GuestEFGH 15 5 black u\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        t.write('draw\n')
        t2.write('draw\n')
        self.expect('1/2-1/2', t)
        self.expect('1/2-1/2', t2)


        t.write('history\n')
        today = datetime.utcnow().date()
        self.expect('History for GuestABCD:\r\n                  Opponent      Type         ECO End Date', t)
        self.expect(' 0: - ++++ W ++++ GuestEFGH     [bnu  2  12] B20 Res %s' % today, t)
        self.expect(' 1: = ++++ B ++++ GuestEFGH     [snu 15   5] A00 Agr %s' % today, t)

        t2.write('hi\n')
        self.expect('History for GuestEFGH:\r\n                  Opponent      Type         ECO End Date', t2)
        self.expect(' 0: + ++++ B ++++ GuestABCD     [bnu  2  12] B20 Res ', t2)
        self.expect(' 1: = ++++ W ++++ GuestABCD     [snu 15   5] A00 Agr %s' % today, t2)

        t.write('hi GuestEFGH\n')
        self.expect('History for GuestEFGH:\r\n                  Opponent      Type         ECO End Date', t)
        self.expect(' 0: + ++++ B ++++ GuestABCD     [bnu  2  12] B20 Res ', t)
        self.expect(' 1: = ++++ W ++++ GuestABCD     [snu 15   5] A00 Agr %s' % today, t)

        self.close(t)
        self.close(t2)

    def test_history_user(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('GuestABCD', '')

        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('aclearhist admin\n')
        t.write('history\n')
        self.expect('admin has no history games', t)

        t.write('match GuestABCD 15 0 black u\n')
        self.expect('Challenge:', t2)
        t2.write('a\n')

        self.expect('Creating:', t)
        self.expect('Creating:', t2)
        t2.write('c4\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        t.write('resign\n')

        self.expect('admin resigns', t)
        self.expect('admin resigns', t2)

        self.close(t)

        t2.write('history admin\n')
        self.expect('History for admin:\r\n                  Opponent      Type         ECO End Date', t2)
        self.expect(' 0: - ---- B ++++ GuestABCD     [snu 15   0] A10 Res ', t2)
        self.close(t2)

        t = self.connect_as_admin()
        t.write('history\n')
        self.expect('History for admin:\r\n                  Opponent      Type         ECO End Date', t)
        self.expect(' 0: - ---- B ++++ GuestABCD     [snu 15   0] A10 Res ', t)

        t.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t)

        self.close(t)

    def test_alternating_colors(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as('GuestEFGH', '')

        t2.write('match GuestABCD 3 1 chess black u\n')
        self.expect('Challenge:', t)
        t.write('a\n')
        self.expect('Creating:', t)
        self.expect('Creating:', t2)
        t.write('resign\n')
        self.expect('GuestABCD resigns', t)
        self.expect('GuestABCD resigns', t2)

        for i in range(1, 11):
            t2.write('rematch\n')
            self.expect('Challenge:', t)
            t.write('a\n')
            self.expect('Creating:', t)
            self.expect('Creating:', t2)
            t.write('resign\n')
            self.expect('GuestABCD resigns', t)
            self.expect('GuestABCD resigns', t2)

        t.write('hi\n')
        self.expect(' 1: - ++++ B ++++ GuestEFGH     [bnu  3   1] A00 Res ', t)
        self.expect(' 2: - ++++ W ++++ GuestEFGH     [bnu  3   1] A00 Res ', t)
        self.expect(' 3: - ++++ B ++++ GuestEFGH     [bnu  3   1] A00 Res ', t)
        self.expect(' 4: - ++++ W ++++ GuestEFGH     [bnu  3   1] A00 Res ', t)
        self.expect(' 5: - ++++ B ++++ GuestEFGH     [bnu  3   1] A00 Res ', t)
        self.expect(' 6: - ++++ W ++++ GuestEFGH     [bnu  3   1] A00 Res ', t)
        self.expect(' 7: - ++++ B ++++ GuestEFGH     [bnu  3   1] A00 Res ', t)
        self.expect(' 8: - ++++ W ++++ GuestEFGH     [bnu  3   1] A00 Res ', t)
        self.expect(' 9: - ++++ B ++++ GuestEFGH     [bnu  3   1] A00 Res ', t)
        self.expect('10: - ++++ W ++++ GuestEFGH     [bnu  3   1] A00 Res ', t)

        t.write('hi GuestEFGH\n')
        self.expect(' 1: + ++++ W ++++ GuestABCD     [bnu  3   1] A00 Res ', t)
        self.expect(' 2: + ++++ B ++++ GuestABCD     [bnu  3   1] A00 Res ', t)
        self.expect(' 3: + ++++ W ++++ GuestABCD     [bnu  3   1] A00 Res ', t)
        self.expect(' 4: + ++++ B ++++ GuestABCD     [bnu  3   1] A00 Res ', t)
        self.expect(' 5: + ++++ W ++++ GuestABCD     [bnu  3   1] A00 Res ', t)
        self.expect(' 6: + ++++ B ++++ GuestABCD     [bnu  3   1] A00 Res ', t)
        self.expect(' 7: + ++++ W ++++ GuestABCD     [bnu  3   1] A00 Res ', t)
        self.expect(' 8: + ++++ B ++++ GuestABCD     [bnu  3   1] A00 Res ', t)
        self.expect(' 9: + ++++ W ++++ GuestABCD     [bnu  3   1] A00 Res ', t)
        self.expect('10: + ++++ B ++++ GuestABCD     [bnu  3   1] A00 Res ', t)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

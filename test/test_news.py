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

class TestNews(Test):
    def test_news_guest(self):
        t = self.connect_as_guest()
        t.write("news\n")
        self.expect("There is no news", t)

        t.write("cnewsi test\n")
        self.expect("cnewsi: Command not found", t)

        self.close(t)

    def test_news(self):
        t = self.connect_as_admin()
        t.write("news\n")
        self.expect("There is no news", t)

        t.write("cnewsi This is a test news item that is more than 45 characters long.\n")
        self.expect('The news title exceeds', t)

        t.write("cnewsi This is a test news item.\n")
        m = self.expect_re(r'Created news item (\d+)', t)
        news_id = int(m.group(1))

        t.write('news\n')
        self.expect('%4d (%s) This is a test news item.\r\n' % (news_id, datetime.utcnow().date()), t)

        t.write('cnewse -1\n')
        self.expect('News item -1 not found', t)
        t.write('cnewse 0\n')
        self.expect('News item 0 not found', t)
        t.write('cnewse %d\n' % news_id)
        self.expect('Deleted news item %d' % news_id, t)

        t.write('news\n')
        self.expect('There is no news.', t)
        self.close(t)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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

import time

from datetime import datetime

from test import *

class TestNews(Test):
    def test_news_guest(self):
        t = self.connect_as_guest()
        t.write("news\n")
        self.expect_re(r"(?:There is no news|Index of the last few news items:)", t)

        t.write("cnewsi test\n")
        self.expect("cnewsi: Command not found", t)

        self.close(t)

    def test_news(self):
        t = self.connect_as_admin()
        t.write("news\n")
        self.expect_re(r"(?:There is no news|Index of the last few news items:)", t)

        t.write("cnewsi This is a test news item that is more than 45 characters long.\n")
        self.expect('The news title exceeds', t)

        t.write("cnewsi This is a test news item.\n")
        m = self.expect_re(r'Created news item (\d+)', t)
        news_id = int(m.group(1))

        t.write('news\n')
        self.expect('%4d (%s) This is a test news item.\r\n' % (news_id, datetime.utcnow().date()), t)

        t.write('cnewsd %d\n' % news_id)
        self.expect('News item %d not found or already has no lines.' % news_id, t)

        t.write('cnewse -1\n')
        self.expect('News item -1 not found', t)
        t.write('cnewse 0\n')
        self.expect('News item 0 not found', t)
        t.write('cnewse %d\n' % news_id)
        self.expect('Deleted news item %d' % news_id, t)
        t.write('news %d\n' % news_id)
        self.expect('News item %d not found.' % news_id, t)
        t.write('cnewse %d\n' % news_id)
        self.expect('News item %d not found.' % news_id, t)

        t.write('news\n')
        self.expect_re(r"(?:There is no news|Index of the last few news items:)", t)
        self.expect_not('^%d' % news_id, t)
        self.close(t)

    def test_news_text(self):
        t = self.connect_as_admin()
        t.write('cnewsi Test news item title.\n')
        m = self.expect_re(r'Created news item (\d+)', t)
        news_id = int(m.group(1))

        t.write('news %d\n' % news_id)
        self.expect('%4d (%s) Test news item title.\r\n\r\n\r\n\r\nPosted by admin.' % (
            news_id, datetime.utcnow().date()), t)

        t.write('cnewsf %d Test line 1.\n' % news_id)
        self.expect('News item %d updated.' % news_id, t)
        t.write('cnewsf %d Test line 2.\n' % news_id)
        self.expect('News item %d updated.' % news_id, t)
        t.write('cnewsf %d\n' % news_id)
        self.expect('News item %d updated.' % news_id, t)
        t.write('cnewsf %d Last line.\n' % news_id)
        self.expect('News item %d updated.' % news_id, t)

        t.write('news %d\n' % news_id)
        self.expect('%4d (%s) Test news item title.\r\n\r\nTest line 1.\r\nTest line 2.\r\n\r\nLast line.\r\n\r\nPosted by admin.' % (
            news_id, datetime.utcnow().date()), t)

        t.write('cnewsd %d\n' % news_id)
        self.expect('Deleted last line of news item %d.' % news_id, t)
        t.write('cnewsd %d\n' % news_id)
        self.expect('Deleted last line of news item %d.' % news_id, t)
        t.write('cnewsf %d Test line 3.\n' % news_id)
        self.expect('News item %d updated.' % news_id, t)

        t.write('news %d\n' % news_id)
        self.expect('%4d (%s) Test news item title.\r\n\r\nTest line 1.\r\nTest line 2.\r\nTest line 3.\r\n\r\nPosted by admin.' % (
            news_id, datetime.utcnow().date()), t)

        t.write('cnewse %d\n' % news_id)
        self.expect('Deleted news item %d.' % news_id, t)

        self.close(t)

    @with_player('TestPlayer')
    def test_news_notification(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('TestPlayer')
        today = datetime.utcnow().date()

        t.write('cnewsi News item 1.\n')
        m = self.expect_re(r'Created news item (\d+)', t)
        news_id1 = int(m.group(1))

        self.close(t2)
        time.sleep(1)

        t.write('cnewsi News item 2.\n')
        m = self.expect_re(r'Created news item (\d+)', t)
        news_id2 = int(m.group(1))

        t2 = self.connect()
        t2.write('testplayer\n%s\n' % tpasswd)
        self.expect('There is 1 new news item since your last login:\r\n%4d (%s) News item 2.\r\n' %
            (news_id2, today), t2)
        self.close(t2)
        time.sleep(1)

        t.write('cnewsi News item 3.\n')
        m = self.expect_re(r'Created news item (\d+)', t)
        news_id3 = int(m.group(1))
        t.write('cnewsi News item 4.\n')
        m = self.expect_re(r'Created news item (\d+)', t)
        news_id4 = int(m.group(1))

        t2 = self.connect()
        t2.write('testplayer\n%s\n' % tpasswd)
        self.expect('There are 2 new news items since your last login:\r\n%4d (%s) News item 3.\r\n%4d (%s) News item 4.\r\n' %
            (news_id3, today, news_id4, today), t2)
        self.close(t2)

        for news_id in [news_id1, news_id2, news_id3, news_id4]:
            t.write('cnewse %d\n' % news_id)
            self.expect('Deleted news item %d.' % news_id, t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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

class TestNotify(Test):
    def test_notify_guest(self):
        t = self.connect_as_user('GuestABCD', '')
        t.write('+not admin\n')
        self.expect("admin added to your notify list", t)

        t.write('=not\n')
        self.expect('notify list: 1 name', t)
        self.expect('admin', t)

        t2 = self.connect_as_admin()
        self.expect('Notification: admin has arrived', t)

        t2.write('+not guest\n')
        self.expect("GuestABCD added to your notify list", t2)

        self.close(t)
        self.expect('Notification: GuestABCD has departed', t2)
        t = self.connect_as_user('GuestABCD', '')
        self.expect('Notification: GuestABCD has arrived', t2)

        self.close(t)
        self.close(t2)

    def test_bad_notify(self):
        t = self.connect_as_admin()
        t.write('+not testplayer\n')
        self.expect('There is no player matching the name "testplayer"', t)
        self.close(t)

    def test_notify_user(self):
        self.adduser('TestPlayer', 'test')
        try:
            t = self.connect_as_admin()

            t.write('+notify testplayer\n')
            self.expect("TestPlayer added to your notify list", t)

            t.write('+not testplayer\n')
            self.expect("TestPlayer is already on your notify list", t)

            t2 = self.connect_as_user('testplayer', 'test')
            self.expect("Notification: TestPlayer has arrived", t)

            self.close(t)

            t = self.connect()
            t.write('admin\n%s\n' % admin_passwd)
            self.expect('Present company includes: TestPlayer', t)

            self.close(t2)
            self.expect("Notification: TestPlayer has departed", t)

            t.write('-NOTIFY testplayer\n')
            self.expect('TestPlayer removed from your notify list', t)

            t.write('-not testplayer\n')
            self.expect('TestPlayer is not on your notify list', t)

            t2 = self.connect_as_user('testplayer', 'test')
            self.expect_not("TestPlayer", t)

            self.close(t2)
            self.close(t)
        finally:
            self.deluser('TestPlayer')

class TestSummon(Test):
    def test_summon(self):
        self.adduser('TestPlayer', 'test')
        t = self.connect_as_admin()
        t2 = self.connect_as_user('testplayer', 'test')
        t.write('summon\n')
        self.expect('Usage:', t)

        t.write('summo admin\n')
        self.expect('summon yourself', t)

        t.write('summo testp\n')
        self.expect('Summoning sent to "TestPlayer".\r\n', t)
        self.expect('admin needs to speak to you', t2)

        t.write('+cen testplayer\n')
        t2.write('+cen admin\n')
        t.write('summo testp\n')
        self.expect('admin needs to speak to you', t2)
        t2.write('summon admin\n')
        self.expect('admin is censoring you.\r\n', t2)


class TestZnotify(Test):
    def test_znotify(self):
        self.adduser('TestPlayer', 'test')
        try:
            t = self.connect_as_admin()
            t.write('znotify\n')
            self.expect('No one from your notify list is logged on.\r\nNo one logged in has you on their notify list.', t)

            t.write('+notify testplayer\n')
            t2 = self.connect_as_user('testplayer', 'test')
            t3 = self.connect_as_user('GuestABCD', '')
            t3.write('+notify admin\n')
            self.expect('admin added to your notify list', t3)

            t.write('znot\n')
            self.expect('Present company on your notify list:\r\n   TestPlayer\r\nThe following players have you on their notify list:\r\n   GuestABCD', t)

            t.write('-notify testplayer\n')
            self.close(t2)
            self.close(t3)
        finally:
            self.deluser('TestPlayer')

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

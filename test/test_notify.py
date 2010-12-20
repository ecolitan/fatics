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
        t = self.connect_as_guest('GuestABCD')
        t.write('+not admin\n')
        self.expect('Only registered players', t)

        t.write('=not\n')
        self.expect('Only registered players', t)

        t2 = self.connect_as_admin()
        t2.write('+not guest\n')
        self.expect('You cannot add an unregistered', t2)

        self.close(t)
        self.close(t2)

    def test_bad_notify(self):
        t = self.connect_as_admin()
        t.write('+not testplayer\n')
        self.expect('There is no player matching the name "testplayer"', t)
        t.write('-notify testplayer\n')
        self.expect('There is no player matching the name "testplayer"', t)
        t.write('+not admin\n')
        self.expect("notify yourself.", t)
        self.close(t)

    @with_player('TestPlayer', 'test')
    def test_notify_user(self):
        t = self.connect_as_admin()

        t.write('=not\n')
        self.expect('notify list: 0 names', t)

        t.write('+notify testplayer\n')
        self.expect("TestPlayer added to your notify list", t)

        t.write('=not\n')
        self.expect('notify list: 1 name', t)
        self.expect('TestPlayer', t)

        t.write('+not testplayer\n')
        self.expect("TestPlayer is already on your notify list", t)

        t2 = self.connect_as('testplayer', 'test')
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

        t2 = self.connect_as('testplayer', 'test')
        self.expect_not("TestPlayer", t)

        self.close(t2)
        self.close(t)

    @with_player('TestPlayer', 'test')
    def test_notifiedby(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'test')

        t2.write('set notifiedby 1\n')
        self.expect('You will now hear if people notify you', t2)

        t.write('+notify testplayer\n')
        self.expect("TestPlayer added to your notify list", t)
        self.expect("You have been added to the notify list of admin.", t2)

        self.close(t)
        self.expect("Notification: admin has departed and isn't on your notify list.", t2)


        t = self.connect_as_admin()
        self.expect("Notification: admin has arrived and isn't on your notify list.", t2)

        t2.write('quit\n')
        self.expect('The following players were notified of your departure: admin', t2)
        t2.close()

        t2 = self.connect()
        t2.write('testplayer\ntest\n')
        self.expect('The following players were notified of your arrival: admin', t2)

        t.write('-not testplayer\n')
        self.expect('TestPlayer removed from your notify list', t)

        self.close(t2)
        self.close(t)

class TestIdlenotify(Test):
    def test_idlenotify_guest(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()

        t.write('+idlenot admin\n')
        self.expect('admin added to your idlenotify list.', t)
        t.write('=idle\n')
        self.expect('-- idlenotify list: 1 name --', t)
        self.expect('admin', t)
        t.write('-idlenot admin\n')
        self.expect('admin removed from your idlenotify list.', t)
        t.write('+idlenot admin\n')
        self.expect('admin added to your idlenotify list.', t)

        self.expect_not('Notification: ', t)

        t2.write('\n')
        self.expect('Notification: admin has unidled.', t)

        t.write('-idlenot admin\n')
        self.expect('admin is not on your idlenotify list.', t)

        self.close(t)
        self.close(t2)

    def test_idlenotify_depart(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_admin()

        t.write('+idlenot admin\n')
        self.expect('admin added to your idlenotify list.', t)

        t2.close()
        self.expect('admin, whom you were idlenotifying, has departed.', t)

        self.close(t)

    def test_idlenotify_depart_2(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_admin()

        t.write('+idlenot admin\n')
        self.expect('admin added to your idlenotify list.', t)

        # should handle disonnect gracefully
        t.close()
        self.close(t2)

    def test_bad_idlenotify(self):
        t = self.connect_as_guest('GuestEFGH')
        t.write('+idlenot 33\n')
        self.expect('"33" is not a valid handle.', t)
        t.write('+idlenot admin\n')
        self.expect('No player named "admin" is online', t)
        t.write('+idlenot guestefgh\n')
        self.expect("idlenotify yourself.", t)
        t.write('-idlenotify testplayer\n')
        self.expect('No player named "testplayer" is online', t)
        self.close(t)

class TestSummon(Test):
    @with_player('TestPlayer', 'test')
    def test_summon(self):
        t = self.connect_as_admin()

        t.write('summon testplayer\n')
        self.expect('No player named "testplayer" is online', t)
        t.write('summon\n')
        self.expect('Usage:', t)
        t.write('summo admin\n')
        self.expect('summon yourself', t)

        t2 = self.connect_as('testplayer', 'test')

        t.write('summo testp\n')
        self.expect('Summoning sent to "TestPlayer".\r\n', t)
        self.expect('admin needs to speak to you', t2)

        t2.write('\n')
        self.expect('Notification: TestPlayer has unidled.', t)

        t.write('+cen testplayer\n')
        t2.write('+cen admin\n')
        t.write('summo testp\n')
        self.expect('admin needs to speak to you', t2)
        t2.write('summon admin\n')
        self.expect('admin is censoring you.\r\n', t2)

        self.close(t)
        self.close(t2)

class TestZnotify(Test):
    @with_player('TestPlayer', 'test')
    @with_player('testtwo', 'test')
    def test_znotify(self):
        t = self.connect_as_admin()
        t.write('znotify\n')
        self.expect('No one from your notify list is logged on.\r\nNo one logged in has you on their notify list.', t)

        t.write('+notify testplayer\n')
        t2 = self.connect_as('testplayer', 'test')
        t3 = self.connect_as('testtwo', 'test')
        t3.write('+notify admin\n')
        self.expect('admin added to your notify list', t3)

        t.write('znot\n')
        self.expect('Present company on your notify list:\r\n   TestPlayer\r\nThe following players have you on their notify list:\r\n   testtwo', t)

        t.write('-notify testplayer\n')
        self.close(t2)
        self.close(t3)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

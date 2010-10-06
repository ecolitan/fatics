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

class CommandTest(Test):
    def test_addplayer_and_remplayer(self):
        t = self.connect_as_admin()
        t.write('addplayer TestPlayer nobody@example.com Foo Bar\n')
        self.expect('Added: >TestPlayer< >Foo Bar< >nobody@example.com<', t)
        t.write('addplayer testplayer nobody@example.com Foo Bar\n')
        self.expect('already registered', t)
        t.write('remplayer testplayer\n')
        self.expect('Player TestPlayer removed.', t)
        self.close(t)

    def test_announce(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()

        t.write("announce foo bar baz\n")
        self.expect('(1) **ANNOUNCEMENT** from admin: foo bar baz', t)
        self.expect('**ANNOUNCEMENT** from admin: foo bar baz', t2)
        self.close(t)
        self.close(t2)

    @with_player('testplayer', 'passwd')
    def test_annunreg(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()
        t3 = self.connect_as_guest()
        t4 = self.connect_as('testplayer', 'passwd')

        t.write("annunreg x Y z\n")
        self.expect('(2) **UNREG ANNOUNCEMENT** from admin: x Y z', t)
        self.expect('**UNREG ANNOUNCEMENT** from admin: x Y z', t2)
        self.expect('**UNREG ANNOUNCEMENT** from admin: x Y z', t3)
        self.expect_not('**UNREG ANNOUNCEMENT**', t4)
        self.close(t)
        self.close(t2)
        self.close(t3)
        self.close(t4)

    def test_nuke(self):
        t = self.connect_as_admin()

        t.write('nuke 123\n')
        self.expect('not a valid handle', t)

        t.write('nuke guesttest\n')
        self.expect('no player matching', t)

        t2 = self.connect_as('GuestTest', '')
        t.write('nuke guesttest\n')
        self.expect('You have been kicked out', t2)
        self.expect('Nuked: GuestTest', t)
        t2.close()

        t2 = self.connect_as('GuestTest', '')
        t.write('asetadmin guesttest 100\n')
        t2.write('nuke admin\n')
        self.expect('need a higher adminlevel', t2)
        self.close(t2)

        self.close(t)

    @with_player('TestPlayer', 'testpass')
    def test_nuke_registered(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t.write('nuke testplayer\n')
        self.expect('You have been kicked out', t2)
        self.expect('Nuked: TestPlayer', t)

        t.write('showcomment testplayer\n')
        self.expect_re('admin at .*: Nuked', t)

        self.close(t)
        self.close(t2)

    def test_asetpass(self):
        self.adduser('testplayer', 'passwd')
        t = self.connect_as_admin()

        t2 = self.connect_as('GuestTest', '')
        t.write('asetpass GuestTest pass\n')
        self.expect('cannot set the password', t)
        self.close(t2)

        t2 = self.connect_as('testplayer', 'passwd')
        t.write('asetpass testplayer test\n')
        self.expect("Password of testplayer changed", t)
        self.expect("admin has changed your password", t2)
        self.close(t)
        self.close(t2)

        t2 = self.connect()
        t2.write('testplayer\ntest\n')
        self.expect('fics%', t2)
        self.close(t2)
        self.deluser('testplayer')


    def test_asetadmin(self):
        self.adduser('testplayer', 'passwd')
        self.adduser('testtwo', 'passwd')
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'passwd')
        t.write('asetadmin testplayer 100\n')
        self.expect('Admin level of testplayer set to 100.', t)
        self.close(t)

        self.expect('admin has set your admin level to 100.', t2)
        t2.write('asetadmin admin 100\n')
        self.expect('You can only set the adminlevel for players below', t2)
        t2.write('asetadmin testplayer 1000\n')
        self.expect("You can't change your own", t2)

        t2.write('asetadmin testtwo 100\n')
        self.expect('''You can't promote''', t2)

        t2.write('asetadmin testtwo 50\n')
        self.expect('Admin level of testtwo set', t2)
        self.close(t2)
        self.deluser('testplayer')
        self.deluser('testtwo')

    def test_asetemail(self):
        t = self.connect_as_admin()
        t.write('addplayer TestPlayer nobody@example.com Foo Bar\n')
        m = self.expect_re('Added: >TestPlayer< >Foo Bar< >nobody@example.com< >(.*)<\r\n', t)
        t2 = self.connect_as('testplayer', m.group(1))

        t.write('f testplayer\n')
        self.expect('nobody@example.com', t)

        t.write('asetemail testplayer new@example.org\n')
        self.expect('Email address of TestPlayer changed to "new@example.org".', t)
        self.expect('admin has changed your email address to "new@example.org".', t2)

        t.write('showcomment testplayer\n')
        self.expect_re('admin at .*: Changed email address from "nobody@example.com" to "new@example.org".', t)

        t.write('f testplayer\n')
        self.expect('new@example.org', t)

        self.close(t2)

        # check again to be sure the change was committed to the DB
        t.write('f testplayer\n')
        self.expect('new@example.org', t)
        t.write('remplayer testplayer\n')
        self.expect('Player TestPlayer removed.', t)

        self.close(t)

    @with_player('TestPlayer', 'testpass')
    def test_asetemail_bad(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('GuestABCD', '')

        t.write('asetemail guestabcd nobody@example.org\n')
        self.expect('You can only set the email for registered', t)
        t.write('asetemail admin test@example.com\n')
        self.expect('You need a higher adminlevel', t)
        t.write('asetemail testplayer test\n')
        self.expect('That does not look like an email address.', t)

        self.close(t)
        self.close(t2)

    def test_asetrating(self):
        t = self.connect_as_admin()
        t.write('asetrating admin blitz chess 2000 200 .005 100 75 35\n')
        self.expect('Set blitz chess rating for admin.\r\n', t)
        self.close(t)

        t = self.connect_as_admin()
        t.write('finger admin\n')
        self.expect('blitz                    2000   200  0.005000     210', t)
        t.write('asetrating admin blitz chess 0 0 0 0 0 0\n')
        self.expect('Cleared blitz chess rating for admin.\r\n', t)
        t.write('finger admin\n')
        self.expect_not('blitz chess', t)
        self.close(t)

    def test_aclearhistory(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_admin()
        t.write('match admin white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        t2.write('resign\n')
        self.expect('admin resigns', t)
        self.expect('admin resigns', t2)

        t.write('history admin\n')
        self.expect('History for admin:', t)

        t2.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t2)

        t.write('history admin\n')
        self.expect('admin has no history games.', t)

        t2.write('aclearhist guestabcd\n')
        self.expect('History of GuestABCD cleared.', t2)

        self.close(t)
        self.close(t2)

    @with_player('TestPlayer', 'testpass')
    def test_pose(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('GuestABCD', '')

        t.write('pose testplayer test\n')
        self.expect('No player named "testplayer" is online', t)

        t.write('pose guestabcd finger testplay\n')
        self.expect('Command issued as GuestABCD.', t)
        self.expect('admin has issued the following command on your behalf: finger testplay', t2)
        self.expect('Finger of TestPlayer:', t2)

        t.write('pose guestabcd badcommand\n')
        self.expect('badcommand: Command not found', t2)
        self.close(t2)

        t2 = self.connect_as('testplayer', 'testpass')
        t.write('pose testplayer shout disregard that\n')
        self.expect('TestPlayer shouts: disregard that', t)

        self.close(t)
        self.close(t2)

    def test_admin(self):
        t = self.connect_as_admin()
        t.write('admin\n')
        self.expect('(*) is now not shown', t)
        t.write('f admin\n')
        self.expect('Finger of admin:', t)
        self.close(t)

        t = self.connect_as_admin()
        t.write('f admin\n')
        self.expect('Finger of admin:', t)
        t.write('admin\n')
        self.expect('(*) is now shown', t)
        t.write('f admin\n')
        self.expect('Finger of admin(*):', t)

        self.close(t)

class PermissionsTest(Test):
    def test_permissions(self):
        t = self.connect_as_guest()
        t.write('asetpass admin test\n')
        self.expect('asetpass: Command not found', t)
        self.close(t)

class CommentTest(Test):
    @with_player('TestPlayer', 'testpass')
    def test_comment(self):
        t = self.connect_as_admin()

        t.write('showcomment testplayer\n')
        self.expect('There are no comments for TestPlayer.', t)

        t.write('addcomment testplay This is a test comment.\n')
        self.expect('Comment added for TestPlayer.', t)

        t.write('showcomment testplayer\n')
        self.expect_re('admin at .*: This is a test comment.', t)

        self.close(t)

    def test_comment_bad(self):
        t = self.connect_as_admin()
        t.write('addcomment nosuchplayer test\n')
        self.expect('There is no player matching the name "nosuchplayer".', t)
        t.write('showcomment nosuchplayer\n')
        self.expect('There is no player matching the name "nosuchplayer".', t)

        t.write('addcomment admin\n')
        self.expect('Usage:', t)

        t2 = self.connect_as('GuestABCD', '')
        t.write('addcomment  guestabcd test\n')
        self.expect('Unregistered players cannot have comments.', t)
        t.write('showcomment guestabcd\n')
        self.expect('Unregistered players cannot have comments.', t)
        self.close(t2)

        self.close(t)


class AreloadTest(Test):
    def runTest(self):
        self.skip('not stable')
        t = self.connect()
        t.write('areload\n')
        self.expect('reloaded online', t, "server reload")
        t.close()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

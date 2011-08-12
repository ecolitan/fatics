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

class TestChannel(Test):
    def test_channel_guest(self):
        t = self.connect_as_guest()

        # guests should be in 53 by default
        t.write('+ch 53\n')
        self.expect('is already on your channel list', t)

        t.write('+ch 1\n')
        self.expect("[1] added to your channel list", t)

        t.write('t 1 foo bar baz\n')
        self.expect("(1): foo bar baz", t)

        t.write('=ch\n')
        self.expect('channel list: 3 channels', t)
        self.expect('1 4 53', t)

        t.write('-ch 1\n')
        self.expect("[1] removed from your channel list", t)

        t.write('-ch 1\n')
        self.expect("[1] is not on your channel list", t)

        t.write('t 1 foo bar baz\n')
        self.expect("not in channel 1", t)

        t.write('+ch 0\n')
        self.expect("Only admins can join channel 0.", t)

        self.close(t)

    def test_channel_admin(self):
        t = self.connect_as_admin()

        t.write(', foo bar\n')
        self.expect("No previous channel", t)

        t.write('-ch 100\n')

        t.write('+ch 100\n')
        self.expect("[100] added to your channel list", t)

        t.write('t 100 foo bar baz\n')
        self.expect("(100): foo bar baz", t)

        t.write(', a b c d\n')
        self.expect("(100): a b c d", t)

        t.write('+ch foo\n')
        self.expect("must be a number", t)

        t.write('+ch -1\n')
        self.expect("Invalid channel", t)

        t.write('+ch 10000000000\n')
        self.expect("Invalid channel", t)

        t.write('-ch 10000000000\n')
        self.expect("Invalid channel", t)

        self.close(t)

        t = self.connect_as_admin()

        t.write('=ch\n')
        self.expect('channel list: 1 channel', t)

        t.write('+ch 100\n')
        self.expect('is already on your channel list', t)

        t.write('-ch 100\n')
        self.expect("[100] removed from your channel list", t)
        self.close(t)

        t = self.connect_as_admin()
        t.write('-ch 100\n')
        self.expect("is not on your channel list", t)

        self.close(t)

    def test_channel_admin_ch0(self):
        t = self.connect_as_admin()
        t.write('+ch 0\n')
        self.expect("[0] added to your channel list", t)
        t.write('inch 0\n')
        self.expect_re(r'0: .*admin', t)
        self.close(t)

        # XXX want to do a server restart here to check whether
        # the value is stored correctly in the DB

        t = self.connect_as_admin()
        t.write('inch 0\n')
        self.expect_re(r'0: .*admin', t)
        t.write('-ch 0\n')
        self.expect("[0] removed from your channel list", t)
        self.close(t)

    def test_chanoff_var(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_guest()

        t.write('+ch 1000\n')
        self.expect('[1000] added to your channel list.', t)
        t2.write('+ch 1000\n')
        self.expect('[1000] added to your channel list.', t2)

        t.write('t 1000 test 1\n')
        self.expect('test 1', t2)

        t2.write('set chanoff 1\n')
        self.expect('You will not hear channel tells.', t2)
        t.write('t 1000 test 2\n')
        self.expect_not('test 2', t2)

        t2.write('set chanoff 0\n')
        self.expect('You will now hear channel tells.', t2)
        t.write('t 1000 test 3\n')
        self.expect('test 3', t2)

        self.close(t)
        self.close(t2)

class TestChannelOwnership(Test):
    def test_channel_owner(self):
        t = self.connect_as_admin()
        t.write('+ch 1024\n')
        self.expect('You are now the owner of channel 1024.', t)
        self.expect('[1024] added to your channel list.', t)
        t.write('-ch 1024\n')
        self.expect('You are no longer an owner of channel 1024.', t)
        self.expect('[1024] removed from your channel list.', t)
        self.close(t)

    @with_player('TestPlayer')
    def test_channel_ownership_limit(self):
        t = self.connect_as('TestPlayer')
        for i in range(5000, 5008):
            t.write('+ch %d\n' % i)
            self.expect('You are now the owner of channel %d.' % i, t)
            self.expect('[%d] added to your channel list.' % i, t)

        t.write('+ch 5008\n')
        self.expect('You cannot own more than 8 channels.', t)

        for i in range(5000, 5008):
            t.write('-ch %d\n' % i)
            self.expect('You are no longer an owner of channel %d.' % i, t)
            self.expect('[%d] removed from your channel list.' % i, t)

        self.close(t)

    def test_channel_owner_guests(self):
        t = self.connect_as_guest()
        t.write('+ch 1024\n')
        self.expect('Only registered players can join channels 1024 and above.', t)
        self.close(t)

class TestKick(Test):
    @with_player('TestPlayer')
    def test_kick(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer')
        t.write('=ch\n')
        t.write('+ch 1024\n')
        self.expect('You are now the owner of channel 1024.', t)
        self.expect('[1024] added to your channel list.', t)
        t.write('chkick 1024 testplayer\n')
        self.expect('TestPlayer is not in channel 1024.', t)

        t2.write('+ch 1024\n')
        self.expect('[1024] added to your channel list.', t2)
        t.write('chkick 1024 testplayer\n')
        self.expect('admin(*)(1024): *** Kicked out TestPlayer. ***', t)
        self.expect('*** You have been kicked out of channel 1024 by admin. ***', t2)

        t.write('-ch 1024\n')
        self.expect('You are no longer an owner of channel 1024.', t)
        self.expect('[1024] removed from your channel list.', t)

        self.close(t)
        self.close(t2)

    def test_kick_guest(self):
        t = self.connect_as_guest('GuestARST')
        t2 = self.connect_as_admin()
        t.write('+ch 1\n')
        self.expect('[1] added', t)
        t2.write('+ch 1\n')
        self.expect('[1] added', t2)
        t2.write('chkick 1 guestarst\n')
        self.expect('You have been kicked out of channel 1 by', t)
        self.expect('Kicked out GuestARST', t2)
        t2.write('-ch 1\n')
        self.expect("[1] removed from your channel list", t2)
        self.close(t)
        self.close(t2)

    @with_player('TestPlayer')
    def test_kick_admin(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('TestPlayer')

        t2.write('+ch 5000\n')
        self.expect('You are now the owner of channel 5000.', t2)

        t.write('chkick 5000 testplayer\n')
        self.expect('You are not in channel 5000.', t)
        t.write('+ch 5000\n')
        self.expect('[5000] added', t)

        t2.write('chkick 5000 admin\n')
        self.expect('You cannot kick out an admin.', t2)
        t.write('chkick 5000 testplayer\n')
        self.expect('admin(*)(5000): *** Kicked out TestPlayer. ***', t)
        self.expect('*** You have been kicked out of channel 5000 by admin. ***', t2)
        t.write('-ch 5000\n')
        self.expect('[5000] removed from your channel list.', t)

        self.close(t)
        self.close(t2)

    @with_player('TestPlayer')
    def test_kick_offline(self):
        t2 = self.connect_as('testplayer')
        t2.write('+ch 1024\n')
        self.expect('You are now the owner of channel 1024.', t2)
        self.expect('[1024] added to your channel list.', t2)
        self.close(t2)

        t = self.connect_as_admin()
        t.write('+ch 1024\n')
        self.expect('[1024] added to your channel list.', t)
        t.write('chkick 1024 testplayer\n')
        self.expect('admin(*)(1024): *** Kicked out TestPlayer. ***', t)
        t.write('-ch 1024\n')
        self.expect('[1024] removed from your channel list.', t)
        self.close(t)

        t2 = self.connect_as('testplayer')
        t2.write('=ch\n')
        self.expect('-- channel list: 1 channel --\r\n1\r\n', t2)
        t2.write('inch 1024\n')
        self.expect('0 players', t2)
        self.close(t2)

    @with_player('testone')
    @with_player('testtwo')
    def test_kick_bad(self):
        t = self.connect_as('testone')
        t2 = self.connect_as('testtwo')
        t.write('+ch 2000\n')
        self.expect('You are now the owner of channel 2000.', t)
        self.expect('[2000] added to your channel list.', t)
        t2.write('+ch 2000\n')
        self.expect('[2000] added to your channel list.', t2)
        t2.write('chkick 2000 testone\n')
        self.expect("You don't have permission to do that.", t2)

        t.write('chkick 2000\n')
        self.expect('Usage:', t)

        t.write('chkick 2000 testtwo\n')
        self.expect('*** You have been kicked out of channel 2000 by testone. ***', t2)
        self.expect('testone(2000): *** Kicked out testtwo. ***', t)

        t.write('-ch 2000\n')
        self.expect('You are no longer an owner of channel 2000.', t)
        self.expect('[2000] removed from your channel list.', t)

        self.close(t)
        self.close(t2)

class TestInchannel(Test):
    def test_inchannel(self):
        t = self.connect_as_guest('GuestTest')
        t.write('inch\n')
        self.expect_re("4: .*GuestTest", t)

        t.write('inch -1\n')
        self.expect('Invalid channel', t)

        t.write('inch 9999999999\n')
        self.expect('Invalid channel', t)

        t.write('+ch 1\n')
        t.write('inch 1\n')
        self.expect_re('1 "help": .*GuestTest', t)
        self.expect('in channel 1.', t)

        t.write('inch 28741\n') # XXX somebody could join
        self.expect('There are 0 players in channel 28741.', t)

        self.close(t)

class TestCtellVar(Test):
    def test_ctell_var(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()

        t.write('set ctell 0\n')
        self.expect('You will not hear channel tells from unregistered', t)
        t.write('+ch 1\n')
        self.expect("[1] added to your channel list", t)
        t2.write('+ch 1\n')
        self.expect("[1] added to your channel list", t2)

        t2.write('tell 1 Channel 1 test\n')
        self.expect_not('Channel 1 test', t)

        t.write('set ctell 1\n')
        self.expect('You will now hear channel tells from unregistered', t)

        t2.write('tell 1 Another channel 1 test\n')
        self.expect('Another channel 1 test', t)

        t.write('-ch 1\n')
        self.expect("[1] removed from your channel list", t)

        self.close(t2)
        self.close(t)

class TestTopic(Test):
    @with_player('TestPlayer')
    def test_topic(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('TestPlayer')
        today = datetime.utcnow().date()

        t.write('chtopic\n')
        self.expect('Usage:', t)
        t.write('chtopic 10 test\n')
        self.expect('You are not in channel 10.', t)

        t.write('+ch 10\n')
        self.expect('[10] added to your channel list.', t)
        t2.write('+ch 10\n')
        self.expect('[10] added to your channel list.', t2)

        t.write('chtopic 10\n')
        self.expect('There is no topic for channel 10.', t)
        t.write('chtopic 10 This is an example topic.\n')
        self.expect('TOPIC(10): *** This is an example topic. (admin at %s' % today, t)
        self.expect(') ***', t)
        self.expect('TOPIC(10): *** This is an example topic. (admin at %s' % today, t2)
        self.expect(') ***', t2)

        t2.write('chtopic 10\n')
        self.expect('TOPIC(10): *** This is an example topic. (admin at %s' % today, t2)
        self.expect(') ***', t2)

        # joining channel displays topic
        t2.write('-ch 10\n')
        self.expect('[10] removed from your channel list.', t2)
        t2.write('+ch 10\n')
        self.expect('TOPIC(10): *** This is an example topic. (admin at %s' % today, t2)
        self.expect(') ***', t2)
        self.expect('[10] added to your channel list.', t2)

        # Leaving and rejoining does not display the topic...
        time.sleep(1)
        self.close(t2)
        t2 = self.connect()
        t2.write('testplayer\n%s\n' % tpasswd)
        self.expect('**** Starting FICS session as TestPlayer ****', t2)
        self.expect_not('TOPIC', t2)
        self.close(t2)

        # ...unless it has been modified.
        t.write('chtopic 10 A new topic.\n')
        self.expect('TOPIC(10): *** A new topic. (admin at %s' % today, t)
        time.sleep(1)
        t2 = self.connect()
        t2.write('testplayer\n%s\n' % tpasswd)
        self.expect('TOPIC(10): *** A new topic. (admin at %s' % today, t2)

        # clear topic
        t.write('chtopic 10 -\n')
        self.expect('admin(*)(10): *** Cleared topic. ***', t)
        self.expect('admin(*)(10): *** Cleared topic. ***', t2)

        t2.write('chtopic 10\n')
        self.expect('There is no topic for channel 10.', t2)

        t.write('-ch 10\n')
        self.expect('[10] removed from your channel list.', t)
        t2.write('-ch 10\n')
        self.expect('[10] removed from your channel list.', t2)

        t2.write('chtopic 10\n')
        self.expect('There is no topic for channel 10.', t2)

        self.close(t)
        self.close(t2)

    #def test_topic_userchannel(self):

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

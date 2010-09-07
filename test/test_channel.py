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

        t.write('+ch 0\n')
        self.expect("[0] added to your channel list", t)
        t.write('-ch 0\n')
        self.expect("[0] removed from your channel list", t)

        self.close(t)

class TestInchannel(Test):
    def test_inchannel(self):
        t = self.connect_as_guest()
        t.write('inch\n')
        self.expect("4: Guest", t)

        t.write('inch -1\n')
        self.expect('Invalid channel', t)

        t.write('inch 9999999999\n')
        self.expect('Invalid channel', t)

        t.write('+ch 1\n')
        t.write('inch 1\n')
        self.expect('1 "help": Guest', t)
        self.expect('There is 1 player', t)

        t.write('inch 999\n')
        self.expect('There are 0 players in channel 999.', t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

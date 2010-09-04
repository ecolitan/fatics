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

class TestMessage(Test):
    def test_message_guest(self):
        t = self.connect_as('GuestABCD', '')

        t.write("mess\n")
        self.expect("Only registered players can use the messages command", t)
        t.write("fmess admin 1\n")
        self.expect("Only registered players can use the fmessage command", t)
        t.write("clearmess *\n")
        self.expect("Only registered players can use the clearmessages command", t)
        t2 = self.connect_as_admin()
        t2.write('mess guestabcd foobar\n')
        self.expect('Only registered players can have messages.', t2)
        self.close(t2)

        self.close(t)


    @with_player('testplayer', 'testpass')
    def test_message(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t2.write('clearmess *\n')
        self.expect('Cleared 0 messages.', t2)

        t.write('mess testplayer This is an important message from admin.\n')
        self.expect('The following message was sent to testplayer:', t)
        self.expect('admin at', t)
        self.expect(': This is an important message from admin.', t)
        self.expect('The following message was received:', t2)
        self.expect('admin at', t2)
        self.expect(': This is an important message from admin.', t2)
        self.close(t2)

        t.write('mess testplayer mess 2!\n')
        t.write('mess testplayer mess 3!\n')
        t.write('mess testplayer mess 4!\n')
        self.expect('mess 4!', t)

        t2 = self.connect_as('testplayer', 'testpass')
        t2.write('message 3\n')
        self.expect(': mess 3!', t2)

        t2.write('mess\n')
        self.expect('1. admin at', t2)
        self.expect('2. admin at', t2)
        self.expect('3. admin at', t2)
        self.expect('4. admin at', t2)

        t2.write('mess 3\n')
        self.expect('3. admin at', t2)

        t2.write('mess 2-3\n')
        self.expect('2. admin at', t2)
        self.expect('3. admin at', t2)
        self.expect_not('4. admin at', t2)

        t2.write('mess admin\n')
        self.expect('You have no messages to admin.\r\n\r\n', t2)
        self.expect('Messages from admin:', t2)
        self.expect('1. admin at', t2)
        self.expect('2. admin at', t2)
        self.expect('3. admin at', t2)
        self.expect('4. admin at', t2)
        t2.write('clearmessages *\n')
        self.expect('Cleared 4 messages.', t2)

        t2.write('mess admin Too many messages\n')
        self.expect(': Too many messages', t)
        self.expect(': Too many messages', t2)
        t2.write('mess admin\n')
        self.expect('Messages to admin:', t2)
        self.expect('testplayer at ', t2)
        self.expect('You have no messages from admin.\r\n', t2)

        t.write('clearmess 1\n')
        self.expect('Cleared 1 message.', t)

        t.write('mess admin self message\n')
        self.expect(': self message', t)
        self.expect(': self message', t)
        t.write('mess\n')
        self.expect('1. admin at', t)
        t.write('clearmess *\n')
        self.expect('Cleared 1 message.', t)

        self.close(t)
        self.close(t2)

    @with_player('testplayer', 'testpass')
    def test_clearmessages(self):
        t = self.connect_as_admin()

        t.write('clearmessages *\n')
        self.expect('Cleared 0 messages.', t)

        t.write('mess testplayer message #1\n')
        t.write('mess testplayer message #2\n')
        t.write('mess testplayer message #3\n')
        t.write('mess testplayer message #4\n')
        self.expect('message #4', t)

        t2 = self.connect_as('testplayer', 'testpass')
        t2.write('clearmess 3\n')
        self.expect('Cleared 1 message.', t2)
        t2.write('mess\n')
        self.expect('message #1', t2)
        self.expect('message #2', t2)
        self.expect_not('message #3', t2)

        t2.write('clearmess 1-3\n')
        self.expect('Cleared 3 messages.', t2)

        t2.write('clearmess 1-9999\n')
        self.expect('Cleared 0 messages.', t2)

        t2.write('clearmess\n')
        self.expect('Use "clearmessages *"', t2)

        self.close(t)
        self.close(t2)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

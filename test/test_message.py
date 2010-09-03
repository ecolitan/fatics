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
        #t2 = self.connect_as_admin()
        #t2.write('mess guestabcd foobar\n')
        #self.close(t2)

        self.close(t)


    @with_player('testplayer', 'testpass')
    def test_message(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t.write('clearmessages *\n')
        self.expect('Cleared 0 messages.', t)

        t.write('mess testplayer This is an important message from admin.\n')
        self.expect('The following message was sent to testplayer:', t)
        self.expect('admin at', t)
        self.expect('This is an important message from admin.', t)
        self.expect('The following message was received:', t2)
        self.expect('admin at', t2)
        self.expect('This is an important message from admin.', t2)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

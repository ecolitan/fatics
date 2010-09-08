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

#from twisted.trial import unittest
from test import *

class TellTest(Test):
    def test_tell(self):
        t = self.connect_as_admin()
        t.write('tell admin Hello there!\n')
        self.expect('admin(*) tells you: Hello there!', t, "tell self")
        
        t.write('tell admin \t  space  test\t\n')
        self.expect('tells you: \t  space  test', t)

        t2 = self.connect_as_guest()
        t2.write('tell admin Guest tell\n')
        self.expect('(U) tells you: Guest tell', t, 'guest tell')
        self.close(t2)

        self.close(t)

    def test_bad_tell(self):
        t = self.connect_as_guest()
        t.write('tell nonexistentname foo\n')
        self.expect('No player named "nonexistentname"', t)

        t.write('tell admin foo bar\n')
        self.expect('No player named "admin" is online', t)

        t.write('tell admin1 too baz\n')
        self.expect('not a valid handle', t)

        self.close(t)

    def test_ambiguous_tell(self):
        self.adduser('aduser', 'test')
        t = self.connect_as('aduser', 'test')
        t2 = self.connect_as_guest()

        # not ambiguous when admin is offline
        t2.write('tell a blah blah\n')
        self.expect('tells you: blah blah', t)
        self.expect('(told aduser)', t2)

        t3 = self.connect_as_admin()
        t2.write('tell a blah blah\n')
        self.expect('Ambiguous name', t2)

        self.close(t)
        self.close(t3)

        t2.write('tell a blah blah\n')
        self.expect('No player named "a" is online', t2)

        self.close(t2)
        self.deluser('aduser')

    def test_tell_disconnected(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest()

        t2.write('t admin hello there\n')
        self.expect('hello there', t)
        self.close(t)

        t2.write('. where are you?\n')
        self.expect('admin is no longer online', t2)

        t = self.connect_as_admin()
        t2.write('. why hello again\n')
        self.expect('tells you: why hello again', t)

        self.close(t)
        self.close(t2)

class QtellTest(Test):
    def test_qtell(self):
        self.adduser('tdplayer', 'tdplayer', ['td'])
        try:
            t = self.connect_as('tdplayer', 'tdplayer')
            t.write('qtell nonexistentname test\n')
            self.expect('*qtell nonexistentname 1*', t)

            t.write('qtell admin test\n')
            self.expect('*qtell admin 1*', t)

            t2 = self.connect_as_admin()
            t.write('qtell admin simple test\n')
            self.expect(':simple test', t2)
            self.expect('*qtell admin 0*', t)

            t.write('qtell admin \\bthis\\nis a \\Hmore complicated\\h test\n')
            self.expect(':\x07this', t2)
            self.expect(':is a \x1b[7mmore complicated\x1b[0m test', t2)
            self.expect('*qtell admin 0*', t)

            t2.write('qtell tdplayer test\n')
            self.expect('Only TD programs are allowed to use this command', t2)


            t2.write('+ch 55\n')
            self.expect('added', t2)
            t.write('qtell -1 hello world\n')
            self.expect('*qtell -1 1*', t)
            t.write('qtell 55 !!! ###\n')
            self.expect('*qtell 55 0*', t)
            self.expect('!!! ###', t2)
            t2.write('-ch 55\n')
            self.expect('removed', t2)

            self.close(t2)
            self.close(t)
        finally:
            self.deluser('tdplayer')

class SayTest(Test):
    @with_player('testplayer', 'testpass')
    def test_say(self):
        t = self.connect_as('testplayer', 'testpass')
        t2 = self.connect_as_admin()

        t.write('say hello\n')
        self.expect("I don't know", t)

        t.write('match admin white 1 0 u\n')
        self.expect('Issuing:', t)
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        t.write('say Hello!\n')
        self.expect('testplayer[1] says: Hello!\r\n', t2)
        self.expect('(told admin', t)

        t2.write('say hi\n')
        self.expect('admin(*)[1] says: hi\r\n', t)
        self.expect('(told testplayer', t2)

        t.write('resign\n')
        self.expect('testplayer resigns', t)
        self.expect('testplayer resigns', t2)

        t.write('say gg\n')
        self.expect('testplayer says: gg', t2)
        t2.write('say thanks\n')
        self.expect('admin(*) says: thanks', t)

        self.close(t)

        t2.write('say bye\n')
        self.expect('testplayer is no longer online.', t2)

        t = self.connect_as('testplayer', 'testpass')
        t2.write('say yo\n')
        self.expect('admin(*) says: yo', t)
        self.expect('(told testplayer', t2)

        self.close(t)
        self.close(t2)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

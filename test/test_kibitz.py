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

class TestKibitz(Test):
    def test_kibitz_guest(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as('GuestEFGH', '')
        t3 = self.connect_as_guest()

        t.write('kibitz hello\n')
        self.expect('You are not playing, examining, or observing a game', t)

        t.write('match GuestEFGH white 5 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        t3.write('o 1\n')
        self.expect('now observing game 1', t3)

        t.write("kibitz This is a test kibitz!\n")
        self.expect('GuestABCD(U)(++++)[1] kibitzes: This is a test kibitz!', t)
        self.expect('GuestABCD(U)(++++)[1] kibitzes: This is a test kibitz!', t2)
        self.expect('GuestABCD(U)(++++)[1] kibitzes: This is a test kibitz!', t3)
        self.expect('(kibitzed to 2 players)', t)

        t.write('set kibitz 0\n')
        self.expect('You will not hear kibitzes', t)
        t2.write("kibitz Another test...\n")
        self.expect('GuestEFGH(U)(++++)[1] kibitzes: Another test...', t2)
        self.expect('GuestEFGH(U)(++++)[1] kibitzes: Another test...', t3)
        self.expect_not('Another test...', t)
        self.expect('(kibitzed to 1 player)', t2)

        t.write('set kibitz 1\n')
        self.expect('You will now hear kibitzes', t)
        t3.write("kibitz Third-party kib\n")
        self.expect('Only registered players may kib', t3)
        self.expect_not('Third-party kib', t)

        t.write('abort\n')
        t2.write('abort\n')

        self.close(t)
        self.close(t2)
        self.close(t3)

    @with_player('testplayer', 'testpass')
    @with_player('testobs', 'testpass')
    def test_kibitz_user(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')
        t3 = self.connect_as('testobs', 'testpass')

        t.write('kibitz hello\n')
        self.expect('You are not playing, examining, or observing a game', t)

        t.write('match testplayer white 5 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        t3.write('o 1\n')
        self.expect('now observing game 1', t3)

        t.write("*This is a test kibitz!\n")
        self.expect('admin(*)(----)[1] kibitzes: This is a test kibitz!', t)
        self.expect('admin(*)(----)[1] kibitzes: This is a test kibitz!', t2)
        self.expect('admin(*)(----)[1] kibitzes: This is a test kibitz!', t3)
        self.expect('(kibitzed to 2 players)', t)

        t.write('set kibitz 0\n')
        self.expect('You will not hear kibitzes', t)
        t2.write("kibitz Another test...\n")
        self.expect('testplayer(----)[1] kibitzes: Another test...', t2)
        self.expect('testplayer(----)[1] kibitzes: Another test...', t3)
        self.expect_not('Another test...', t)
        self.expect('(kibitzed to 1 player)', t2)

        t.write('set kibitz 1\n')
        self.expect('You will now hear kibitzes', t)
        t3.write("kibitz Third-party kib\n")
        self.expect('testobs(----)[1] kibitzes: Third-party kib', t)
        self.expect('testobs(----)[1] kibitzes: Third-party kib', t2)
        self.expect('testobs(----)[1] kibitzes: Third-party kib', t3)
        self.expect('(kibitzed to 2 players)', t3)

        self.close(t)
        self.close(t2)
        self.close(t3)

    @with_player('testplayer', 'testpass')
    def test_kiblevel(self):
        t = self.connect_as('GuestEFGH', '')
        t2 = self.connect_as('testplayer', 'testpass')
        t3 = self.connect_as_admin()

        t3.write('asetrating testplayer lightning chess 0 0 0 0 0 0\n')
        self.expect('Cleared lightning chess rating for testplayer.', t3)

        t.write('match testplayer white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        t3.write('o 1\n')
        self.expect('now observing game 1', t3)

        t3.write('set kiblevel 1000\n')
        self.expect('kiblevel set to 1000.', t3)
        t2.write('ki .\n')
        self.expect('(kibitzed to 1 player)', t2)

        t3.write('asetrating testplayer lightning chess 999 350 .01 0 0 0\n')
        self.expect('Set lightning chess rating for testplayer.', t3)
        t2.write('ki .\n')
        self.expect('(kibitzed to 1 player)', t2)

        t3.write('asetrating testplayer lightning chess 1001 350 .01 0 0 0\n')
        self.expect('Set lightning chess rating for testplayer.', t3)
        t2.write('ki .\n')
        self.expect('testplayer(1001)[1] kibitzes: .', t)
        self.expect('testplayer(1001)[1] kibitzes: .', t2)
        self.expect('testplayer(1001)[1] kibitzes: .', t3)
        self.expect('(kibitzed to 2 players)', t2)
        t3.write('set kiblevel 0\n')

        t.write('abort\n')
        t2.write('abort\n')

        t3.write('asetrating testplayer lightning chess 0 0 0 0 0 0\n')
        self.expect('Cleared lightning chess rating for testplayer.', t3)

        self.close(t)
        self.close(t2)
        self.close(t3)

class TestWhisper(Test):
    def test_whisper_guest(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as('GuestEFGH', '')
        t3 = self.connect_as_guest()

        t.write('whi hello\n')
        self.expect('You are not playing, examining, or observing a game', t)

        t.write('match GuestEFGH white 5 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        t3.write('o 1\n')
        self.expect('now observing game 1', t3)

        t.write("whis This is a test whisper!\n")
        self.expect('GuestABCD(U)(++++)[1] whispers: This is a test whisper!', t3)
        self.expect('(whispered to 1 player)', t)
        self.expect_not('whispers', t)
        self.expect_not('whispers', t2)

        # the kibitz var has no effect on whispers
        t3.write('set kibitz 0\n')
        self.expect('You will not hear kibitzes', t3)
        t2.write("whisper Another test...\n")
        self.expect('GuestEFGH(U)(++++)[1] whispers: Another test...', t3)
        self.expect('(whispered to 1 player)', t2)
        t3.write('set kibitz 1\n')
        self.expect('You will now hear kibitzes', t3)

        t3.write("#Third-party whis\n")
        self.expect('Only registered players may whis', t3)
        self.expect_not('Third-party whis', t3)

        t.write('abort\n')
        t2.write('abort\n')

        self.close(t)
        self.close(t2)
        self.close(t3)

    @with_player('testplayer', 'testpass')
    @with_player('testobs', 'testpass')
    def test_whisper_user(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')
        t3 = self.connect_as('testobs', 'testpass')

        t.write('whisper hello\n')
        self.expect('You are not playing, examining, or observing a game', t)

        t.write('match testplayer white 5 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        t3.write('o 1\n')
        self.expect('now observing game 1', t3)

        t.write("#This is a test whisper!\n")
        self.expect('admin(*)(----)[1] whispers: This is a test whisper!', t3)
        self.expect('(whispered to 1 player)', t)

        t3.write("whis Third-party whisper\n")
        self.expect('testobs(----)[1] whispers: Third-party whisper', t3)
        self.expect_not('whispers', t)
        self.expect('(whispered to 0 players)', t3)

        self.close(t)
        self.close(t2)
        self.close(t3)

    @with_player('testplayer', 'testpass')
    def test_kiblevel_whisper(self):
        t = self.connect_as('GuestEFGH', '')
        t2 = self.connect_as('testplayer', 'testpass')
        t3 = self.connect_as_admin()

        t3.write('asetrating testplayer lightning chess 0 0 0 0 0 0\n')
        self.expect('Cleared lightning chess rating for testplayer.', t3)

        t.write('match testplayer white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        t3.write('o 1\n')
        self.expect('now observing game 1', t3)

        t3.write('set kiblevel 1000\n')
        self.expect('kiblevel set to 1000.', t3)
        t2.write('whi .\n')
        self.expect('(whispered to 0 players)', t2)

        t3.write('asetrating testplayer lightning chess 999 350 .01 0 0 0\n')
        self.expect('Set lightning chess rating for testplayer.', t3)
        t2.write('whi .\n')
        self.expect('(whispered to 0 players)', t2)

        t3.write('asetrating testplayer lightning chess 1001 350 .01 0 0 0\n')
        self.expect('Set lightning chess rating for testplayer.', t3)
        t2.write('whi .\n')
        self.expect('testplayer(1001)[1] whispers: .', t3)
        self.expect('(whispered to 1 player)', t2)
        t3.write('set kiblevel 0\n')

        t.write('abort\n')
        t2.write('abort\n')

        t3.write('asetrating testplayer lightning chess 0 0 0 0 0 0\n')
        self.expect('Cleared lightning chess rating for testplayer.', t3)

        self.close(t)
        self.close(t2)
        self.close(t3)

class TestXkibitz(Test):
    @with_player('testplayer', 'testpass')
    def test_xkibitz(self):
        t = self.connect_as('GuestEFGH', '')
        t2 = self.connect_as('testplayer', 'testpass')
        t3 = self.connect_as_admin()

        t3.write('xki 1 foo\n')
        self.expect('no such game', t3)

        t.write('match testplayer white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')

        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        t3.write('o 1\n')
        self.expect('now observing game 1', t3)

        t3.write('xki 1 sha la la\n')
        self.expect('admin(*)(----)[1] kibitzes: sha la la\r\n', t)
        self.expect('admin(*)(----)[1] kibitzes: sha la la\r\n', t2)
        self.expect('admin(*)(----)[1] kibitzes: sha la la\r\n', t3)

        self.close(t)
        self.close(t2)
        self.close(t3)

class TestXwhisper(Test):
    @with_player('testplayer', 'testpass')
    def test_xwhisper(self):
        t = self.connect_as('GuestEFGH', '')
        t2 = self.connect_as('testplayer', 'testpass')
        t3 = self.connect_as_admin()

        t3.write('xwhi 1 foo\n')
        self.expect('no such game', t3)

        t.write('match testplayer white 1 0\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')

        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)
        t3.write('o 1\n')
        self.expect('now observing game 1', t3)

        t.write('xwhi 1 sha la la\n')
        self.expect('GuestEFGH(U)(++++)[1] whispers: sha la la\r\n', t3)

        self.close(t)
        self.close(t2)
        self.close(t3)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

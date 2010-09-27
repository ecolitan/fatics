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

# GuestFXLR (++++) seeking 5 0 unrated blitz m ("play 37" to respond)

class TestSeek(Test):
    def test_seek_guest(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_guest()

        t.write('seek 3 0\n')
        m = self.expect_re('Your seek has been posted with index (\d+).', t)
        n = int(m.group(1))
        self.expect('GuestABCD(U) (++++) seeking 3 0 unrated blitz ("play %d" to respond)' % n, t2)
        self.expect('(1 player saw the seek.)', t)

        t.write('seek 3 0\n')
        self.expect('You already have an active seek with the same parameters.', t)

        t.write('seek 15+5\n')
        self.expect('Your seek has been posted with index %d.' %
            (n  + 1), t)
        self.expect('GuestABCD(U) (++++) seeking 15 5 unrated standard ("play %d" to respond)' % (n + 1), t2)
        self.expect('(1 player saw the seek.)', t)

        t.write('unseek\n')
        self.expect('Your seeks have been removed.', t)

        self.close(t)
        self.close(t2)

    def test_matching_seek(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as('GuestEFGH', '')

        t.write('seek 15+5 bronstein zh\n')
        self.expect('Your seek has been posted with index ', t)
        self.expect('(1 player saw the seek.)', t)
        self.expect('GuestABCD(U) (++++) seeking 15 5 unrated standard crazyhouse bronstein ("play ', t2)

        t2.write('seek 15 5 bronstein crazyhouse\n')
        self.expect('Your seek matches one posted by GuestABCD.', t2)
        self.expect('Your seek matches one posted by GuestEFGH.', t)

        self.expect('Creating:', t)
        self.expect('unrated standard crazyhouse 15 5', t)
        self.expect('Creating:', t2)
        self.expect('unrated standard crazyhouse 15 5', t2)

        self.close(t)
        self.close(t2)

    def test_bad_seek(self):
        t = self.connect_as_guest()
        t.write('seek 3+0 r\n')
        self.expect('Only registered players can play rated games.', t)
        t.write('play 9999\n')
        self.expect('That seek is not available.', t)
        t.write('play nosuchuser\n')
        self.expect('No player named "nosuchuser" is online', t)

        t.write('ex\n')
        self.expect('Starting a game', t)
        t.write('seek 3+0\n')
        self.expect('You are examining a game.', t)
        t.write('play 1\n')
        self.expect('You are examining a game.', t)
        t.write('unex\n')

        self.close(t)

    @with_player('TestPlayer', 'testpass')
    def test_censor(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t2.write('+cen admin\n')
        self.expect('admin added to your censor list.', t2)

        t2.write('seek 3 0\n')
        m = self.expect_re('Your seek has been posted with index (\d+).', t2)
        n = int(m.group(1))
        self.expect('(0 players saw the seek.)', t2)

        t.write('play %d\n' % n)
        self.expect('TestPlayer is censoring you.', t)

        t2.write('-cen admin\n')
        self.expect('admin removed from your censor list.', t2)

        self.close(t2)
        self.close(t)

    @with_player('TestPlayer', 'testpass')
    def test_noplay(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t2.write('+noplay admin\n')
        self.expect('admin added to your noplay list.', t2)

        t2.write('seek 3 0\n')
        m = self.expect_re('Your seek has been posted with index (\d+).', t2)
        n = int(m.group(1))
        self.expect('(0 players saw the seek.)', t2)

        t.write('play %d\n' % n)
        self.expect("You are on TestPlayer's noplay list.", t)

        t2.write('-noplay admin\n')
        self.expect('admin removed from your noplay list.', t2)

        self.close(t2)
        self.close(t)

    def test_game_removes_seek(self):
        t = self.connect_as_guest()
        t.write('seek 3 0\n')
        m = self.expect_re('Your seek has been posted with index (\d+).', t)
        t.write('ex\n')
        self.expect('Starting a game', t)
        t.write('unseek\n')
        self.expect('You have no active seeks.', t)
        self.close(t)

    def test_showownseek(self):
        """ Test the showownseek var and ivar. """
        t = self.connect_as('GuestABCD', '')
        t.write('see 3+0\n')
        self.expect('(0 players saw the seek.)', t)

        t.write('set showownseek 1\n')
        self.expect('You will now see your own seeks.', t)
        t.write('see 4+0\n')
        self.expect('(1 player saw the seek.)', t)

        t.write('iset showownseek 0\n')
        self.expect('showownseek unset.', t)
        t.write('see 5+0\n')
        self.expect('(0 players saw the seek.)', t)

        t.write('unseek\n')
        self.expect('Your seeks have been removed.', t)

        self.close(t)

    def test_seek_limit(self):
        t = self.connect_as('GuestABCD', '')

        t.write('see 1+0\n')
        self.expect('(0 players saw the seek.)', t)
        t.write('see 5+0\n')
        self.expect('(0 players saw the seek.)', t)
        t.write('see 15+0\n')
        self.expect('(0 players saw the seek.)', t)
        t.write('see 60+0\n')
        self.expect('You can only have 3 active seeks.', t)

        t.write('unseek\n')
        self.expect('Your seeks have been removed.', t)

        self.close(t)

    @with_player('TestPlayer', 'testpass')
    def test_play(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t2.write('seek 3 0 white\n')
        m = self.expect_re('Your seek has been posted with index (\d+).', t2)
        n = int(m.group(1))
        self.expect('(1 player saw the seek.)', t2)

        t.write('play %d\n' % n)
        self.expect('admin accepts your seek.', t2)

        self.expect('Creating: TestPlayer (----) admin (----) rated blitz 3 0', t)
        self.expect('Creating: TestPlayer (----) admin (----) rated blitz 3 0', t2)

        t.write('abo\n')
        self.expect('aborted on move 1', t)

        self.close(t2)
        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

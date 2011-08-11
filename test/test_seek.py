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

import time

# GuestWXYZ (++++) seeking 5 0 unrated blitz [white] mf ("play 37" to respond)

class TestSeek(Test):
    def test_seek_guest(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest()

        self.set_nowrap(t)

        t.write('seek 3 0\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n = int(m.group(1))
        self.expect('GuestABCD (++++) seeking 3 0 unrated blitz ("play %d" to respond)' % n, t2)
        self.expect('(1 player saw the seek.)', t)

        t.write('seek 3 0\n')
        self.expect('You already have an active seek with the same parameters.', t)

        t.write('seek 15+5\n')
        m2 = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n2 = int(m2.group(1))
        self.expect('GuestABCD (++++) seeking 15 5 unrated standard ("play %d" to respond)' % n2, t2)
        self.expect('(1 player saw the seek.)', t)

        t.write('unseek\n')
        self.expect('Your seeks have been removed.', t)

        self.close(t)
        self.close(t2)

    @with_player('testone')
    @with_player('testtwo')
    def test_seek_defaults(self):
        t = self.connect_as('testone')
        t2 = self.connect_as('testtwo')

        t.write('set time 7\n')
        t.write('set inc 4\n')
        self.expect('inc set to 4.', t)
        t.write('see\n')
        self.expect('testone (----) seeking 7 4 rated blitz', t2)
        t.write('uns\n')
        self.expect('Your seeks have been removed.', t)

        t.write('see 5\n')
        self.expect('testone (----) seeking 5 0 rated blitz', t2)

        self.close(t)
        self.close(t2)

    def test_matching_seek(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')

        self.set_nowrap(t2)

        t.write('seek 15+5 bronstein zh white\n')
        self.expect('Your seek has been posted with index ', t)
        self.expect('(1 player saw the seek.)', t)
        self.expect('GuestABCD (++++) seeking 15 5 unrated standard crazyhouse bronstein [white] ("play ', t2)

        t2.write('seek 15 5 bronstein crazyhouse black\n')
        self.expect('Your seek matches one posted by GuestABCD.', t2)
        self.expect('Your seek matches one posted by GuestEFGH.', t)

        self.expect('Creating:', t)
        self.expect('unrated standard crazyhouse 15 5', t)
        self.expect('Creating:', t2)
        self.expect('unrated standard crazyhouse 15 5', t2)

        self.close(t)
        self.close(t2)

    def test_matching_seek_formula(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')

        self.set_nowrap(t2)
        t.write('seek 15+5 bronstein zh white\n')
        self.expect('Your seek has been posted with index ', t)
        self.expect('(1 player saw the seek.)', t)
        self.expect('GuestABCD (++++) seeking 15 5 unrated standard crazyhouse bronstein [white] ("play ', t2)

        t2.write('set formula rating > 0\n')
        t2.write('seek 15 5 bronstein crazyhouse black f\n')
        self.expect('(0 players saw the seek.)', t2)

        self.expect_not('Creating:', t)

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

        t.write('unseek\n')
        self.expect('You have no active seeks.', t)
        t.write('unseek 1\n')
        self.expect('You have no seek 1.', t)
        t.write('unseek foo\n')
        self.expect('Usage:', t)

        self.close(t)

    @with_player('TestPlayer')
    def test_censor(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer')

        t2.write('+cen admin\n')
        self.expect('admin added to your censor list.', t2)

        t2.write('seek 3 0\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t2)
        n1 = int(m.group(1))
        self.expect('(0 players saw the seek.)', t2)

        t.write('play %d\n' % n1)
        self.expect('TestPlayer is censoring you.', t)

        t.write('sou\n')
        self.expect('0 ads displayed.', t)

        t.write('seek 3 0\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n2 = int(m.group(1))
        self.expect('(0 players saw the seek.)', t)

        t2.write('play %d\n' % n2)
        self.expect('You are censoring admin.', t2)

        t2.write('-cen admin\n')
        self.expect('admin removed from your censor list.', t2)

        self.close(t2)
        self.close(t)

    @with_player('TestPlayer')
    def test_noplay(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer')

        t2.write('+noplay admin\n')
        self.expect('admin added to your noplay list.', t2)

        t2.write('seek 3 0\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t2)
        n1 = int(m.group(1))
        self.expect('(0 players saw the seek.)', t2)

        t.write('play %d\n' % n1)
        self.expect("You are on TestPlayer's noplay list.", t)

        t.write('seek 3 0\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n2 = int(m.group(1))
        self.expect('(0 players saw the seek.)', t)

        t2.write('play %d\n' % n2)
        self.expect('You have admin on your noplay list.', t2)

        t2.write('-noplay admin\n')
        self.expect('admin removed from your noplay list.', t2)

        self.close(t2)
        self.close(t)

    def test_game_removes_seek(self):
        t = self.connect_as_guest()
        t.write('seek 3 0\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n = int(m.group(1))
        t.write('ex\n')
        self.expect('Starting a game', t)
        t.write('unseek\n')
        self.expect('You have no active seeks.', t)

        t2 = self.connect_as_guest()
        t2.write('play %d\n' % n)
        self.expect('That seek is not available.', t2)
        self.close(t2)

        self.close(t)

    def test_logout_removes_seek(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_guest()
        t.write('seek 3 0\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n = int(m.group(1))
        self.close(t)

        t2.write('play %d\n' % n)
        self.expect('That seek is not available.', t2)

        t2.write('seek 3 0\n')
        self.expect_re(r'Your seek has been posted with index (\d+).', t2)

        self.close(t2)

    def test_showownseek(self):
        """ Test the showownseek var and ivar. """
        t = self.connect_as_guest('GuestABCD')
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
        t = self.connect_as_guest('GuestABCD')

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

    def test_manual(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest('GuestEFGH')

        t.write('see 90+5 white fischer m\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n1 = int(m.group(1))

        self.expect('GuestABCD (++++) seeking 90 5 unrated slow [white] m ("play %d" to respond)' % n1, t2)
        t2.write('play %d\n' % n1)
        self.expect('Issuing match request since the seek was set to manual.', t2)

        self.expect('Challenge: GuestEFGH (++++) [black] GuestABCD (++++) unrated slow 90 5', t)

        t2.write('play %d\n' % n1)
        self.expect('Issuing match request since the seek was set to manual.', t2)
        self.expect('You are already offering an identical match to GuestABCD.', t2)

        t.write('a\n')
        self.expect('Creating:', t)
        self.expect('Creating:', t2)
        t.write('abo\n')

        self.close(t)
        self.close(t2)

    def test_seek_delay(self):
        t = self.connect_as_guest()
        t.write('seek\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n = int(m.group(1))
        t.write('unseek %d\n' % n)
        self.expect('Your seek %d has been removed.' % n, t)
        time.sleep(0.25)

        t.write('seek\n')
        self.expect('Your seek has been posted with index %d.' % (n + 1), t)
        self.close(t)

    def test_seek_expire(self):
        self._skip('slow test')
        t = self.connect_as_guest()
        t.write('seek\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n1 = int(m.group(1))
        t.write('unseek %d\n' % n1)
        self.expect('Your seek %d has been removed.' % n1, t)
        time.sleep(91)

        t.write('seek\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n2 = int(m.group(1))
        self.assert_(n2 <= n1)
        self.close(t)

    @with_player('testplayer')
    @with_player('testtwo')
    def test_seeker_formula(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer')
        t3 = self.connect_as('testtwo')

        t.write('asetrating testplayer blitz chess 1500 200 .005 100 75 35\n')
        self.expect('Set blitz chess rating for testplayer.', t)
        t.write('asetrating testtwo blitz chess 2001 200 .005 100 75 35\n')
        self.expect('Set blitz chess rating for testtwo.', t)

        t.write('set formula 1000 <= rating and rating <= 2000\n')
        self.expect('formula set to ', t)
        t.write('seek 3+0 f\n')
        self.expect('(1 player saw the seek.)', t)
        m = self.expect_re(r'admin \(----\) seeking 3 0 rated blitz f \("play (\d+)"', t2)
        n = int(m.group(1))

        t3.write('play %d\n' % n)
        # Match request does not fit formula for GuestSFPP:
        # GuestSFPP's formula: rating > 0
        self.expect('Match request does not fit formula for admin:', t3)

        t2.write('play %d\n' % n)
        self.expect('Creating:', t)
        self.expect('Creating:', t2)
        t.write('abo\n')
        self.expect('aborted on move 1', t2)

        t.write('set formula\n')
        self.expect('formula unset.', t)

        self.close(t)
        self.close(t2)
        self.close(t3)

    def test_filter_formula(self):
        t = self.connect_as_guest('GuestABCD')
        t2 = self.connect_as_guest()

        t2.write('set formula !blitz\n')
        self.expect('formula set to "!blitz".', t2)

        t.write('seek 1+0\n')
        self.expect('(1 player saw the seek.)', t)
        self.expect('GuestABCD (++++) seeking', t2)
        t.write('seek 3+0\n')
        self.expect('(0 players saw the seek.)', t)
        self.expect_not('seeking', t2)

        t.write('uns\n')
        t2.write('uns\n')

        self.close(t)
        self.close(t2)

class TestPlay(Test):
    @with_player('TestPlayer')
    def test_play(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer')
        t3 = self.connect_as_guest()

        t2.write('set style 12\n')

        t2.write('seek 3 0 white\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t2)
        n = int(m.group(1))
        self.expect('(1 player saw the seek.)', t2)

        t3.write('play %d\n' % n)
        self.expect('Only registered players can play rated games.', t3)
        self.close(t3)

        t.write('play %d\n' % n)
        self.expect('admin accepts your seek.', t2)

        self.expect('Creating: TestPlayer (----) admin (----) rated blitz 3 0', t)
        self.expect('Creating: TestPlayer (----) admin (----) rated blitz 3 0', t2)

        t2.write('d4\n')
        self.expect('\r\n<12> rnbqkbnr pppppppp -------- -------- ---P---- -------- PPP-PPPP RNBQKBNR B -1 1 1 1 1 0 1 TestPlayer admin -1 3 0 39 39 180 180 1 P/d2-d4 (0:00) d4 0 0 0\r\n', t2)

        t.write('abo\n')
        self.expect('aborted on move 1', t)

        self.close(t2)
        self.close(t)

    @with_player('TestPlayer')
    def test_play_name(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer')
        t2.write('set style 12\n')

        t2.write('play admin\n')
        self.expect("admin isn't seeking any games.", t2)

        t.write('seek 1+0 zh black\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n1 = int(m.group(1))

        t.write('seek 2+12\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n2 = int(m.group(1))

        t2.write('play admin\n')
        self.expect('admin is seeking several games.', t2)

        t.write('unseek %d\n' % n2)
        self.expect('Your seek %d has been removed.' % n2, t)

        t2.write('play admin\n')
        self.expect('Creating: TestPlayer (----) admin (----) rated lightning crazyhouse 1 0', t)
        self.expect('Creating: TestPlayer (----) admin (----) rated lightning crazyhouse 1 0', t2)

        t.write('abo\n')
        self.expect('aborted on move 1', t)

        self.close(t2)
        self.close(t)

#  7 1500 SomePlayerA         5   2 rated   blitz      [white]  1300-9999 m
class TestSought(Test):
    def test_sought_all(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest('GuestABCD')

        t.write('seek 1+0\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t)
        n1 = int(m.group(1))

        t2.write('seek 2+12 fr bronstein black\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t2)
        n2 = int(m.group(1))

        # a removed seek that should not be shown
        t2.write('seek 5+12\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t2)
        n3 = int(m.group(1))
        t2.write('uns %d\n' % n3)
        self.expect('Your seek %d has been removed.' % n3, t2)

        t.write('sought all\n')
        self.expect('%3d ---- admin(*)            1   0 rated   lightning' % n1,
            t)
        self.expect('%3d ++++ GuestABCD(U)        2  12 unrated blitz chess960 bronstein [black]' % n2, t)
        self.expect('2 ads displayed.', t)

        self.close(t)
        self.close(t2)

    def test_sought(self):
        t = self.connect_as_admin()
        t2 = self.connect_as_guest('GuestABCD')
        t3 = self.connect_as_guest()

        t.write('set formula time < 15\n')
        self.expect('formula set to "time < 15".', t)

        t2.write('see 3+0\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t2)
        n1 = int(m.group(1))
        t2.write('see 15+0\n')

        # seek filtered out by seeker's formula
        t3.write('set formula rating > 9999\n')
        t3.write('seek 2+12 f\n')

        t.write('sou\n')
        self.expect('%3d ++++ GuestABCD(U)        3   0 unrated blitz' % n1, t)
        self.expect('1 ad displayed.', t)

        t.write('set formula\n')
        self.expect('formula unset.', t)

        self.close(t)
        self.close(t2)

# <s> 47 w=GuestWWPQ ti=01 rt=0P t=2 i=12 r=u tp=blitz c=W rr=0-9999 a=f f=f
class TestSeekinfo(Test):
    def test_seekinfo(self):
        t = self.connect_as_guest()
        t2 = self.connect_as_guest('GuestABCD')
        t3 = self.connect_as_admin()

        t.write('iset seekinfo 1\n')
        t.write('iset seekremove 1\n')
        self.expect('seekremove set.', t)

        t3.write('+gm admin\n')
        self.expect('admin added to the GM list.', t3)

        t2.write('seek 3+1 fr\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t2)
        n1 = int(m.group(1))
        self.expect('<s> %d w=GuestABCD ti=01 rt=0  t=3 i=1 r=u tp=chess960 c=? rr=0-9999 a=t f=f' % n1, t)

        t3.write('seek 15+5 white r m f\n')
        m = self.expect_re(r'Your seek has been posted with index (\d+).', t3)
        n2 = int(m.group(1))
        self.expect('<s> %d w=admin ti=04 rt=0  t=15 i=5 r=r tp=chess c=W rr=0-9999 a=f f=t' % n2, t)

        # seekremove
        t2.write('unseek %d\n' % n1)
        self.expect('<sr> %d' % n1, t)
        t3.write('unseek\n')
        self.expect('<sr> %d' % n2, t)

        t3.write('-gm admin\n')
        self.expect('admin removed from the GM list.', t3)

        self.close(t)
        self.close(t2)
        self.close(t3)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

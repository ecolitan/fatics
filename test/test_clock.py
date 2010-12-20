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

import random

import time

from test import *

class TestTime(Test):
    def _time_to_secs(self, s):
        m = re.match(r'(?:(\d+):)?(\d+):(\d+)\.(\d{3})', s)
        self.assert_(m)
        (h, m, s) = (int(m.group(1)) if m.group(1) else 0, int(m.group(2)),
            int(m.group(3)) + float(m.group(4)) / 1000.0)
        return 60 * 60 * h + 60 * m + s

    @with_player('TestPlayer', 'testpass')
    def test_time(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('time\n')
        self.expect('You are not playing', t)

        t.write('match testp white 0+1\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')
        self.expect('Creating: ', t)
        self.expect('Creating: ', t2)

        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 1 none (0:00) none 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 1 none (0:00) none 1 0 0', t2)

        t.write('time\n')
        self.expect('White Clock : 0:10.000', t)
        self.expect('Black Clock : 0:10.000', t)

        t3 = self.connect_as_guest()
        t3.write('time admin\n')
        self.expect('White Clock : 0:10.000', t3)
        self.expect('Black Clock : 0:10.000', t3)
        self.close(t3)

        t.write('e4\n')
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 1 P/e2-e4 (0:00) e4 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 1 P/e2-e4 (0:00) e4 1 0 0', t2)

        t2.write('e5\n')
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----P--- -------- PPPP-PPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 2 P/e7-e5 (0:00) e5 0 1 0', t)
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----P--- -------- PPPP-PPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 2 P/e7-e5 (0:00) e5 1 1 0', t2)
        time.sleep(3)
        t.write('f4\n')
        time.sleep(1)

        t2.write('time\n')
        m = self.expect_re('White Clock : (.*?)\r\n', t2)
        white_secs = self._time_to_secs(m.group(1))
        # white uses 3 seconds, gets 1 second increment
        self.assert_(7.9 <= white_secs <= 8.1)
        # black uses 1 second
        m = self.expect_re('Black Clock : (.*?)\r\n', t2)
        black_secs = self._time_to_secs(m.group(1))
        self.assert_(8.9 <= black_secs <= 9.1)

        t.write('abo\n')
        t2.write('abo\n')
        self.expect('aborted by agreement', t)

        self.close(t)
        self.close(t2)

    def test_time_examined(self):
        t = self.connect_as_guest('GuestABCD')
        t.write('ex\n')
        self.expect('Starting a game', t)
        t.write('time\n')
        self.expect('Game 1: GuestABCD (0) GuestABCD (0) unrated untimed 0 0',
            t)
        self.expect('White Clock : 0:00.000', t)
        self.expect('Black Clock : 0:00.000', t)
        t.write('unex\n')
        self.close(t)

class TestFlag(Test):
    @with_player('TestPlayer', 'testpass')
    def test_flag(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t.write('set autoflag 0\n')
        self.expect('Auto-flagging disabled.', t)

        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match testplayer white 0+1 u\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')

        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 1 none (0:00) none 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 1 none (0:00) none 1 0 0', t2)

        t.write('e4\n')
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 1 P/e2-e4 (0:00) e4 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 1 P/e2-e4 (0:00) e4 1 0 0', t2)

        t2.write('e5\n')
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----P--- -------- PPPP-PPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 2 P/e7-e5 (0:00) e5 0 1 0', t)
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----P--- -------- PPPP-PPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 2 P/e7-e5 (0:00) e5 1 1 0', t2)
        t.write('f4\n')
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----PP-- -------- PPPP--PP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 11 10 2 P/f2-f4 (0:00) f4 0 1 0', t)
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----PP-- -------- PPPP--PP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 11 10 2 P/f2-f4 (0:00) f4 1 1 0', t2)

        time.sleep(15)
        self.expect_not('forfeits', t)

        t.write('time\n')
        self.expect('Black Clock : 0:00.000', t)

        t.write('flag\n')
        self.expect('TestPlayer forfeits on time} 1-0', t)
        self.expect('TestPlayer forfeits on time} 1-0', t2)

        t.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t)

        self.close(t)
        self.close(t2)

    @with_player('TestPlayer', 'testpass')
    def test_flag_both(self):
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t.write('set autoflag 0\n')
        self.expect('Auto-flagging disabled.', t)

        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('match testplayer white 0+1 u\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')

        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 1 none (0:00) none 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 1 none (0:00) none 1 0 0', t2)

        t.write('e4\n')
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 1 P/e2-e4 (0:00) e4 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 1 P/e2-e4 (0:00) e4 1 0 0', t2)

        t2.write('e5\n')
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----P--- -------- PPPP-PPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 2 P/e7-e5 (0:00) e5 0 1 0', t)
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----P--- -------- PPPP-PPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 2 P/e7-e5 (0:00) e5 1 1 0', t2)
        t.write('f4\n')
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----PP-- -------- PPPP--PP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 11 10 2 P/f2-f4 (0:00) f4 0 1 0', t)
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----PP-- -------- PPPP--PP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 11 10 2 P/f2-f4 (0:00) f4 1 1 0', t2)

        time.sleep(15)
        self.expect_not('forfeits', t)

        t.write('time\n')
        self.expect('Black Clock : 0:00.000', t)

        t2.write('exf4\n')
        self.expect('<12> ', t)
        self.expect('<12> ', t2)
        time.sleep(15)
        #self.expect_not('forfeits', t)

        random.choice([t, t2]).write('flag\n')
        self.expect('(admin vs. TestPlayer) Both players ran out of time} 1/2-1/2', t)
        self.expect('(admin vs. TestPlayer) Both players ran out of time} 1/2-1/2', t2)

        t.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t)

        self.close(t)
        self.close(t2)

    @with_player('TestPlayer', 'testpass')
    def test_autoflag_nomove(self):
        """ Test when a player forfeits on time without making a move. The
        server make take a few seconds to award the forfeit, since it
        checks at the heartbeat timer. """
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('set autoflag 1\n')
        self.expect('Auto-flagging enabled.', t)

        t.write('match testplayer white 0+1 u\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')

        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 1 none (0:00) none 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 1 none (0:00) none 1 0 0', t2)

        t.write('e4\n')
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 1 P/e2-e4 (0:00) e4 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 1 P/e2-e4 (0:00) e4 1 0 0', t2)

        t2.write('e5\n')
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----P--- -------- PPPP-PPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 2 P/e7-e5 (0:00) e5 0 1 0', t)
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----P--- -------- PPPP-PPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 2 P/e7-e5 (0:00) e5 1 1 0', t2)
        t.write('f4\n')
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----PP-- -------- PPPP--PP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 11 10 2 P/f2-f4 (0:00) f4 0 1 0', t)
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----PP-- -------- PPPP--PP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 11 10 2 P/f2-f4 (0:00) f4 1 1 0', t2)

        time.sleep(10)
        self.expect('TestPlayer forfeits on time} 1-0', t, timeout=10)
        self.expect('TestPlayer forfeits on time} 1-0', t2, timeout=10)

        t.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t)

        self.close(t)
        self.close(t2)

    @with_player('TestPlayer', 'testpass')
    def test_autoflag_move(self):
        """ Test when a player forfeits on time after moving barely
        too late; the forfeit should happen immediately. """
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('set autoflag 1\n')
        self.expect('Auto-flagging enabled.', t)

        t.write('match testplayer white 0+1 u\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')

        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 1 none (0:00) none 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- -------- -------- PPPPPPPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 1 none (0:00) none 1 0 0', t2)

        t.write('e4\n')
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 1 P/e2-e4 (0:00) e4 0 0 0', t)
        self.expect('<12> rnbqkbnr pppppppp -------- -------- ----P--- -------- PPPP-PPP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 1 P/e2-e4 (0:00) e4 1 0 0', t2)

        t2.write('e5\n')
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----P--- -------- PPPP-PPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 10 10 2 P/e7-e5 (0:00) e5 0 1 0', t)
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----P--- -------- PPPP-PPP RNBQKBNR W -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 10 10 2 P/e7-e5 (0:00) e5 1 1 0', t2)
        t.write('f4\n')
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----PP-- -------- PPPP--PP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer -1 0 1 39 39 11 10 2 P/f2-f4 (0:00) f4 0 1 0', t)
        self.expect('<12> rnbqkbnr pppp-ppp -------- ----p--- ----PP-- -------- PPPP--PP RNBQKBNR B -1 1 1 1 1 0 1 admin TestPlayer 1 0 1 39 39 11 10 2 P/f2-f4 (0:00) f4 1 1 0', t2)

        time.sleep(11)
        t2.write('exf4\n')
        self.expect('TestPlayer forfeits on time} 1-0', t)
        self.expect('TestPlayer forfeits on time} 1-0', t2)

        t.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t)

        self.close(t)
        self.close(t2)

    @with_player('TestPlayer', 'testpass')
    def test_autoflag_nomaterial(self):
        """ Test when a player runs out of time but the opponent
        has no mating material. """
        t = self.connect_as_admin()
        t2 = self.connect_as('testplayer', 'testpass')

        t.write('set style 12\n')
        t2.write('set style 12\n')

        t.write('set autoflag 1\n')
        self.expect('Auto-flagging enabled.', t)

        t.write('match testplayer white 0+1 u\n')
        self.expect('Challenge:', t2)
        t2.write('accept\n')

        self.expect('<12> ', t)
        self.expect('<12> ', t2)

        moves = ['e4', 'e5', 'Nc3', 'Bc5', 'f4', 'exf4', 'Nf3', 'Qf6', 'd4', 'Bb4', 'e5', 'Bxc3+', 'bxc3', 'Qf5', 'Bd3', 'Qg4', 'O-O', 'g5', 'g3', 'fxg3', 'Nxg5', 'gxh2+', 'Kxh2', 'Qh4+', 'Kg2', 'Nh6', 'Rh1', 'Qg4+', 'Qxg4', 'Nxg4', 'Nxh7', 'Rxh7', 'Rxh7', 'd5', 'exd6', 'Be6', 'dxc7', 'Na6', 'Bg5', 'Kd7', 'Bd8', 'Rxd8', 'cxd8=Q+', 'Kxd8', 'Re1', 'Nf6', 'Rxe6', 'fxe6', 'Rxb7', 'Nc7', 'Rxa7', 'Nfd5', 'c4', 'Nf4+', 'Kf3', 'Nxd3', 'cxd3', 'Kd7', 'Rxc7+', 'Kd6', 'Ke4', 'Kxc7', 'Ke5', 'Kd7', 'd5', 'exd5', 'cxd5', 'Kc7', 'd6+', 'Kd7']

        wtm = True
        for mv in moves:
            if wtm:
                t.write('%s\n' % mv)
            else:
                t2.write('%s\n' % mv)
            self.expect('<12> ', t, timeout=4)
            self.expect('<12> ', t2, timeout=4)
            wtm = not wtm

        assert(wtm)
        time.sleep(45)

        t.write('time\n')

        self.expect('{Game 1 (admin vs. TestPlayer) admin ran out of time and TestPlayer lacks mating material} 1/2-1/2', t, timeout=20)
        self.expect('{Game 1 (admin vs. TestPlayer) admin ran out of time and TestPlayer lacks mating material} 1/2-1/2', t2)

        t.write('aclearhist admin\n')
        self.expect('History of admin cleared.', t)

        self.close(t)
        self.close(t2)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

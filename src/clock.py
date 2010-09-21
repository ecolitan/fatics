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

import timer
import online

from game_constants import *
from config import config


running_clocks = []
clock_names = {}

class Clock(object):
    def __init__(self):
        self.is_ticking = False
        running_clocks.append(self)
        self.started_time = None

    def start(self, side):
        self.is_ticking = True
        self._side_ticking = side
        self.started_time = time.time()

    def stop(self):
        self.is_ticking = False

    def get_white_time(self):
        ret = self._white_time
        if self.is_ticking and self._side_ticking == WHITE:
            ret -= time.time() - self.started_time
        return ret

    def get_black_time(self):
        ret = self._black_time
        if self.is_ticking and self._side_ticking == BLACK:
            ret -= time.time() - self.started_time
        return ret

    def check_flag(self, game, side):
        """Check the flag of the given side.  Return True if the flag
        call was sucessful."""
        assert(game.is_active)
        if side == WHITE:
            if self.get_white_time() <= 0:
                if self.get_black_time() <= 0:
                    game.result('Both players ran out of time', '1/2-1/2')
                elif not game.variant.pos.black_has_mating_material:
                    game.result('%s ran out of time and %s lacks mating material' % (game.white.name, game.black.name), '1/2-1/2')
                else:
                    game.result('%s forfeits on time' % game.white.name, '0-1')
        else:
            # check black's flag
            if self.get_black_time() <= 0:
                if self.get_white_time() <= 0:
                    game.result('Both players ran out of time', '1/2-1/2')
                elif not game.variant.pos.white_has_mating_material:
                    game.result('%s ran out of time and %s lacks mating material' % (game.black.name, game.white.name), '1/2-1/2')
                else:
                    game.result('%s forfeits on time' % game.black.name, '1-0')
        return not game.is_active

class FischerClock(Clock):
    def __init__(self, white_start, black_start, inc):
        super(FischerClock, self).__init__()
        self._white_time = white_start
        self._black_time = black_start
        self.inc = inc

    def got_move(self, side, ply, elapsed=None):
        """ Stop the clock, and record the time remaining for the player
        whose clock was ticking.  Returns the time taken for the move.
        If elapsed is supplied, it is used as the time taken instead
        of the wall-clock time (this is used for timeseal). """
        assert(self.is_ticking)
        assert(self._side_ticking == side)

        self.stop()
        if elapsed is None:
            # no timeseal, so use our own timer
            elapsed = time.time() - self.started_time
        if side == WHITE:
            self._white_time -= elapsed
        else:
            self._black_time -= elapsed
        return elapsed

    def add_increment(self, side):
        if side == WHITE:
            self._white_time += self.inc
        else:
            self._black_time += self.inc
clock_names['fischer'] = FischerClock


class BronsteinClock(Clock):
    def __init__(self, white_start, black_start, inc):
        super(BronsteinClock, self).__init__()
        self._white_time = white_start
        self._black_time = black_start
        self.inc = inc
        self.last_elapsed = None

    def got_move(self, side, ply, elapsed=None):
        """ Stop the clock, and record the time remaining for the player
        whose clock was ticking.  Returns the time taken for the move.
        If elapsed is supplied, it is used as the time taken instead
        of the wall-clock time (this is used for timeseal). """
        assert(self.is_ticking)
        assert(self._side_ticking == side)

        self.stop()
        if elapsed is None:
            # no timeseal, so use our own timer
            elapsed = time.time() - self.started_time
        if side == WHITE:
            self._white_time -= elapsed
        else:
            self._black_time -= elapsed
        self.last_elapsed = elapsed
        return elapsed

    def add_increment(self, side):
        assert(self.last_elapsed is not None)
        inc = min(self.last_elapsed, self.inc)

        if side == WHITE:
            self._white_time += inc
        else:
            self._black_time += inc
clock_names['bronstein'] = BronsteinClock

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

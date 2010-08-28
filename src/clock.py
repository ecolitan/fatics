import time

import timer
from game_constants import *

class Clock(object):
    pass

running_clocks = []

def heartbeat():
    pass

class FischerClock(Clock):
    def __init__(self, white_start, black_start, inc):
        self.is_ticking = False
        self._white_time = white_start
        self._black_time = black_start
        self.inc = inc
        running_clocks.append(self)
        self.started_time = None

    def start(self, side):
        self.is_ticking = True
        self._side_ticking = side
        self.started_time = time.time()

    def update(self, side, elapsed=None):
        """Record the time remaining for the player whose clock was
        ticking, and stop the clock.  Returns a string representing
        the time taken for the move."""
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

    def add_increment(self, side):
        if side == WHITE:
            self._white_time += self.inc
        else:
            self._black_time += self.inc

    def stop(self):
        self.is_ticking = False

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

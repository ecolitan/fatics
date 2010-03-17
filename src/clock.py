import time

from game import WHITE, BLACK
import timer

class Clock(object):
    pass

running_clocks = []

def heartbeat():
    pass

class FischerClock(Clock):
    def __init__(self, white_start, black_start, white_inc, black_inc):
        self.is_ticking = False
        self.white_time = white_start
        self.black_time = black_start
        self.white_inc = white_inc
        self.black_inc = black_inc
        running_clocks.append(self)
        self.started_time = None
        self.last_move_time_str = '%s' % timer.timer.hms(0)
    
    def start(self, side):
        self.is_ticking = True
        self.started_time = time.time()

    def update(self, side):
        elapsed = time.time() - self.started_time
        self.last_move_time_str = '%s' % timer.timer.hms(elapsed)
        if side == WHITE:
            self.white_time -= elapsed
        else:
            self.black_time -= elapsed

    def check_flag(self, game, side):
        """Check the flag of the given side.  Return True if the flag
        call was sucessful."""
        assert(game.is_active)
        if side == WHITE:
            if self.white_time <= 0:
                if self.black_time <= 0:
                    game.result('Both players ran out of time' % game.white.name, '1/2-1/2')
                elif not game.variant.pos.black_has_mating_material:
                    game.result('%s ran out of time and %s lacks mating material' % (game.white.name, game.black.name), '1/2-1/2')
                else:
                    game.result('%s forfeits on time' % game.white.name, '0-1')
        else:
            # check black's flag
            if self.black_time <= 0:
                assert(self.white_time > 0)
                if not game.variant.pos.white_has_mating_material:
                    game.result('%s ran out of time and %s lacks mating material' % (game.black.name, game.white.name), '1/2-1/2')
                else:
                    game.result('%s forfeits on time' % game.black.name, '1-0')
        return not game.is_active

    def add_increment(self, side):
        if side == WHITE:
            self.white_time += self.white_inc
        else:
            self.white_time += self.black_inc

    def stop(self):
        self.is_ticking = False

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

import time

import game
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
        if side == game.WHITE:
            self.white_time -= elapsed
        else:
            self.black_time -= elapsed

    def stop(self):
        self.is_ticking = False

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

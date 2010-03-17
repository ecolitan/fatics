import random

(WHITE, BLACK) = range(2)

import clock

games = {}

from variant.variant_factory import variant_factory

def opp(side):
    assert side in [WHITE, BLACK]
    return BLACK if side==WHITE else WHITE

def side_to_str(side):
    assert side in [WHITE, BLACK]
    return "white" if side==WHITE else "black"

def find_free_slot():
    """Find the first available game number."""
    # This is O(n) in the number of games, but it's simple and should
    # be more than efficient enough.
    i = 1
    while True:
        if i not in games:
            return i
        i += 1

class Game(object):
    def __init__(self, chal):
        self.number = find_free_slot()
        games[self.number] = self
        side = chal.side
        if side == None:
            side = self._pick_color(chal.a, chal.b)
        if side == WHITE:
            self.white = chal.a
            self.black = chal.b
            self.white_time = chal.a_time
            self.black_time = chal.b_time
            self.white_inc = chal.a_inc
            self.black_inc = chal.b_inc
            self.white_rating = chal.a_rating
            self.black_rating = chal.b_rating
        else:
            assert(side == BLACK)
            self.white = chal.b
            self.black = chal.a
            self.white_time = chal.b_time
            self.black_time = chal.a_time
            self.white_inc = chal.b_inc
            self.black_inc = chal.a_inc
            self.white_rating = chal.b_rating
            self.black_rating = chal.a_rating

        self.white.session.is_white = True
        self.black.session.is_white = False

        self.speed = chal.speed
        rated_str = 'rated' if chal.rated else 'unrated'
        if not chal.is_time_odds:
            time_str = '%d %d' % (self.white_time,self.white_inc)
        else:
            time_str = '%d %d %d %d' % (self.white_time,self.white_inc,self.blacck.time,self.black.inc)

        self.last_move_verbose = 'none'
        self.last_move_san = 'none'
        self.last_move_mins = 0
        self.last_move_secs = 0.0
        self.flip = False
        self.is_active = True

        self.pending_offers = []
        self.clock = clock.FischerClock(self.white_time * 60.0,
            self.black_time * 60.0, self.white_inc, self.black_inc)

        # Creating: GuestBEZD (0) admin (0) unrated blitz 2 12
        create_str = _('Creating: %s (%s) %s (%s) %s %s %s\n') % (self.white.name, self.white_rating, self.black.name, self.black_rating, rated_str, chal.variant_and_speed, time_str)
    
        self.white.write(create_str)
        self.black.write(create_str)
        
        create_str_2 = '\n{Game %d (%s vs. %s) Creating %s %s match.}\n' % (self.number, self.white.name, self.black.name, rated_str, chal.variant_and_speed)
        self.white.write(create_str_2)
        self.black.write(create_str_2)

        self.variant = variant_factory.get(chal.variant_name, self)

        #print('white: ' + self.variant.to_style12(self.white))
        #print('black: ' + self.variant.to_style12(self.black))
        self.white.send_board(self.variant)
        self.black.send_board(self.variant)

    def _pick_color(self, a, b): 
        return random.choice([WHITE, BLACK])

    def next_move(self):
        # decline all offers to the player who just moved
        u = self.get_user_to_move()
        offers = [o for o in self.pending_offers if o.a == u]
        for o in offers:
            o.decline()

        #print(self.variant.to_style12(self.white))
        if self.is_active and self.variant.pos.half_moves > 1:
            moved_side = opp(self.variant.get_turn())
            if self.clock.is_ticking:
                self.clock.update(moved_side)
            if self.get_user_to_move().vars['autoflag']:
                self.clock.check_flag(self, moved_side)
            if self.is_active:
                self.clock.add_increment(moved_side)
                self.clock.start(self.variant.get_turn())

        self.white.send_board(self.variant)
        self.black.send_board(self.variant)

        if self.variant.pos.is_checkmate:
            if self.variant.get_turn() == WHITE:
                self.result('%s checkmated' % self.white.name, '0-1')
            else:
                self.result('%s checkmated' % self.black.name, '1-0')
        elif self.variant.pos.is_stalemate:
            self.result('Game drawn by stalemate', '1/2-1/2')
        elif self.variant.pos.is_draw_nomaterial:
            self.result('Game drawn because neither player has mating material', '1/2-1/2')

    def get_user_side(self, user):
        if user == self.white:
            return WHITE
        elif user == self.black:
            return BLACK
        else:
            raise RuntimeError('Game.get_side(): got a non-player')
    
    def get_user_opp_side(self, user):
        if user == self.white:
            return BLACK
        elif user == self.black:
            return WHITE
        else:
            raise RuntimeError('Game.get_opp_side(): got a non-player')

    def get_side_user(self, side):
        if side == WHITE:
            return self.white
        else:
            return self.black

    def get_opp(self, user):
        side = self.get_user_side(user)
        return self.get_side_user(opp(side))
    
    def get_user_to_move(self):
        if self.variant.get_turn() == WHITE:
            return self.white
        else:
            return self.black
    
    def abort(self, msg):
        self.result(msg, '*')
    
    def resign(self, user):
        side = self.get_user_side(user)
        if side == WHITE:
            self.result('%s resigns' % user.name, '0-1')
        else:
            assert(side == BLACK)
            self.result('%s resigns' % user.name, '1-0')

    def result(self, msg, code):
        line = '\n{Game %d (%s vs. %s) %s} %s\n' % (self.number,
            self.white.name, self.black.name, msg, code)
        self.white.write(line)
        self.black.write(line)
        
        self.clock.stop()
        self.is_active = False
        self.free()

    def free(self):
        for o in self.pending_offers:
            o.decline(notify=False)
        del games[self.number]
        del self.white.session.games[self.black.name]
        del self.black.session.games[self.white.name]

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

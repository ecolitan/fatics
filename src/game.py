import random

from variant.variant_factory import variant_factory

(WHITE, BLACK) = range(2)
def opp(side):
    assert side in [WHITE, BLACK]
    return BLACK if side==WHITE else WHITE

def side_to_str(side):
    assert side in [WHITE, BLACK]
    return "white" if side==WHITE else "black"

class Game(object):
    def __init__(self, offer):
        side = offer.side
        if side == None:
            side = self._pick_color(offer.player_a.user, offer.player_b.user)
        if side == WHITE:
            self.white = offer.player_a
            self.black = offer.player_b
        else:
            assert(side == BLACK)
            self.white = offer.player_b
            self.black = offer.player_a

        self.white.user.session.is_white = True
        self.black.user.session.is_white = False

        self.speed = offer.speed
        rated_str = 'rated' if offer.rated else 'unrated'
        if not offer.is_time_odds:
            time_str = '%d %d' % (self.white.time,self.white.inc)
        else:
            time_str = '%d %d %d %d' % (self.white.time,self.white.inc,self.blacck.time,self.black.inc)
        self.white_clock = self.white.time*60.0
        self.black_clock = self.black.time*60.0

        # Creating: GuestBEZD (0) admin (0) unrated blitz 2 12
        create_str = 'Creating: %s (%s) %s (%s) %s %s %s\n' % (self.white.user.name, self.white.rating, self.black.user.name, self.black.rating, rated_str, offer.variant_and_speed, time_str)
    
        self.white.user.write(create_str)
        self.black.user.write(create_str)

        self.variant = variant_factory.get(offer.variant_name)

    def _pick_color(self, a, b): 
        return random.choice([WHITE, BLACK])

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

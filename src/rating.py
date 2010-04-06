import glicko2
import speed_variant
import datetime

from db import db

INITIAL_RATING = 1720
INITIAL_RD = 350

# I solved 350 = sqrt(0^2 + 1051897*vol^2), so a rd of 0 would increase to
# 350 in about 2 years.
INITIAL_VOLATILITY = .00196 # 0.6

class Rating(object):
    def __init__(self, rating, rd, volatility, ltime, best=None,
            when_best=None):
        self.rating = rating
        self.rd = rd
        self.volatility = volatility
        self.best = best
        self.when_best = when_best
        self.ltime = ltime
	assert(self.ltime is not None)

    def glicko2_rating(self):
        return (self.rating - 1500) / glicko2.scale

    def glicko2_rd(self):
        return self.rd / glicko2.scale

    def __str__(self):
        return str(self.rating)

class NoRating(object):
    def __init__(self, is_guest):
        self.is_guest = is_guest
        self.rating = INITIAL_RATING
	self.ltime = datetime.datetime.utcnow()
        self.volatility = INITIAL_VOLATILITY

    def glicko2_rating(self):
        assert(not self.is_guest)
        return (INITIAL_RATING - 1500) / glicko2.scale

    def glicko2_rd(self):
        assert(not self.is_guest)
        return INITIAL_RD / glicko2.scale

    def __str__(self):
        if self.is_guest:
            return '++++'
        else:
            return '----'

def update_ratings(game, white_score, black_score):
    wp = glicko2.Player(game.white_rating.glicko2_rating(),
        game.white_rating.glicko2_rd(), game.white_rating.volatility,
        game.white_rating.ltime)
    wp.update_player([game.black_rating.glicko2_rating()],
        [game.black_rating.glicko2_rd()], [white_score])

    bp = glicko2.Player(game.black_rating.glicko2_rating(),
        game.black_rating.glicko2_rd(), game.black_rating.volatility,
        game.black_rating.ltime)
    bp.update_player([game.white_rating.glicko2_rating()],
        [game.white_rating.glicko2_rd()], [black_score])

    if white_score == 0.0:
        (white_wins, white_losses, white_draws, white_total) = (0, 1, 0, 1)
    elif white_score == 0.5:
        (white_wins, white_losses, white_draws, white_total) = (0, 0, 1, 1)
    elif white_score == 1.0:
        (white_wins, white_losses, white_draws, white_total) = (1, 0, 0, 1)
    else:
        raise RuntimeError('rating.update_ratings(): unexpected score')
    if black_score == 0.0:
        (black_wins, black_losses, black_draws, black_total) = (0, 1, 0, 1)
    elif black_score == 0.5:
        (black_wins, black_losses, black_draws, black_total) = (0, 0, 1, 1)
    elif black_score == 1.0:
        (black_wins, black_losses, black_draws, black_total) = (1, 0, 0, 1)
    else:
        raise RuntimeError('rating.update_ratings(): unexpected score')

    wpg = wp.get_glicko()
    bpg = bp.get_glicko()

    ltime = datetime.datetime.utcnow()

    game.white.update_rating(game.speed_variant,
        wpg.rating, wpg.rd, wp.vol,
        white_wins, white_losses, white_draws, white_total, ltime)
    game.black.update_rating(game.speed_variant,
        bpg.rating, bpg.rd, bp.vol,
        black_wins, black_losses, black_draws, black_total, ltime)

def show_ratings(user, conn):
    rows = db.user_get_ratings(user.id)
    if not rows:
        conn.write(_('%s has not played any rated games.\n\n') % user.name)
    else:
        conn.write(_('speed & variant         rating  RD    Volat.    total  best\n'))
        for row in rows:
            ent = {}
            ent['speed_variant'] = str(speed_variant.from_ids(row['speed_id'], row['variant_id']))
            r = Rating(row['rating'], row['rd'],
                row['volatility'], row['ltime'])
            p = glicko2.Player(r.glicko2_rating(), r.glicko2_rd(),
                r.volatility, r.ltime)
            r = p.get_glicko()
            ent['rating'] = r.rating
            ent['rd'] = r.rd
            ent['volatility'] = r.volatility
            if row['best'] is None:
                ent['best_str'] = ''
            else:
                ent['best_str'] = '%4d %10s' % (row['best'], row['when_best'])
            ent['total'] = row['total']
            conn.write('%(speed_variant)-24s %(rating)-6d %(rd)-3.0f %(volatility)9.6f %(total)7d %(best_str)s\n' % ent)
        conn.write('\n')


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

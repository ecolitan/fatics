import glicko2

from db import db

INITIAL_RATING = 1720
INITIAL_RD = 350

class Rating(object):
    def __init__(self, rating, rd, volatility): #, win, loss, draw, total):
        self.rating = rating
        self.rd = rd
        self.volatility = volatility

    def glicko2_rating(self):
        return (self.rating - 1500) / glicko2.scale

    def glicko2_rd(self):
        return self.rd / glicko2.scale

    def __str__(self):
        return str(self.rating)

class NoRating(object):
    def __init__(self, is_guest):
        self.is_guest = is_guest
        self.rating = None

    def __str__(self):
        if self.is_guest:
            return '++++'
        else:
            return '----'

def update_ratings(game, white_score, black_score):
    wp = glicko2.Player(game.white_rating.glicko2_rating(),
        game.white_rating.glicko2_rd(), game.white_rating.volatility)
    wp.update_player([game.black_rating.glicko2_rating()],
        [game.black_rating.glicko2_rd()], [white_score])

    bp = glicko2.Player(game.black_rating.glicko2_rating(),
        game.black_rating.glicko2_rd(), game.black_rating.volatility)
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

    game.white.update_rating(game.white.id, game.speed_id, game.variant.id,
        wpg.rating, wpg.rd, wp.vol,
        white_wins, white_losses, white_draws, white_total)
    game.black.update_ratings(game.black.id, game.speed_id, game.variant.id,
        bpg.rating, bpg.rd, bp.vol,
        black_wins, black_losses, black_draws, black_total)

def show_ratings(user, conn):
    rows = db.user_get_ratings(user.id)
    if not rows:
        conn.write(_('%s has not played any rated games.\n\n') % user.name)
    else:
        conn.write(_('speed, variant          rating   RD  Vol. total  best\n'))
        for row in rows:
            row['speed_variant'] = '%(speed)s %(variant)s' % row
            row['total'] = row['win'] + row['loss'] + row['draw']
            conn.write(_('%(speed_variant)-15s %(rating)4s %(rd)3.0s %(volatility)4.3s %(total)7s %(best)4s %(when_best)10s\n') % row)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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
    def __init__(self, rating, rd, volatility, ltime, win, loss, draw,
            best=None, when_best=None):
        self.rating = rating
        self.rd = rd
        self.volatility = volatility
        self.win = win
        self.loss = loss
        self.draw = draw
        self.best = best
        self.when_best = when_best
        self.ltime = ltime

    def glicko2_rating(self):
        return (self.rating - INITIAL_RATING) / glicko2.scale

    def glicko2_rd(self):
        return self.rd / glicko2.scale

    def ginfo_str(self):
        return str(self.rating)

    def __str__(self):
        return str(self.rating)

    def __int__(self):
        return self.rating

class NoRating(object):
    def __init__(self, is_guest):
        self.is_guest = is_guest
        self.rating = INITIAL_RATING
        self.ltime = datetime.datetime.utcnow()
        self.volatility = INITIAL_VOLATILITY
        self.win = 0
        self.loss = 0
        self.draw = 0

    def glicko2_rating(self):
        assert(not self.is_guest)
        return (INITIAL_RATING - INITIAL_RATING) / glicko2.scale

    def glicko2_rd(self):
        assert(not self.is_guest)
        return INITIAL_RD / glicko2.scale

    def ginfo_str(self):
        #return '0P'
        return '0'

    def __str__(self):
        if self.is_guest:
            return '++++'
        else:
            return '----'

    def __int__(self):
        return 0

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

    white_win = game.white_rating.win
    white_loss = game.white_rating.loss
    white_draw = game.white_rating.draw
    black_win = game.black_rating.win
    black_loss = game.black_rating.loss
    black_draw = game.black_rating.draw
    assert(black_score + white_score == 1.0)
    if white_score == 0.0:
        white_loss += 1
        black_win += 1
    elif white_score == 0.5:
        white_draw += 1
        black_draw += 1
    elif white_score == 1.0:
        white_win += 1
        black_loss += 1
    else:
        raise RuntimeError('rating.update_ratings(): unexpected score')

    white_rating = wp.get_glicko_rating()
    white_rd = wp.get_glicko_rd()
    black_rating = bp.get_glicko_rating()
    black_rd = bp.get_glicko_rd()

    ltime = datetime.datetime.utcnow()

    game.white.set_rating(game.speed_variant,
        white_rating, white_rd, wp.vol,
        white_win, white_loss, white_draw, ltime)
    game.black.set_rating(game.speed_variant,
        black_rating, black_rd, bp.vol,
        black_win, black_loss, black_draw, ltime)

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
                row['volatility'], row['ltime'], row['win'], row['loss'],
                row['draw'])
            p = glicko2.Player(r.glicko2_rating(), r.glicko2_rd(),
                r.volatility, r.ltime)
            ent['rating'] = p.get_glicko_rating()
            ent['rd'] = p.get_glicko_rd()
            ent['volatility'] = r.volatility
            if row['best'] is None:
                ent['best_str'] = ''
            else:
                ent['best_str'] = '%4d %10s' % (row['best'], row['when_best'])
            ent['total'] = row['total']
            conn.write('%(speed_variant)-24s %(rating)-6d %(rd)-3.0f %(volatility)9.6f %(total)7d %(best_str)s\n' % ent)
        conn.write('\n')


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

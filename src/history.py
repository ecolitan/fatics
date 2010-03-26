from db import db

class History(object):
    def save(self, game, msg, result_code):
        if 'by adjudication' in msg:
            result_reason = 'Adj'
        elif 'by agreement' in msg:
            result_reason = 'Agr'
        elif 'by disonnection' in msg:
            result_reason = 'Dis'
        elif 'forfeits on time' in msg:
            result_reason = 'Fla'
        elif 'checkmated' in msg:
            result_reason = 'Mat'
        elif 'neither player has mating material' in msg:
            result_reason = 'NM'
        elif 'by repetition' in msg:
            result_reason = 'Rep'
        elif 'resigns' in msg:
            result_reason = 'Res'
        elif 'ran out of time' in msg:
            result_reason = 'TM'
        # TODO add suicide PLM and WNM
        elif '50 move rule' in msg:
            result_reason = '50'
        else:
            raise RuntimeError('could not abbreviate result message: %s' % msg)

        try:
            white_rating = int(game.white_rating, 10)
        except ValueError:
            white_rating = None

        try:
            black_rating = int(game.black_rating, 10)
        except ValueError:
            black_rating = None

        (i, eco, long) = game.get_eco()
        db.game_add(game.white.name, white_rating, game.black.name,
            black_rating, eco, game.variant.name, game.speed,
            game.white_time, game.white_inc, result_code, game.rated,
            result_reason)

history = History()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

#from db import db

class History(object):
    def save(self, game, msg, result):
        if 'by adjudication' in msg:
            res = 'Adj'
        elif 'by agreement' in msg:
            res = 'Agr'
        elif 'by disonnection' in msg:
            res = 'Dis'
        elif 'forfeits on time' in msg:
            res = 'Fla'
        elif 'checkmated' in msg:
            res = 'Mat'
        elif 'neither player has mating material' in msg:
            res = 'NM'
        elif 'by repetition' in msg:
            res = 'Rep'
        elif 'resigns' in msg:
            res = 'Res'
        elif 'ran out of time' in msg:
            res = 'TM'
        # TODO add suicide PLM and WNM
        elif '50 move rule' in msg:
            res = '50'
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

        #db.game_add(game.white.id, white_rating, game.black.id,
        #    black_rating, game.get_eco(), 

history = History()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

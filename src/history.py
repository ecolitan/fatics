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

def show_for_user(user, conn):
    hist = db.history_get(user.name)
    if not hist:
        conn.write(_('%s has no history games.\n') % user.name)
        return

    conn.write(_('History for %s:\n') % user.name)
    conn.write(_('                  Opponent      Type         ECO End Date\n'))
    i = 1
    for row in db.history_get(user.name):
        if row['white_name'] == user.name:
            color_char = 'W'
            user_rating = row['white_rating']
            opp_rating = row['black_rating']
            opp_name = row['black_name']
            if row['result'] == '1-0':
                result_char = '+'
            elif row['result'] == '1/2-1/2':
                result_char = '='
            else:
                assert(row['result'] == '0-1')
                result_char = '-'
        else:
            assert(row['black_name'] == user.name)
            color_char = 'B'
            user_rating = row['black_rating']
            opp_rating = row['white_rating']
            opp_name = row['white_name']
            if row['result'] == '1-0':
                result_char = '-'
            elif row['result'] == '1/2-1/2':
                result_char = '='
            else:
                assert(row['result'] == '0-1')
                result_char = '+'
        conn.write('%2d %s %4s %s %4s %15s' % (i, result_char, user_rating,
            color_char, opp_rating, opp_name))
        i += 1

history = History()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

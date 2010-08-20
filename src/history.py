from db import db

class History(object):
    def save_game(self, game, msg, result_code):
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
        elif 'stalemate' in msg:
            result_reason = 'Sta'
        elif 'resigns' in msg:
            result_reason = 'Res'
        elif 'ran out of time' in msg:
            result_reason = 'TM'
        # TODO add suicide PLM and WNM
        elif '50 move rule' in msg:
            result_reason = '50'
        else:
            raise RuntimeError('could not abbreviate result message: %s' % msg)

        white_rating = str(game.white_rating)
        black_rating = str(game.black_rating)

        (i, eco, longeco) = game.get_eco()
        game_id = db.game_add(game.white.name, white_rating, game.black.name,
            black_rating, eco, game.variant.name, game.speed_variant.speed,
            game.white_time, game.inc, result_code, game.rated,
            result_reason, game.get_moves(), game.when_ended)

        flags = '%s%s' % (game.speed_variant.speed.abbrev,
            game.speed_variant.variant.abbrev)

        flags += 'r' if game.rated else 'u'

        if result_code == '1-0':
            white_result_char = '+'
            black_result_char = '-'
        elif result_code == '0-1':
            white_result_char = '-'
            black_result_char = '+'
        else:
            assert(result_code == '1/2-1/2')
            white_result_char = '='
            black_result_char = '='
        game.white.save_history(game_id, white_result_char,
            white_rating, 'W', game.black.name, black_rating,
            eco[0:3], flags, game.white_time, game.inc, result_reason,
            game.when_ended)
        game.black.save_history(game_id, black_result_char,
            black_rating, 'B', game.white.name, white_rating,
            eco[0:3], flags, game.white_time, game.inc, result_reason,
            game.when_ended)
        return game_id

def show_for_user(user, conn):
    hist = user.get_history()
    if not hist:
        conn.write(_('%s has no history games.\n') % user.name)
        return
        

    conn.write(_('History for %s:\n') % user.name)
    conn.write(_('                  Opponent      Type         ECO End Date\n'))
    for entry in hist:
        entry['when_ended_str'] = entry['when_ended'].strftime("%Y-%m-%d %H:%M %Z")
        entry['opp_str'] = entry['opp_name'][0:14]
        conn.write('%(num)2d: %(result_char)1s %(user_rating)4s %(color_char)1s %(opp_rating)4s %(opp_str)-14s[%(flags)3s%(time)3s %(inc)3s] %(eco)-3s %(result_reason)-3s %(when_ended_str)-s\n' %
            entry)

history = History()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

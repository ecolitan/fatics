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

from MySQLdb import connect, cursors, IntegrityError
from config import config

class DuplicateKeyError(Exception):
    pass
class DeleteError(Exception):
    pass

class DB(object):
    def __init__(self):
        self.db = connect(host=config.db_host, db=config.db_db,
            read_default_file="~/.my.cnf")
        cursor = self.db.cursor()
        cursor.execute("""SET time_zone='+00:00'""")
        cursor.close()

    def user_get(self, name):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT user_id,user_name,user_passwd,user_last_logout,user_admin_level,user_email,user_real_name FROM user WHERE user_name=%s""", (name,))
        row = cursor.fetchone()
        cursor.close()
        return row

    def user_get_vars(self, user_id, vnames):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute(("SELECT %s" % ','.join(vnames)) +
            " FROM user WHERE user_id=%s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        return row

    def user_set_var(self, user_id, name, val):
        cursor = self.db.cursor()
        up = """UPDATE user SET %s""" % name
        cursor.execute(up + """=%s WHERE user_id=%s""", (val,user_id))
        cursor.close()

    def user_get_formula(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT num,f FROM formula WHERE user_id=%s ORDER BY num ASC""", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def user_set_formula(self, user_id, name, val):
        # ON DUPLICATE KEY UPDATE is probably not very portable to
        # other databases, but this shouldn't be hard to rewrite
        dbkeys = {'formula': 0, 'f1': 1, 'f2': 2, 'f3': 3, 'f4': 4, 'f5': 5, 'f6': 6, 'f7': 7, 'f8': 8, 'f9': 9}
        assert(name in dbkeys.keys())
        num = dbkeys[name]
        cursor = self.db.cursor()
        if val is not None:
            cursor.execute("""INSERT INTO formula SET user_id=%s,num=%s,f=%s ON DUPLICATE KEY UPDATE f=%s""", (user_id,num,val,val))
        else:
            # OK to not actually delete any rows; we are just unsetting an
            # already unset variable.
            cursor.execute("""DELETE FROM formula WHERE user_id=%s AND num=%s""", (user_id,num))
            assert(cursor.rowcount <= 1)
        cursor.close()

    def user_get_notes(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT num,txt FROM note WHERE user_id=%s ORDER BY num ASC""", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def user_set_note(self, user_id, name, val):
        num = int(name, 10)
        assert(num >= 1 and num <= 10)
        cursor = self.db.cursor()
        if val is not None:
            cursor.execute("""INSERT INTO note SET user_id=%s,num=%s,txt=%s ON DUPLICATE KEY UPDATE txt=%s""" , (user_id,num,val,val))
        else:
            cursor.execute("""DELETE FROM note WHERE user_id=%s AND num=%s""", (user_id,num))
            if cursor.rowcount != 1:
                cursor.close()
                raise DeleteError()
        cursor.close()

    def user_set_alias(self, user_id, name, val):
        cursor = self.db.cursor()
        if val is not None:
            cursor.execute("""INSERT INTO user_alias SET user_id=%s,name=%s,val=%s ON DUPLICATE KEY UPDATE val=%s""" , (user_id,name,val,val))
        else:
            cursor.execute("""DELETE FROM user_alias WHERE user_id=%s AND name=%s""", (user_id,name))
            if cursor.rowcount != 1:
                cursor.close()
                raise DeleteError()
        cursor.close()

    def user_get_aliases(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT name,val FROM user_alias WHERE user_id=%s ORDER BY name ASC""", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def user_get_matching(self, prefix):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT user_id,user_name,user_passwd,user_last_logout,user_admin_level,user_email,user_real_name FROM user WHERE user_name LIKE %s LIMIT 8""", (prefix + '%',))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def user_add(self, name, email, passwd, real_name, admin_level):
        cursor = self.db.cursor()
        cursor.execute("""INSERT INTO user SET user_name=%s,user_email=%s,user_passwd=%s,user_real_name=%s,user_admin_level=%s""", (name,email,passwd,real_name,admin_level))
        cursor.close()

    def user_set_passwd(self, id, passwd):
        cursor = self.db.cursor()
        cursor.execute("""UPDATE user SET user_passwd=%s WHERE user_id=%s""", (passwd, id))
        cursor.close()

    def user_set_admin_level(self, id, level):
        cursor = self.db.cursor()
        cursor.execute("""UPDATE user SET user_admin_level=%s WHERE user_id=%s""", (str(level), id))
        cursor.close()

    def user_set_last_logout(self, id):
        cursor = self.db.cursor()
        cursor.execute("""UPDATE user SET user_last_logout=NOW() WHERE user_id='%s'""", (id,))
        cursor.close()

    def user_delete(self, id):
        cursor = self.db.cursor()
        cursor.execute("""DELETE FROM user WHERE user_id=%s""", (id,))
        if cursor.rowcount != 1:
            cursor.close()
            raise DeleteError()
        cursor.close()

    def user_get_channels(self, id):
        cursor = self.db.cursor() #cursors.DictCursor)
        cursor.execute("""SELECT channel_id FROM channel_user WHERE user_id=%s""", (id,))
        rows = cursor.fetchall()
        cursor.close()
        return [r[0] for r in rows]

    def channel_new(self, id, name):
        cursor = self.db.cursor()
        cursor.execute("""INSERT INTO channel SET channel_id=%s,name=%s,descr=NULL""", (id, name,))
        cursor.close()

    def channel_add_user(self, ch_id, user_id):
        cursor = self.db.cursor()
        cursor.execute("""INSERT INTO channel_user SET user_id=%s,channel_id=%s""", (user_id,ch_id))
        cursor.close()

    def channel_del_user(self, ch_id, user_id):
        cursor = self.db.cursor()
        cursor.execute("""DELETE FROM channel_user WHERE user_id=%s AND channel_id=%s""", (user_id,ch_id))
        if cursor.rowcount != 1:
            cursor.close()
            raise DeleteError()
        cursor.close()

    def channel_list(self):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT channel_id,name,descr FROM channel""")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def channel_get_members(self, id):
        cursor = self.db.cursor()
        cursor.execute("""SELECT user_name FROM channel_user LEFT JOIN user USING (user_id) WHERE channel_id=%s""", (id,))
        rows = cursor.fetchall()
        cursor.close()
        return [r[0] for r in rows]

    def user_add_title(self, user_id, title_id):
        cursor = self.db.cursor()
        try:
            cursor.execute("""INSERT INTO user_title SET user_id=%s,title_id=%s""", (user_id,title_id))
            cursor.close()
        except IntegrityError:
            cursor.close()
            raise DuplicateKeyError()

    def user_del_title(self, user_id, title_id):
        cursor = self.db.cursor()
        cursor.execute("""DELETE FROM user_title WHERE user_id=%s AND title_id=%s""", (user_id,title_id))
        if cursor.rowcount != 1:
            cursor.close()
            raise DeleteError()
        cursor.close()

    def user_get_titles(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT title_name,title_flag,title_light FROM user_title LEFT JOIN title USING (title_id) WHERE user_id=%s ORDER BY title_id DESC""", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    # notifications
    def user_add_notification(self, notified, notifier):
        cursor = self.db.cursor()
        try:
            cursor.execute("""INSERT INTO user_notify SET notified=%s,notifier=%s""", (notified,notifier))
        except IntegrityError:
            raise DuplicateKeyError()
        finally:
            cursor.close()

    def user_del_notification(self, notified, notifier):
        cursor = self.db.cursor()
        cursor.execute("""DELETE FROM user_notify WHERE notified=%s AND notifier=%s""", (notified,notifier))
        if cursor.rowcount != 1:
            cursor.close()
            raise DeleteError()
        cursor.close()

    def user_get_notified(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT user_name FROM user LEFT JOIN user_notify ON (user.user_id=user_notify.notified) WHERE notifier=%s""", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def user_get_notifiers(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT user_name FROM user LEFT JOIN user_notify ON (user.user_id=user_notify.notifier) WHERE notified=%s""", (user_id,))
        rows = cursor.fetchall()
        return rows
    
    # censor
    def user_add_censor(self, censorer, censored):
        cursor = self.db.cursor()
        try:
            cursor.execute("""INSERT INTO censor SET censored=%s,censorer=%s""", (censored,censorer))
        except IntegrityError:
            raise DuplicateKeyError()
        finally:
            cursor.close()
    
    def user_del_censor(self, censorer, censored):
        cursor = self.db.cursor()
        cursor.execute("""DELETE FROM censor WHERE censored=%s AND censorer=%s""", (censored,censorer))
        if cursor.rowcount != 1:
            cursor.close()
            raise DeleteError()
        cursor.close()

    def user_get_censored(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT user_name FROM user LEFT JOIN censor ON (user.user_id=censor.censored) WHERE censorer=%s""", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    # noplay
    def user_add_noplay(self, noplayer, noplayed):
        cursor = self.db.cursor()
        try:
            cursor.execute("""INSERT INTO noplay SET noplayed=%s,noplayer=%s""", (noplayed,noplayer))
        except IntegrityError:
            raise DuplicateKeyError()
        finally:
            cursor.close()
    
    def user_del_noplay(self, noplayer, noplayed):
        cursor = self.db.cursor()
        cursor.execute("""DELETE FROM noplay WHERE noplayed=%s AND noplayer=%s""", (noplayed,noplayer))
        if cursor.rowcount != 1:
            cursor.close()
            raise DeleteError()
        cursor.close()
    
    def user_get_noplayed(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT user_name FROM user LEFT JOIN noplay ON (user.user_id=noplay.noplayed) WHERE noplayer=%s""", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def title_get_all(self):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT title_id,title_name,title_descr,title_flag,title_public FROM title""")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def title_get_users(self, title_id):
        cursor = self.db.cursor()
        cursor.execute("""SELECT user_name FROM user LEFT JOIN user_title USING(user_id) WHERE title_id=%s""", (title_id,))
        rows = cursor.fetchall()
        cursor.close()
        return [r[0] for r in rows]

    # eco
    def get_eco(self, hash):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT eco,long_ FROM eco WHERE hash=%s""", (hash,))
        row = cursor.fetchone()
        cursor.close()
        return row

    def get_nic(self, hash):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT nic FROM nic WHERE hash=%s""", (hash,))
        row = cursor.fetchone()
        cursor.close()
        return row

    def look_up_eco(self, eco):
        cursor = self.db.cursor(cursors.DictCursor)
        if len(eco) == 3:
            # match all subvariations
            eco = '%s%%' % eco
        cursor.execute("""SELECT eco,nic,long_,eco.fen AS fen FROM eco LEFT JOIN nic USING(hash) WHERE eco LIKE %s LIMIT 100""", (eco,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def look_up_nic(self, nic):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT eco,nic,long_,nic.fen AS fen FROM nic LEFT JOIN eco USING(hash) WHERE nic = %s LIMIT 100""", (nic,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    # game
    def game_add(self, white_name, white_rating, black_name, black_rating,
            eco, variant_id, speed_id, time, inc, rated, result, result_reason,
            ply_count, movetext, when_started, when_ended):
        cursor = self.db.cursor()
        cursor.execute("""INSERT INTO game SET white_name=%s,white_rating=%s,black_name=%s,black_rating=%s,eco=%s,variant_id=%s,speed_id=%s,time=%s,inc=%s,rated=%s,result=%s,result_reason=%s,ply_count=%s,movetext=%s,when_started=%s,when_ended=%s""", (white_name,
            white_rating, black_name, black_rating, eco, variant_id,
            speed_id, time, inc, rated, result, result_reason, ply_count,
            movetext, when_started, when_ended))
        game_id = cursor.lastrowid
        cursor.close()
        return game_id

    def user_get_history(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT game_id, num, result_char, user_rating, color_char, opp_name, opp_rating, eco, flags, time, inc, result_reason, when_ended FROM history WHERE user_id=%s""", user_id)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_history_game(self, user_id, num):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT white_name,white_rating,black_name,black_rating,game.eco,variant_id,speed_id,game.time,game.inc,rated,result,game.result_reason,ply_count,movetext,game.when_ended FROM game LEFT JOIN history USING (game_id) where user_id=%s AND num=%s""", (user_id, num))
        row = cursor.fetchone()
        cursor.close()
        return row

    def user_add_history(self, entry, user_id):
        cursor = self.db.cursor()
        entry.update({'user_id': user_id})
        cursor.execute("""DELETE FROM history WHERE user_id=%s AND num=%s""" % (user_id, entry['num']))
        cursor.execute("""INSERT INTO history SET user_id=%(user_id)s,game_id=%(game_id)s, num=%(num)s, result_char=%(result_char)s, user_rating=%(user_rating)s, color_char=%(color_char)s, opp_name=%(opp_name)s, opp_rating=%(opp_rating)s, eco=%(eco)s, flags=%(flags)s, time=%(time)s, inc=%(inc)s, result_reason=%(result_reason)s, when_ended=%(when_ended)s""", entry)
        cursor.close()

    def user_del_history(self, user_id):
        cursor = self.db.cursor()
        cursor.execute("""DELETE FROM history WHERE user_id=%s""", user_id)
        cursor.close()

    def user_get_ratings(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT * FROM (SELECT rating.variant_id as variant_id,rating.speed_id as speed_id,variant_name,speed_name,rating,rd,volatility,win,loss,draw,total,best,when_best,ltime FROM rating LEFT JOIN variant USING (variant_id) LEFT JOIN speed USING (speed_id) WHERE user_id=%s ORDER BY total DESC LIMIT 5) as tmp ORDER BY variant_id,speed_id""", user_id)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def user_get_all_ratings(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT variant_id,speed_id,rating,rd,volatility,win,loss,draw,total,best,when_best,ltime FROM rating WHERE user_id=%s""", user_id)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def user_set_rating(self, user_id, speed_id, variant_id,
            rating, rd, volatility, win, loss, draw, total, ltime):
        cursor = self.db.cursor()
        cursor.execute("""UPDATE rating SET rating=%s,rd=%s,volatility=%s,win=%s,loss=%s,draw=%s,total=%s,ltime=%s WHERE user_id = %s AND speed_id = %s and variant_id = %s""", (rating, rd, volatility, win, loss, draw, total, ltime, user_id, speed_id, variant_id))
        if cursor.rowcount == 0:
            cursor.execute("""INSERT INTO rating SET rating=%s,rd=%s,volatility=%s,win=%s,loss=%s,draw=%s,total=%s,ltime=%s,user_id=%s,speed_id=%s,variant_id=%s""", (rating, rd, volatility, win, loss, draw, total, ltime, user_id, speed_id, variant_id))
        assert(cursor.rowcount == 1)
        cursor.close()

    def user_del_rating(self, user_id, speed_id, variant_id):
        cursor = self.db.cursor()
        cursor.execute("""DELETE FROM rating WHERE user_id = %s AND speed_id = %s and variant_id = %s""", (user_id, speed_id, variant_id))
        cursor.close()

    def get_variants(self):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT variant_id,variant_name,variant_abbrev FROM variant""")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_speeds(self):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT speed_id,speed_name,speed_abbrev FROM speed""")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    # news
    def add_news(self, title, user, is_admin):
        is_admin = '1' if is_admin else '0'
        cursor = self.db.cursor()
        cursor.execute("""INSERT INTO news_index SET news_title=%s,news_poster=%s,news_date=UTC_DATE(),news_is_admin=%s""", (title,user.name,is_admin))
        news_id = cursor.lastrowid
        cursor.close()
        return news_id

    def delete_news(self, news_id):
        cursor = self.db.cursor()
        try:
            cursor.execute("""DELETE FROM news_index WHERE news_id=%s LIMIT 1""", (news_id,))
            if cursor.rowcount != 1:
                raise DeleteError()
            cursor.execute("""DELETE FROM news_line WHERE news_id=%s""", (news_id,))
        finally:
            cursor.close()

    def get_recent_news(self, is_admin):
        is_admin = '1' if is_admin else '0'
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT news_id,news_title,news_date,news_poster FROM news_index WHERE news_is_admin=%s ORDER BY news_id DESC LIMIT 10""", (is_admin,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    # messages
    # Use user variables to simulate enumerating messages for each user,
    # although no such numbers are actually stored in the table.
    def get_message_id(self, message_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT message_id,sender.user_name AS sender_name,forwarder.user_name AS forwarder_name,when_sent,txt FROM message LEFT JOIN user AS sender ON (message.from_user_id = sender.user_id) LEFT JOIN user AS forwarder ON (message.forwarder_user_id = forwarder.user_id) WHERE message_id=%s""",
            (message_id,))
        row = cursor.fetchone()
        cursor.close()
        return row

    def get_messages_all(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SET @i=0""")
        cursor.execute("""SELECT message_id,@i := @i + 1 AS num,sender.user_name AS sender_name,forwarder.user_name AS forwarder_name,when_sent,txt FROM message LEFT JOIN user AS sender ON (message.from_user_id = sender.user_id) LEFT JOIN user AS forwarder ON (message.forwarder_user_id = forwarder.user_id) WHERE to_user_id=%s ORDER BY message_id""",
            (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_messages_range(self, user_id, start, end):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SET @i=0""")
        cursor.execute("""SELECT * FROM (
                SELECT message_id,@i := @i + 1 AS num,from_user_id,sender.user_name AS sender_name,forwarder.user_name AS forwarder_name,when_sent,txt
                FROM message
                    LEFT JOIN user AS sender ON (message.from_user_id = sender.user_id)
                    LEFT JOIN user AS forwarder ON (message.forwarder_user_id = forwarder.user_id)
                WHERE to_user_id=%s ORDER BY message_id) AS t1
            WHERE num BETWEEN %s AND %s""", (user_id, start, end))
            #(user_id, start - 1, end - start + 1))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_messages_from_to(self, from_user_id, to_user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SET @i=0""")
        cursor.execute("""SELECT * FROM (SELECT message_id,@i := @i + 1 AS num,from_user_id,sender.user_name AS sender_name,forwarder.user_name AS forwarder_name,when_sent,txt FROM message LEFT JOIN user AS sender ON (message.from_user_id = sender.user_id) LEFT JOIN user AS forwarder ON (message.forwarder_user_id = forwarder.user_id) WHERE to_user_id=%s ORDER BY message_id) AS t1 WHERE from_user_id=%s""",
            (to_user_id, from_user_id))

        rows = cursor.fetchall()
        cursor.close()
        return rows


    def send_message(self, from_user_id, to_user_id, txt):
        cursor = self.db.cursor()
        cursor.execute("""INSERT INTO message SET from_user_id=%s,to_user_id=%s,txt=%s,when_sent=NOW(),unread=1""",
            (from_user_id, to_user_id, txt))
        message_id = cursor.lastrowid
        cursor.close()
        return message_id

    def forward_message(self, forwarder_user_id, to_user_id, message_id):
        cursor = self.db.cursor()
        cursor.execute("""INSERT INTO message (from_user_id,forwarder_user_id,to_user_id,txt,when_sent,unread)
            (SELECT from_user_id,%s,%s,txt,when_sent,1 FROM message
                WHERE message_id=%s)""",
            (forwarder_user_id,to_user_id,message_id))
        message_id = cursor.lastrowid
        cursor.close()
        return message_id

    def clear_messages_all(self, user_id):
        cursor = self.db.cursor()
        cursor.execute("""DELETE FROM message WHERE to_user_id=%s""",
            (user_id,))
        ret = cursor.rowcount
        cursor.close()
        return ret

    def clear_messages_list(self, lst):
        if not lst:
            return 0
        cursor = self.db.cursor()
        cursor.execute("""DELETE FROM message WHERE message_id IN (%s)""" %
            (','.join(lst),))
        ret = cursor.rowcount
        cursor.close()
        return ret

    def clear_messages_from_to(self, from_user_id, to_user_id):
        cursor = self.db.cursor()
        cursor.execute("""DELETE FROM message WHERE from_user_id=%s AND to_user_id=%s""",
            (from_user_id, to_user_id))
        ret = cursor.rowcount
        cursor.close()
        return ret

db = DB()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

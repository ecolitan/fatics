from MySQLdb import *
from config import config

class DuplicateKeyError(Exception):
    pass
class DeleteError(Exception):
    pass

class DB(object):
    def __init__(self):
        self.db = connect(host=config.db_host, db=config.db_db, user=config.db_user, passwd=config.db_passwd)

    def user_get(self, name):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT user_id,user_name,user_passwd,user_last_logout,user_admin_level,user_email FROM user WHERE user_name=%s""", (name,))
        row = cursor.fetchone()
        cursor.close()
        return row

    def user_get_vars(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT tell,shout,open,silence,bell,time,inc FROM user WHERE user_id=%s""", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        return row

    def user_set_var(self, user_id, name, val):
        cursor = self.db.cursor()
        up = """UPDATE user SET %s""" % name
        cursor.execute(up + """=%s WHERE user_id=%s""", (val,user_id))
        cursor.close()

    def user_set_formula(self, user_id, name, val):
        # ON DUPLICATE KEY UPDATE is probably not very portable to
        # other databases, but this shouldn't be hard to rewrite
        dbkeys = {'formula': 0, 'f1': 1, 'f2': 2, 'f3': 3, 'f4': 4, 'f5': 5, 'f6': 6, 'f7': 7, 'f8': 8, 'f9': 9}
        assert(name in dbkeys.keys())
        num = dbkeys[name]
        cursor = self.db.cursor()
        cursor.execute("""INSERT INTO formula SET user_id=%s,num=%d,f=%s ON DUPLICATE KEY UPDATE""" % (user_id,num,val))
        cursor.close()

    def user_set_note(self, user_id, name, val):
        num = int(name, 10)
        assert(num >= 1 and num <= 10)
        cursor = self.db.cursor()
        cursor.execute("""INSERT INTO note SET user_id=%s,num=%d,txt=%s ON DUPLICATE KEY UPDATE""" % (user_id,num,val))
        cursor.close()

    def user_get_matching(self, prefix):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT user_id,user_name,user_passwd,user_last_logout,user_admin_level,user_email FROM user WHERE user_name LIKE %s LIMIT 8""", (prefix + '%',))
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
        cursor.execute("""SELECT title_flag,display FROM user_title LEFT JOIN title USING (title_id) WHERE user_id=%s""", user_id)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    # notifications
    def user_add_notification(self, notified, notifier):
        cursor = self.db.cursor()
        try:
            cursor.execute("""INSERT INTO user_notify SET notified=%s,notifier=%s""", (notified,notifier))
        except IntegrityError:
            cursor.close()
            raise DuplicateKeyError()
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
        cursor.execute("""SELECT user_name FROM user LEFT JOIN user_notify ON (user.user_id=user_notify.notified) WHERE notifier=%s""", user_id)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def user_get_notifiers(self, user_id):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT user_name FROM user LEFT JOIN user_notify ON (user.user_id=user_notify.notifier) WHERE notified=%s""", user_id)
        rows = cursor.fetchall()
        return rows

    def title_get_all(self):
        cursor = self.db.cursor(cursors.DictCursor)
        cursor.execute("""SELECT title_id,title_name,title_descr,title_flag FROM title""")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def title_get_users(self, title_id):
        cursor = self.db.cursor()
        cursor.execute("""SELECT user_name FROM user LEFT JOIN user_title USING(user_id) WHERE title_id=%s""", title_id)
        rows = cursor.fetchall()
        cursor.close()
        return [r[0] for r in rows]

db = DB()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

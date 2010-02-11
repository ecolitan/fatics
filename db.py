from MySQLdb import *

class DB:
	def __init__(self):
		self.db = connect(host="localhost", db="chess", user="chess", passwd="Luu9yae7")

        """def query(self, s):
                self.db.query(s)

        def query(self, s):
                self.db.query(s)

        def fetch(self):
                res = self.db.store_result()
                return res.fetch_row()"""

        def get_user(self, name):
                cursor = self.db.cursor(cursors.DictCursor)
                cursor.execute("""SELECT user_id,user_name,user_passwd FROM user WHERE user_name=%s""", (name,))
                row = cursor.fetchone()
                return row

        def set_user_passwd(self, id, passwd):
                cursor = self.db.cursor()
                cursor.execute("""INSERT INTO USER SET user_passwd=%s WHERE user_id=%d""", (passwd, id))

        def set_user_admin_level(self, id, level):
                cursor = self.db.cursor()
                cursor.execute("""UPDATE user SET user_admin_level=%d WHERE user_id='%s'""" % (level, id))
                

db = DB()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

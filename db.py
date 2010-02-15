from MySQLdb import *

class DB:
	def __init__(self):
		self.db = connect(host="localhost", db="chess", user="chess", passwd="Luu9yae7")

        def get_user(self, name):
                cursor = self.db.cursor(cursors.DictCursor)
                cursor.execute("""SELECT user_id,user_name,user_passwd,user_last_logout FROM user WHERE user_name=%s""", (name,))
                row = cursor.fetchone()
                return row
        
        def user_add(self, name, email, passwd, real_name, admin_level):
                cursor = self.db.cursor(cursors.DictCursor)
                cursor.execute("""INSERT INTO user SET user_name=%s,user_email=%s,user_passwd=%s,user_real_name=%s,user_admin_level=%s""", (name,email,passwd,real_name,admin_level))

        def user_set_passwd(self, id, passwd):
                cursor = self.db.cursor()
                cursor.execute("""UPDATE user SET user_passwd=%s WHERE user_id=%s""", (passwd, id))

        def user_set_admin_level(self, id, level):
                cursor = self.db.cursor()
                cursor.execute("""UPDATE user SET user_admin_level=%d WHERE user_id=%s""", (level, id))

        def user_update_last_logout(self, id):
                cursor = self.db.cursor()
                cursor.execute("""UPDATE user SET user_last_logout=NOW() WHERE user_id='%s'""", (id,))
        

db = DB()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

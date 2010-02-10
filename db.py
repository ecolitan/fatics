from MySQLdb import *

class DB:
	def __init__(self):
		self.db = connect(host="localhost", db="chess", user="chess", passwd="Luu9yae7")

        def query(self, s):
                self.db.query(s)
                self.res = self.db.store_result()

        def fetch(self):
                return self.res.fetch_row()

db = DB()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

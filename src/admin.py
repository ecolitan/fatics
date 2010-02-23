class Level(object):
	user = 10
	admin = 100
	god = 1000

class Checker(object):
	'''Check whether one admin can perform an operation on
	another.'''
	def check_users(self, byuser, touser):
		return self.check_level(byuser.admin_level, touser.admin_level)
	
	def check_level(self, by_level, to_level):
		if by_level >= Level.god:
			return True
		else:
			return by_level > to_level


checker = Checker()

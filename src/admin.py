"""Define admin levels and provide routines that
check them."""

class Level(object):
    """represents admin levels"""
    user = 10
    admin = 100
    god = 1000
    head = 10000

    def __init__(self):
        pass
   
    def to_str(self, lvl):
        """convert the level to a string"""
        if lvl == self.head:
            return _('Head Administrator')
        elif lvl == self.god:
            return _('Super User')
        elif lvl == self.admin:
            return _('Administrator')
        else:
            return _('Unknown (%d)') % level
level = Level()

class Checker(object):
    '''Check whether one admin can perform an operation on
    another.'''
    def check_user_operation(self, byuser, touser):
        return self.check_level(byuser.admin_level, touser.admin_level)
    
    def check_level(self, by_level, to_level):
        if by_level >= Level.god and to_level < Level.head:
            return True
        else:
            return by_level > to_level


checker = Checker()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

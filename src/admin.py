class Level(object):
    user = 10
    admin = 100
    god = 1000
    head = 10000
    
    def to_str(self, level):
        if level == self.head:
            return _('Head Administrator')
        elif level == self.god:
            return _('Super User')
        elif level == self.admin:
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

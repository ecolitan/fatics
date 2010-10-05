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

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

import copy

class GameList(object):
    def __init__(self):
        self.games = {}

    def primary(self):
        return self.games.values()[0]

    def add(self, game, opp_name):
        assert(opp_name not in self.games)
        self.games[opp_name] = game

    def free(self, opp_name):
        del self.games[opp_name]

    def __len__(self):
        return len(self.games)

    def iter(self):
        return self.games.itervalues()

    def leave_all(self, user):
        # python docs: "Using iteritems() while adding or deleting entries
        # in the dictionary may raise a RuntimeError or fail to iterate
        # over all entries."
        for (k, v) in copy.copy(self.games).iteritems():
            v.leave(user)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

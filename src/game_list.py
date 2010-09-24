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
        self.games = []

    def primary(self):
        return self.games[0]

    def make_primary(self, game):
        self.games.remove(game)
        self.games.insert(0, game)

    def add(self, game):
        assert(game not in self.games)
        self.games.append(game)

    def remove(self, game):
        self.games.remove(game)

    def __len__(self):
        return len(self.games)

    def __nonzero__(self):
        return bool(self.games)

    def __iter__(self):
        return iter(self.games)

    def copy(self):
        return self.games[:]

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

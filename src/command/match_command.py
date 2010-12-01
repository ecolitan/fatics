# -*- coding: utf-8 -*-
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

import game
import match
import admin
import user
import speed_variant

from command import Command, ics_command
from online import online

@ics_command('match', 'wt', admin.Level.user)
class Match(Command):
    def run(self, args, conn):
        if conn.user.session.game:
            if conn.user.session.game.gtype == game.EXAMINED:
                conn.write(_("You can't challenge while you are examining a game.\n"))
            else:
                conn.write(_("You can't challenge while you are playing a game.\n"))
            return
        u = user.find.by_prefix_for_user(args[0], conn, online_only=True)
        if not u:
            return
        if u == conn.user:
            conn.write(_("You can't match yourself.\n"))
            return

        match.Challenge(conn.user, u, args[1])

# TODO: parameters?
@ics_command('rematch', '')
class Rematch(Command):
    def run(self, args, conn):
        # note that rematch uses history to determine the previous opp,
        # so unlike "say", it works after logging out and back in, and
        # ignores aborted games
        hist = conn.user.get_history()
        if not hist:
            conn.write(_('You have no previous opponent.\n'))
            return
        h = hist[-1]
        opp = online.find_exact(h['opp_name'])
        if not opp:
            conn.write(_('Your last opponent, %s, is not logged in.\n') % h['opp_name'])
            return
        variant_name = speed_variant.variant_abbrevs[h['flags'][1]]
        assert(h['flags'][2] in ['r', 'u'])
        match_str = '%d %d %s %s' % (h['time'], h['inc'], h['flags'][2],
            variant_name)
        match.Challenge(conn.user, opp, match_str)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

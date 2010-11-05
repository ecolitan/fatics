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

import time
from gettext import ngettext

import online
import game

from config import config

heartbeat_timeout = 5
def heartbeat():
    # idle timeout
    if config.idle_timeout:
        now = time.time()
        for u in online.online:
            if (now - u.session.last_command_time > config.idle_timeout and
                    not u.is_admin() and
                    not u.has_title('TD')):
                u.session.conn.idle_timeout(config.idle_timeout // 60)

    # ping all zipseal clients
    # I wonder if it would be better to spread out the pings in time,
    # rather than sending a large number of ping requests all at once.
    # However, this method is simple, and FICS timeseal 2 seems to do it
    # this way (pinging all capable clients every 10 seconds).
    for u in online.online:
        if u.session.use_zipseal:
            u.session.ping()

    # forfeit games on time
    for g in game.games.values():
        if g.gtype == game.PLAYED and g.clock.is_ticking:
            u = g.get_user_to_move()
            opp = g.get_opp(u)
            if opp.vars['autoflag']:
                g.clock.check_flag(g, g.get_user_side(u))

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

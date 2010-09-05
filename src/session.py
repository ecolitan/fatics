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
import copy

import var
import game
import timeseal
from game_list import GameList
from timer import timer

# user state that is per-session and not saved to persistent storage
class Session(object):
    def __init__(self, conn):
        self.conn = conn
        self.login_time = time.time()
        self.last_command_time = time.time()
        self.last_tell_user = None
        self.last_tell_ch = None
        self.last_opp = None
        self.use_timeseal = False
        self.ping_sent = None
        self.ping_time = []
        self.use_zipseal = False
        self.check_for_timeseal = True
        self.offers_sent = []
        self.offers_received = []
        self.games = GameList()
        self.ivars = var.varlist.get_default_ivars()
        self.lag = 0
        self.observed = set()
        self.closed = False

    def set_user(self, user):
        self.user = user
        self.conn.write(_('**** Starting FICS session as %s ****\n\n') % user.get_display_name())

    """returns a human-readable string"""
    def get_idle_time(self):
        assert(self.last_command_time is not None)
        return timer.hms_words(time.time() - self.last_command_time)

    """returns a human-readable string"""
    def get_online_time(self):
        assert(self.login_time is not None)
        return timer.hms_words(time.time() - self.login_time)

    def close(self):
        assert(not self.closed)
        self.closed = True
        for v in self.offers_sent[:]:
            if v.name not in ['match offer', 'pause request']:
                continue
            v.withdraw(notify=False)
            v.a.write(_('Withdrawing your match offer to %s.\n') % v.b.name)
            v.b.write(_('%s, who was challenging you, has departed.\n') % self.user.name)
        for v in self.offers_received[:]:
            if v.name not in ['match offer', 'pause request']:
                continue
            v.decline(notify=False)
            v.b.write(_('Declining the match offer from %s.\n') % v.a.name)
            v.a.write(_('%s, whom you were challenging, has departed.\n') % self.user.name)
        self.games.leave_all(self.user)
        del self.offers_received[:]
        del self.offers_sent[:]
        if self.games and self.games.current().gtype == game.PLAYED:
            self.conn.write('Your game will be lost because adjourning is not implemented.\n')

        # unobserve games
        for g in copy.copy(self.observed):
            g.unobserve(self.user)
        assert(not self.observed)

    def set_ivars_from_str(self, s):
        """Parse a %b string sent by Jin to set ivars before logging in."""
        for (i, val) in enumerate(s):
            self.ivars[var.ivar_number[i].name] = val
        self.conn.write("#Ivars set.\n")

    def set_ivar(self, v, val):
        if val is not None:
            self.ivars[v.name] = val
        else:
            if v.name in self.ivars:
                del self.ivars[v.name]

    def ping(self):
        # don't send another ping if one is already pending
        assert(self.use_timeseal or self.use_zipseal)
        if not self.ping_sent:
            self.ping_sent = time.time()
            self.conn.write(timeseal.PING)

    def pong(self, t):
        if not self.ping_sent:
            self.conn.write('protocol error: got reply without ping')
            self.conn.loseConnection('protocol error: got reply without ping')
        else:
            reply_time = time.time() - self.ping_sent
            self.ping_sent = None
            if len(self.ping_time) > 4:
                self.ping_time.pop(0)
            self.ping_time.append(reply_time)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

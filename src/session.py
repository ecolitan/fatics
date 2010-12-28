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
import time_format
import partner

from game_list import GameList

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
        self.ping_sent = []
        self.ping_time = []
        self.move_sent_timestamp = None
        self.use_zipseal = False
        self.check_for_timeseal = True
        self.offers_sent = []
        self.offers_received = []
        self.game = None
        self.ivars = var.varlist.get_default_ivars()
        self.lag = 0
        self.observed = GameList()
        self.closed = False
        self.seeks = []
        self.partner = None
        self.following = None

    def set_user(self, user):
        self.user = user
        self.conn.write(_('**** Starting FICS session as %s ****\n\n') % user.get_display_name())

    """returns a human-readable string"""
    def get_idle_time(self):
        assert(self.last_command_time is not None)
        return time_format.hms_words(time.time() - self.last_command_time)

    """returns a human-readable string"""
    def get_online_time(self):
        assert(self.login_time is not None)
        return time_format.hms_words(time.time() - self.login_time)

    def close(self):
        assert(not self.closed)
        self.closed = True
        # XXX this will not remove draw offers; game-related offers
        # should probably be saved when a game is adjourned
        for v in self.offers_sent[:]:
            assert(v.a == self.user)
            v.withdraw_logout()
        for v in self.offers_received[:]:
            assert(v.b == self.user)
            v.decline_logout()
        if self.partner:
            #self.conn.write(_('Removing partnership with %s.\n') %
            #    partner.name)
            self.partner.write_('Your partner, %s, has departed.\n',
                self.user.name)
            partner.end_partnership(self.partner, self.user)

        if self.game:
            self.game.leave(self.user)
            assert(self.game == None)
        del self.offers_received[:]
        del self.offers_sent[:]

        # unobserve games
        assert(self.user.session == self)
        for g in self.observed.copy():
            g.unobserve(self.user)
        assert(not self.observed)

        # remove seeks
        if self.seeks:
            for s in self.seeks[:]:
                s.remove()
            self.conn.write(_('Your seeks have been removed.\n'))
        assert(not self.seeks)

    def set_ivars_from_str(self, s):
        """Parse a %b string sent by Jin to set ivars before logging in."""
        for (i, val) in enumerate(s):
            self.ivars[var.ivar_number[i].name] = int(val)
        self.conn.write("#Ivars set.\n")

    def set_ivar(self, v, val):
        if val is not None:
            self.ivars[v.name] = val
        else:
            if v.name in self.ivars:
                del self.ivars[v.name]

    def ping(self, for_move=False):
        # don't send another ping if one is already pending
        assert(self.use_timeseal or self.use_zipseal)
        # Always send a ping with a move in a game being played.
        # Otherwise, send a ping if one is not alredy pending.
        if for_move or not self.ping_sent:
            if self.use_zipseal:
                self.conn.write(timeseal.ZIPSEAL_PING)
            else:
                self.conn.write(timeseal.TIMESEAL_1_PING)
            self.ping_sent.append((time.time(), for_move))

    def pong(self, t):
        assert(self.ping_sent)
        sent_time, for_move = self.ping_sent.pop(0)
        reply_time = time.time() - sent_time

        if len(self.ping_time) > 9:
            self.ping_time.pop(0)
        self.ping_time.append(reply_time)

        if for_move:
            self.move_sent_timestamp = t

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

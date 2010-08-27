import time
import copy

import var
from timer import timer
from game_list import GameList

# user state that is per-session and not saved to persistent storage
class Session(object):
    def __init__(self, conn):
        self.conn = conn
        self.login_time = time.time()
        self.last_command_time = time.time()
        self.last_tell_user = None
        self.last_tell_ch = None
        self.use_timeseal = False
        self.ping_sent = False
        self.ping_reply_time = None
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
        if self.games:
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

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

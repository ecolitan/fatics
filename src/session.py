import time
import copy

import var
from timer import timer

# user state that is per-session and not saved to persistent storage
class Session(object):
    def __init__(self, conn):
        self.conn = conn
        self.login_time = time.time()
        self.last_command_time = time.time()
        self.last_tell_user = None
        self.last_tell_ch = None
        self.use_timeseal = False
        self.use_zipseal = False
        self.check_for_timeseal = True
        self.offers_sent = []
        self.offers_received = []
        self.games = {}
        self.ivars = var.varlist.get_default_ivars()
        self.lag = 0
        self.observed = set()

    def set_user(self, user):
        self.user = user

    """returns a human-readable string"""
    def get_idle_time(self):
        assert(self.last_command_time is not None)
        return timer.hms_words(time.time() - self.last_command_time)

    """returns a human-readable string"""
    def get_online_time(self):
        assert(self.login_time is not None)
        return timer.hms_words(time.time() - self.login_time)
        
    def close(self):
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
        # python docs: "Using iteritems() while adding or deleting entries
        # in the dictionary may raise a RuntimeError or fail to iterate
        # over all entries."
        for (k, v) in copy.copy(self.games).iteritems():
            v.abort('%s aborted by disconnection' % self.user.name)
        del self.offers_received[:]
        del self.offers_sent[:]
        if len(self.games) > 0:
            self.conn.write('Your game will be lost because adjourning is not implemented.\n')

        # unobserve games
        for g in copy.copy(self.observed):
            g.unobserve(self.user)
        assert(not self.observed)

    def set_ivars_from_str(self, s):
        """Parse a %b string sent by Jin to set ivars before logging in."""
        for (i, val) in enumerate(s):
            self.ivars[var.ivar_number[i].name] = val
        self.conn.write(_("Ivars set.\n"))
    
    def set_ivar(self, v, val):
        if val is not None:
            self.ivars[v.name] = val
        else:
            if v.name in self.ivars:
                del self.ivars[v.name]

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

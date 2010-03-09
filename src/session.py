import time
import copy

import user
import db
from online import online

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
        self.pending_sent = {}
        self.pending_received = {}
        self.games = {}

    def set_user(self, user):
        self.user = user

    """returns a human-readable string"""
    def get_idle_time(self):
        assert(self.last_command_time != None)
        return timer.hms(time.time() - self.last_command_time)

    """returns a human-readable string"""
    def get_online_time(self):
        assert(self.login_time != None)
        return timer.hms(time.time() - self.login_time)
        
    def close(self):
        # python docs: "Using iteritems() while adding or deleting entries
        # in the dictionary may raise a RuntimeError or fail to iterate
        # over all entries."  So pass a flag to avoid deleting.
        for (k, v) in self.pending_sent.iteritems():
            v.withdraw(logout=True)
            v.player_b.user.write(_('%s, who was challenging you, has departed.\n') % k)
        for (k, v) in self.pending_received.iteritems():
            v.decline(logout=True)
            v.player_a.user.write(_('%s, whom you were challenging, has departed.\n') % k)
        for (k, v) in copy.copy(self.games).iteritems():
            v.abort('%s aborted by disconnection' % self.user.name)
        self.pending_received.clear()
        self.pending_sent.clear()
        if len(self.games) > 0:
            self.conn.write('Your game will be lost because adjourning is not implemented.\n')

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

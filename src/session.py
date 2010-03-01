import user
import db
import time
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

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

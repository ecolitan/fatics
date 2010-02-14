online = {}

import user
import db
import time

from timer import timer

# user state that is per-session and not saved to persistent storage
class Session: 
        def __init__(self, conn):
                self.conn = conn
                self.login_time = time.time()
	        self.last_command_time = time.time()
                self.last_tell_user = None
                self.use_timeseal = True
                self.check_for_timeseal = True

        def set_user(self, user):
                self.user = user
                online[user.name.lower()] = self

        def close(self):
                del online[user.name]

        """returns a human-readable string"""
        def get_idle_time(self):
                assert(self.last_command_time != None)
                return timer.hms(time.time() - self.last_command_time)

        """returns a human-readable string"""
        def get_online_time(self):
                assert(self.login_time != None)
                return timer.hms(time.time() - self.login_time)


# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

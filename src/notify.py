from db import *
from online import online

#"""A giant dict whose keys consist of every user who might potentially 
#cause a notification by logging in or out."""
#notify = {}

class Notify(object):
        """Send a message to all users notivied about the given user_id."""
        def users(self, user_id, msg):
                for dbu in db.user_get_notified(user_id):
                        u = online.find_exact(dbu['user_name'])
                        if u:
                                u.write(msg)
notify = Notify()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent

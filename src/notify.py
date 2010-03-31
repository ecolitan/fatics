from online import online

class Notify(object):
    """Send a message to all users notified about the given user."""
    def users(self, user, msg):
        name = user.name
        for u in online:
            if name in u.notifiers:
                u.write(msg)
notify = Notify()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

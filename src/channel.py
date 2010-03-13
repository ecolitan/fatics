import sys
import copy

from db import db
#from online import online

class ChannelError(Exception):
    pass

class Channel(object):
    def __init__(self, id, name, desc):
        assert(type(id) == type(1) or type(id) == type(1l))
        self.id = id
        self.name = name
        self.desc = desc
        self.online = []
        """for name in self.members:
                u = online.find_exact(name)
                if u:
                        self.online.append(u)"""

    def tell(self, msg, user):
        msg = '%s(%s): %s\n' % (user.get_display_name(), self.id, msg)
        for u in self.online:
            u.write(msg)
        return len(self.online)

    def log_on(self, user):
        self.online.append(user)

    def log_off(self, user):
        self.online.remove(user)

    def add(self, user):
        if user in self.online:
            user.write(_('[%s] is already on your channel list.\n') % self.id)
            return
        self.online.append(user)
        user.add_channel(self.id)
        user.write(_('[%s] added to your channel list.\n') % self.id)

    def remove(self, user):
        if  user not in self.online:
            user.write(_('[%s] is not on your channel list.\n') % self.id)
            return
        if user.is_online:
            self.online.remove(user)
        user.remove_channel(self.id)
        user.write(_('[%s] removed from your channel list.\n') % self.id)

    def get_display_name(self):
        if self.name != None:
            return '''%d "%s"''' % (self.id, self.name)
        else:
            return "%d" % self.id

    def get_online(self):
        return [u.get_display_name() for u in self.online]

class ChannelList(object):
    all = {}
    max = sys.maxint
    def __init__(self):
        for ch in db.channel_list():
            id = ch['channel_id']
            self.all[id] = Channel(id, ch['name'], ch['descr'])

    def __getitem__(self, key):
        assert(type(key) == type(1) or type(key) == type(1l))
        if key < 0 or key > self.max:
            raise KeyError
        try:
            return self.all[key]
        except KeyError:
            self.all[key] = self.make_ch(key)
            return self.all[key]

    def make_ch(self, key):
        name = None
        db.channel_new(key, name)
        return Channel(key, name, None)

    def get_default_guest_channels(self):
        return copy.copy([4, 53])
chlist = ChannelList()


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

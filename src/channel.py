from db import db

class ChannelError(Exception):
        pass

class Channel(object):
        def __init__(self, id, name, desc, members):
                self.id = id
                self.name = name
                self.desc = desc
                self.members = members

        def tell(self, msg):
                print "CHTELL %s %s" % (name, msg)

        def add(self, user):
                if user.name in self.members:
                        user.write(_('[%s] is already on your channel list.\n') % self.name)
                        return
                self.members.append(user)
                if not user.is_guest:
                        db.channel_add_user(self.id, user.id)
                user.write(_('[%s] added to your channel list.\n') % self.name)

class ChannelList(object):
        all = {}
        def __init__(self):
                for ch in db.channel_list():
                        self.all[ch['name']] = Channel(ch['channel_id'], ch['name'], ch['descr'], db.channel_get_members(ch['channel_id']))

        def __getitem__(self, key):
                try:
                        return self.all[key]
                except KeyError:
                        self.all[key] = self.make_ch(key)
                        return self.all[key]

        def make_ch(self, key):
                id = db.channel_new(key)
                return Channel(id, key, None, [])
chlist = ChannelList()


# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent

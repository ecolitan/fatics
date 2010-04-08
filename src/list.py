import trie
import channel
import admin
import user

from db import db, DuplicateKeyError, DeleteError

lists = trie.Trie()

"""A list as operated on by addlist, sublist, and showlist.  Subclasses
should implement add, sub, and show methods."""
class MyList(object):
    def __init__(self, name):
        self.name = name
        lists[name.lower()] = self

class ListError(Exception):
    def __init__(self, reason):
        self.reason = reason

class TitleList(MyList):
    def __init__(self, id, name, descr):
        MyList.__init__(self, name)
        self.id = id
        self.descr = descr

    def add(self, item, conn):
        if conn.user.admin_level < admin.level.admin:
            raise ListError(_("You don't have permission to do that.\n"))
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.is_guest:
                raise ListError(_("Only registered users may have titles.\n"))

            try:
                u.add_title(self.id)
            except DuplicateKeyError:
                raise ListError(_('%(uname)s is already on the %(lname)s list.\n') %
                    {'uname': u.name, 'lname': self.name })
            else:
                conn.write(_('%s added to the %s list.\n') % (u.name, self.name))

    def sub(self, item, conn):
        if conn.user.admin_level < admin.level.admin:
            raise ListError(_("You don't have permission to do that.\n"))
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.is_guest:
                raise ListError(_("Only registered users may have titles.\n"))
            try:
                u.remove_title(self.id)
            except DeleteError:
                raise ListError(_('%(uname)s is not on the %(lname)s list.\n') %
                    {'uname': u.name, 'lname': self.name })
            conn.write(_('%s removed from the %s list.\n') % (u.name, self.name))
    
    def show(self, conn):
        tlist = db.title_get_users(self.id)
        conn.write(ngettext('-- %s list: %d name --\n', '-- %s list: %d names --\n', len(tlist)) % (self.name,len(tlist)))
        conn.write('%s\n' % ' '.join(tlist))

class NotifyList(MyList):
    def add(self, item, conn):
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.name in conn.user.notifiers:
                raise ListError(_('%s is already on your notify list.\n')
                    % u.name)
            conn.user.add_notification(u)
            conn.write(_('%s added to your notify list.\n') % (u.name))

    def sub(self, item, conn):
        # would it be better to only search the notify list?
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.name not in conn.user.notifiers:
                raise ListError(_('%s is not on your notify list.\n') % u.name)
            conn.user.remove_notification(u)
            conn.write(_('%s removed from your notify list.\n') % (u.name))

    def show(self, conn):
        notlist = conn.user.notifiers
        conn.write(ngettext('-- notify list: %d name --\n', '-- notify list: %d names --\n', len(notlist)) % len(notlist))
        conn.write('%s\n' % ' '.join(notlist))

class ChannelList(MyList):
    def add(self, item, conn):
        try:
            val = int(item, 10)
        except ValueError:
            raise ListError(_('The channel must be a number.\n'))

        try:
            ch = channel.chlist[val]
        except KeyError:
            raise ListError(_('Invalid channel number.\n'))

        if ch.id == 0 and conn.user.admin_level < admin.level.admin:
            conn.write(_('Only admins can join channel 0.\n'))
        else:
            ch.add(conn.user)
            conn.user.write(_('[%d] added to your channel list.\n') % val)

    def sub(self, item, conn):
        try:
            val = int(item, 10)
        except ValueError:
            raise ListError(_('The channel must be a number.\n'))

        try:
            ch = channel.chlist[val]
        except KeyError:
            raise ListError(_('Invalid channel number.\n'))

        ch.remove(conn.user)
        conn.user.write(_('[%d] removed from your channel list.\n') % val)

    def show(self, conn):
        chlist = conn.user.channels
        conn.write(ngettext('-- channel list: %d channel --\n', '-- channel list: %d channels --\n', len(chlist)) % len(chlist))
        for ch in chlist:
            conn.write('%s ' % ch)
        conn.write('\n')

class CensorList(MyList):
    def add(self, item, conn):
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.name in conn.user.censor:
                raise ListError(_('%s is already on your censor list.\n') % u.name)
            conn.user.add_censor(u)
            conn.write(_('%s added to your censor list.\n') % (u.name))

    def sub(self, item, conn):
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.name not in conn.user.censor:
                raise ListError(_('%s is not on your censor list.\n') % u.name)
            conn.user.remove_censor(u)
            conn.write(_('%s removed from your censor list.\n') % (u.name))

    def show(self, conn):
        cenlist = conn.user.censor
        conn.write(ngettext('-- censor list: %d name --\n', '-- censor list: %d names --\n', len(cenlist)) % len(cenlist))
        conn.write('%s\n' % ' '.join(cenlist))

class NoplayList(MyList):
    def add(self, item, conn):
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.name in conn.user.noplay:
                raise ListError(_('%s is already on your noplay list.\n') % u.name)
            conn.user.add_noplay(u)
            conn.write(_('%s added to your noplay list.\n') % (u.name))

    def sub(self, item, conn):
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.name not in conn.user.noplay:
                raise ListError(_('%s is not on your noplay list.\n') % u.name)
            conn.user.remove_noplay(u)
            conn.write(_('%s removed from your noplay list.\n') % (u.name))

    def show(self, conn):
        noplist = conn.user.noplay
        conn.write(ngettext('-- noplay list: %d name --\n', '-- noplay list: %d names --\n', len(noplist)) % len(noplist))
        conn.write('%s\n' % ' '.join(noplist))

"""a list of lists"""
class ListList(object):
    def __init__(self):
        ChannelList("channel")
        NotifyList("notify")
        CensorList("censor")
        NoplayList("noplay")

        for title in db.title_get_all():
            TitleList(title['title_id'], title['title_name'], title['title_descr'])
ListList()

#  removedcom filter muzzle, cmuzzle, c1muzzle, c24muzzle, c46muzzle, c49muzzle, c50muzzle, c51muzzle,
# censor, gnotify, noplay, channel, follow, remote, idlenotify

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

import gettext
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

    def add(self, args, conn):
        if conn.user.admin_level < admin.level.admin:
            raise ListError(_("You don't have permission to do that."))
        u = user.find.by_name_or_prefix_for_user(args[1], conn)
        if u:
            if u.is_guest:
                raise ListError(_("Only registered users may have titles."))
            try:
                u.add_title(self.id)
            except DuplicateKeyError:
                raise ListError(_('%s is already in the %s list.') % (u.name, self.name))
            else:
                conn.write(_('%s added to the %s list.\n') % (u.name, self.name))

    def show(self, args, conn):
        conn.write('%s: ' % self.name)
        for user_name in db.title_get_users(self.id):
            conn.write('%s ' % user_name)
        conn.write('\n')

    def sub(self, args, conn):
        if conn.user.admin_level < admin.level.admin:
            raise ListError(_("You don't have permission to do that."))
        u = user.find.by_name_or_prefix_for_user(args[1], conn)
        if u:
            if u.is_guest:
                raise ListError(_("Only registered users may have titles."))
            try:
                u.remove_title(self.id)
            except DeleteError:
                raise ListError(_("%s is not in the %s list.") % (u.name, self.name))
            else:
                conn.write(_('%s removed from the %s list.\n') % (u.name, self.name))

class NotifyList(MyList):
    def add(self, args, conn):
        if conn.user.is_guest:
            raise ListError(_('Sorry, only registered users can use notification lists.'))
        u = user.find.by_name_or_prefix_for_user(args[1], conn)
        if u:
            if u.is_guest:
                raise ListError(_('Sorry, you can only add registered users to your notify list.'))
            try:
                conn.user.add_notification(u)
            except DuplicateKeyError:
                raise ListError(_('%s is already on your notify list.') % u.name)
            else:
                conn.write(_('%s added to your notify list.\n') % (u.name))


    def sub(self, args, conn):
        if conn.user.is_guest:
            raise ListError(_('Sorry, only registered users can use notification lists.'))
        u = user.find.by_name_or_prefix_for_user(args[1], conn)
        if u:
            if u.is_guest:
                raise ListError(_('Sorry, you can only remove registered users from your notify list.'))
            try:
                conn.user.remove_notification(u)
            except DeleteError:
                raise ListError(_('%s is not on your notify list.') % u.name)
            else:
                conn.write(_('%s removed from your notify list.\n') % (u.name))

    def show(self, args, conn):
        notlist = db.user_get_notifiers(conn.user.id)
        conn.write(ngettext('-- notify list: %d name --\n', '-- notify list: %d names --\n', len(notlist)) % len(notlist))
        for dbu in notlist:
            conn.write('%s ' % dbu['user_name'])
        conn.write('\n')

class ChannelList(MyList):
    def add(self, args, conn):
        try:
            val = int(args[1], 10)
            channel.chlist[val].add(conn.user)
        except ValueError:
            raise ListError(_('The channel must be a number.'))
        except KeyError:
            raise ListError(_('Invalid channel number.'))

    def sub(self, args, conn):
        try:
            val = int(args[1], 10)
            channel.chlist[val].remove(conn.user)
        except ValueError:
            raise ListError(_('The channel must be a number.'))
        except KeyError:
            raise ListError(_('Invalid channel number.'))

    def show(self, args, conn):
        chlist = conn.user.channels
        conn.write(ngettext('-- channel list: %d channel --\n', '-- channel list: %d channels --\n', len(chlist)) % len(chlist))
        for ch in chlist:
            conn.write('%s ' % ch)
        conn.write('\n')

"""a list of lists"""
class ListList(object):
    def __init__(self):
        ChannelList("channel")
        NotifyList("notify")

        for title in db.title_get_all():
            TitleList(title['title_id'], title['title_name'], title['title_descr'])

ListList()

#  removedcom filter muzzle, cmuzzle, c1muzzle, c24muzzle, c46muzzle, c49muzzle, c50muzzle, c51muzzle,
# censor, gnotify, noplay, channel, follow, remote, idlenotify


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

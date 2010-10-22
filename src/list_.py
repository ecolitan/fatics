# Copyright (C) 2010  Wil Mahan <wmahan+fatics@gmail.com>
#
# This file is part of FatICS.
#
# FatICS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FatICS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with FatICS.  If not, see <http://www.gnu.org/licenses/>.
#

import trie
import channel
import user

from db import db, DuplicateKeyError, DeleteError

""" The list design is intentionally kept simple, at the cost of
some repeated code, for example in the messages displayed to users.
Trying to factor out the common code only created a bigger mess.
The lists of original FICS were implemented a bit more concisely, but
it made some English-specific assumptions I don't want to
repeat (e.g. that system-wide lists use the same messages as personal
lists, with "your list" replaced by "the list").  Also original FICS
used a linear search to find entries, so my implementation should
be more efficient for large lists. """

class ListError(Exception):
    def __init__(self, reason):
        self.reason = reason

class MyList(object):
    """ A list as operated on by addlist, sublist, and showlist.  Subclasses
    should implement add, sub, and show methods. """
    def __init__(self, name):
        self.name = name
        lists[name.lower()] = self

    def _require_admin(self, user):
        if not user.is_admin():
            raise ListError(_("You don't have permission to do that.\n"))

class TitleList(MyList):
    def __init__(self, id, name, descr, public):
        MyList.__init__(self, name)
        self.id = id
        self.descr = descr
        self.public = public

    def add(self, item, conn):
        self._require_admin(conn.user)
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.is_guest:
                raise ListError(_("Only registered users may have titles.\n"))

            try:
                u.add_title(self.id)
            except DuplicateKeyError:
                raise ListError(_('%(uname)s is already on the %(lname)s list.\n') %
                    {'uname': u.name, 'lname': self.name })
            conn.write(_('%s added to the %s list.\n') %
                (u.name, self.name))
            if u.is_online:
                u.write_('%(aname)s has added you to the %(lname)s list.\n',
                    {'aname': conn.user.name, 'lname': self.name})

    def sub(self, item, conn):
        self._require_admin(conn.user)
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
            if u.is_online:
                u.write_('%(aname)s has removed you from the %(lname)s list.\n',
                    {'aname': conn.user.name, 'lname': self.name})

    def show(self, conn):
        if not self.public:
            self._require_admin(conn.user)
        tlist = db.title_get_users(self.id)
        conn.write(ngettext('-- %s list: %d name --\n',
            '-- %s list: %d names --\n', len(tlist)) % (self.name,len(tlist)))
        conn.write('%s\n' % ' '.join(tlist))

class NotifyList(MyList):
    def add(self, item, conn):
        if conn.user.is_guest:
            raise ListError(_('Only registered players can have notify lists.\n'))
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u == conn.user:
                raise ListError(_('You cannot notify yourself.\n'))
            if u.is_guest:
                raise ListError(_('You cannot add an unregistered user to your notify list.\n'))
            if u.name in conn.user.notifiers:
                raise ListError(_('%s is already on your notify list.\n')
                    % u.name)
            conn.user.add_notification(u)
            conn.write(_('%s added to your notify list.\n') % u.name)
            if u.is_online:
                u.write_('You have been added to the notify list of %s.\n',
                    (conn.user.name,))

    def sub(self, item, conn):
        if conn.user.is_guest:
            raise ListError(_('Only registered players can have notify lists.\n'))
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.name not in conn.user.notifiers:
                raise ListError(_('%s is not on your notify list.\n') % u.name)
            conn.user.remove_notification(u)
            conn.write(_('%s removed from your notify list.\n') % u.name)
            # We deliberately don't notify the user, to avoid
            # embarrassment or hurt feelings.

    def show(self, conn):
        if conn.user.is_guest:
            raise ListError(_('Only registered players can have notify lists.\n'))
        notlist = conn.user.notifiers
        conn.write(ngettext('-- notify list: %d name --\n',
            '-- notify list: %d names --\n', len(notlist)) % len(notlist))
        conn.write('%s\n' % ' '.join(notlist))

class IdlenotifyList(MyList):
    def add(self, item, conn):
        u = user.find.by_prefix_for_user(item, conn, online_only=True)
        if u:
            if u == conn.user:
                raise ListError(_('You cannot idlenotify yourself.\n'))
            if conn.user in u.idlenotified:
                raise ListError(_('%s is already on your idlenotify list.\n')
                    % u.name)
            conn.user.add_idlenotification(u)
            conn.write(_('%s added to your idlenotify list.\n') % u.name)

    def sub(self, item, conn):
        u = user.find.by_prefix_for_user(item, conn, online_only=True)
        if u:
            if conn.user not in u.idlenotified:
                raise ListError(_('%s is not on your idlenotify list.\n') % u.name)
            conn.user.remove_idlenotification(u)
            conn.write(_('%s removed from your idlenotify list.\n') % u.name)

    def show(self, conn):
        notlist = conn.user.idlenotifiers
        conn.write(ngettext('-- idlenotify list: %d name --\n',
            '-- idlenotify list: %d names --\n', len(notlist)) % len(notlist))
        conn.write('%s\n' % ' '.join([u.name for u in notlist]))

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

        if ch.id == 0 and not conn.user.is_admin():
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
        conn.write(ngettext('-- channel list: %d channel --\n',
            '-- channel list: %d channels --\n', len(chlist)) % len(chlist))
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
            conn.write(_('%s added to your censor list.\n') % u.name)

    def sub(self, item, conn):
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.name not in conn.user.censor:
                raise ListError(_('%s is not on your censor list.\n') % u.name)
            conn.user.remove_censor(u)
            conn.write(_('%s removed from your censor list.\n') % (u.name))

    def show(self, conn):
        cenlist = conn.user.censor
        conn.write(ngettext('-- censor list: %d name --\n',
            '-- censor list: %d names --\n', len(cenlist)) % len(cenlist))
        conn.write('%s\n' % ' '.join(cenlist))

class NoplayList(MyList):
    def add(self, item, conn):
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.name in conn.user.noplay:
                raise ListError(_('%s is already on your noplay list.\n') % u.name)
            conn.user.add_noplay(u)
            conn.write(_('%s added to your noplay list.\n') % u.name)

    def sub(self, item, conn):
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.name not in conn.user.noplay:
                raise ListError(_('%s is not on your noplay list.\n') % u.name)
            conn.user.remove_noplay(u)
            conn.write(_('%s removed from your noplay list.\n') % (u.name))

    def show(self, conn):
        noplist = conn.user.noplay
        conn.write(ngettext('-- noplay list: %d name --\n',
            '-- noplay list: %d names --\n', len(noplist)) % len(noplist))
        conn.write('%s\n' % ' '.join(noplist))

class BanList(MyList):
    def add(self, item, conn):
        self._require_admin(conn.user)
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.is_guest:
                raise ListError(A_('Only registered players can be banned.\n'))
            if u.is_admin():
                raise ListError(A_('Admins cannot be banned.\n'))
            if u.is_banned:
                raise ListError(_('%s is already on the ban list.\n') % u.name)
            db.user_set_banned(u.id, 1)
            u.is_banned = True
            db.add_comment(conn.user.id, u.id, 'Banned.')
            conn.write(_('%s added to the ban list.\n') % u.name)
            if u.is_online:
                conn.write('Note: %s is online.\n' % u.name)

    def sub(self, item, conn):
        self._require_admin(conn.user)
        u = user.find.by_prefix_for_user(item, conn)
        if u:
            if u.is_guest:
                raise ListError(A_('Only registered players can be banned.\n'))
            if not u.is_banned:
                raise ListError(_('%s is not on the ban list.\n') % u.name)
            db.user_set_banned(u.id, 0)
            u.is_banned = False
            conn.write(_('%s removed from the ban list.\n') % (u.name))

    def show(self, conn):
        self._require_admin(conn.user)
        banlist = db.get_banned_user_names()
        conn.write(ngettext('-- ban list: %d name --\n',
            '-- ban list: %d names --\n', len(banlist)) % len(banlist))
        conn.write('%s\n' % ' '.join(banlist))

""" initialize lists """
def _init_lists():
    ChannelList("channel")
    NotifyList("notify")
    IdlenotifyList("idlenotify")
    CensorList("censor")
    NoplayList("noplay")
    BanList("ban")

    for title in db.title_get_all():
        TitleList(title['title_id'], title['title_name'], title['title_descr'], title['title_public'])
lists = trie.Trie()
_init_lists()

#  removedcom filter muzzle, cmuzzle, c1muzzle, c24muzzle, c46muzzle, c49muzzle, c50muzzle, c51muzzle,
# censor, gnotify, noplay, channel, follow, remote, idlenotify

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

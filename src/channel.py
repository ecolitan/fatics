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

import sys
import copy

import list_
import admin

from db import db, DeleteError
from config import config

USER_CHANNEL_START = 1024

class ChannelError(Exception):
    pass

class Channel(object):
    def __init__(self, id, name, desc):
        assert(type(id) == type(1) or type(id) == type(1L))
        self.id = id
        self.name = name
        self.desc = desc
        self.online = []

    def tell(self, msg, user):
        msg = '%s(%d): %s\n' % (user.get_display_name(), self.id, msg)
        is_guest = user.is_guest
        count = 0
        name = user.name
        for u in self.online:
            if is_guest and not u.vars['ctell']:
                continue
            if not u.hears_channels():
                continue
            if not name in u.censor:
                u.write(msg)
                count += 1
        return count

    def qtell(self, msg):
        for u in self.online:
            if not u.hears_channels():
                continue
            u.write(msg)

    def log_on(self, user):
        self.online.append(user)

    def log_off(self, user):
        self.online.remove(user)

    def is_user_owned(self):
        return self.id >= USER_CHANNEL_START

    def user_is_member(self, user):
        if user.is_online:
            return user in self.online
        else:
            assert(not user.is_guest)
            return db.user_in_channel(user.id, self.id)

    def add(self, user):
        if user in self.online:
            raise list_.ListError(_('[%s] is already on your channel list.\n') %
                self.id)

        # channels above 1024 may be claimed by a user simply
        # by joining
        if self.is_user_owned():
            if user.is_guest:
                raise list_.ListError(_('Only registered players can join channels %d and above.\n') % USER_CHANNEL_START)
            if db.channel_user_count(self.id) == 0:
                if (db.user_channels_owned(user.id) >= config.max_channels_owned
                        and not user.has_title('TD')):
                    raise list_.ListError(_('You cannot own more than %d channels.\n') % config.max_channels_owned)
                db.channel_add_owner(self.id, user.id)
                user.write(_('You are now the owner of channel %d.\n') % self.id)

        self.online.append(user)
        user.add_channel(self.id)

    def remove(self, user):
        if user not in self.online:
            raise list_.ListError(_('[%s] is not on your channel list.\n') %
                self.id)

        assert(user.is_online)
        self.online.remove(user)
        user.remove_channel(self.id)

        if not user.is_guest and self.is_user_owned():
            try:
                db.channel_del_owner(self.id, user.id)
            except DeleteError:
                # user was not an owner
                pass
            else:
                user.write(_('You are no longer an owner of channel %d.\n') % self.id)
                # TODO? what if channel no longer has an owner?

    def kick(self, u, owner):
        if not self.user_is_member(u):
            owner.write(_("%(name)s is not in channel %(chid)d.\n") % {
                'name': u.name, 'chid': self.id
                })
            return
        if not owner.is_admin():
            if not db.channel_is_owner(self.id, owner.id):
                owner.write(_("You don't have permission to do that.\n"))
                return
            if db.channel_is_owner(self.id, u.id):
                owner.write(_("You cannot kick out a channel owner.\n"))
                return
            if u.is_admin():
                owner.write(_("You cannot kick out an admin.\n"))
                return
        else:
            if not admin.checker.check_user_operation(owner, u):
                owner.write(A_('You need a higher adminlevel to do that.\n'))
                return
            if db.channel_is_owner(self.id, u.id):
                # remove kicked user as owner of the channel, too
                db.channel_del_owner(self.id, u.id)

        u.remove_channel(self.id)
        if u.is_online:
            self.online.remove(u)
            u.write_('*** You have been kicked out of channel %(chid)d by %(owner)s. ***\n' %
                {'owner': owner.name, 'chid': self.id})

        # not translated, at least for now
        self.tell('*** Kicked out %s. ***\n' % u.name, owner)


    def get_display_name(self):
        if self.name is not None:
            return '''%d "%s"''' % (self.id, self.name)
        else:
            return "%d" % self.id

    def get_online(self):
        return [(u.get_display_name() if u.hears_channels() else
                '{%s}' % u.get_display_name())
            for u in self.online]

class ChannelList(object):
    all = {}
    max = sys.maxint
    def __init__(self):
        for ch in db.channel_list():
            id = ch['channel_id']
            self.all[id] = Channel(id, ch['name'], ch['descr'])

    def __getitem__(self, key):
        assert(type(key) == type(1) or type(key) == type(1L))
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

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
from datetime import datetime

import list_
import admin

from db import db, DeleteError
from config import config

USER_CHANNEL_START = 1024

class ChannelError(Exception):
    pass

class Channel(object):
    def __init__(self, params):
        self.id = params['channel_id']
        assert(type(self.id) == type(1) or type(self.id) == type(1L))
        self.name = params['name']
        self.desc = params['descr']
        if params['topic'] is None:
            self.topic = None
        else:
            self.topic = params['topic']
            self.topic_who_name = params['topic_who_name']
            self.topic_when = params['topic_when']
        self.online = []

    def tell(self, msg, user):
        #if user.is_chmuzzled:
        #    user.write(_('You are muzzled in all channels.\n'))
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
        if self.topic:
            if user.last_logout is None or self.topic_when > user.last_logout:
                self.show_topic(user)

    def show_topic(self, user):
        if self.topic:
            user.write_('TOPIC(%d): *** %s (%s at %s) ***\n',
                (self.id, self.topic, self.topic_who_name,
                user.format_datetime(self.topic_when)))
        else:
            user.write_('There is no topic for channel %d.\n', (self.id,))

    def check_owner(self, user):
        """ Check whether a user is an owner of the channel allowed to
        perform operations on it, and if not, send an error message. """
        if not user.is_admin():
            if not db.channel_is_owner(self.id, user.id):
                user.write(_("You don't have permission to do that.\n"))
                return False

        if not self.has_member(user):
            user.write(_("You are not in channel %d.\n") % (self.id,))
            return False

        if not user.hears_channels():
            user.write(_('You are not listening to channels.\n'))
            return False

        return True

    def set_topic(self, topic, owner):
        if not self.check_owner(owner):
            return

        if topic in ['-', '.']:
            # clear the topic
            self.topic = None
            db.channel_del_topic(self.id)
            for u in self.online:
                if u.hears_channels():
                    u.write_('%s(%d): *** Cleared topic. ***\n',
                        (owner.get_display_name(), self.id))
        else:
            # set a new topic
            self.topic = topic
            self.topic_who_name = owner.name
            self.topic_when = datetime.utcnow()
            db.channel_set_topic({'channel_id': self.id,
                'topic': topic, 'topic_who': owner.id,
                'topic_when': self.topic_when})
            for u in self.online:
                if u.hears_channels():
                    self.show_topic(u)

    def log_off(self, user):
        self.online.remove(user)

    def is_user_owned(self):
        return self.id >= USER_CHANNEL_START

    def has_member(self, user):
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
        if self.topic:
            self.show_topic(user)

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
        if not self.check_owner(owner):
            return

        if not self.has_member(u):
            owner.write(_("%(name)s is not in channel %(chid)d.\n") % {
                'name': u.name, 'chid': self.id
                })
            return

        if not owner.is_admin():
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

        for p in self.online:
            if p.hears_channels():
                p.write_('%s(%d): *** Kicked out %s. ***\n',
                    (owner.get_display_name(), self.id, u.name))

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
            self.all[id] = Channel(ch)

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
        return Channel({'channel_id': key, 'name': None, 'descr': None,
            'topic': None})

    def get_default_channels(self):
        return [1][:]

    def get_default_guest_channels(self):
        return [4, 53][:]
chlist = ChannelList()


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

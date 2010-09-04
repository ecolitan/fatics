# -*- coding: utf-8 -*-
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

import re

import user
from command import *
from db import db

# maximum line length is 1024, but leave some room for the date and
# user names
MAX_LEN = 950

class DisplayMessage(object):
    def _display_msg(self, msg, u):
        if msg['forwarder_name']:
            u.write_('%s forwarded: %s at %s: %s\n', msg['forwarder_name'], msg['sender_name'], msg['when_sent'], msg['txt'])
        else:
            u.write_('%s at %s: %s\n', msg['sender_name'], msg['when_sent'], msg['txt'])

@ics_command('clearmessages', 'n')
class Clearmessages(Command):
    range_re = re.compile('(\d+)-(\d+)')
    @requires_registration
    def run(self, args, conn):
        if args[0] is None:
            conn.write(_('Use "clearmessages *" to clear all your messages.\n'))
            return

        if args[0] == '*':
            count = conn.user.clear_messages_all()
        elif type(args[0]) == type(1):
            i = int(args[0])
            count = conn.user.clear_messages_range(i, i)
        else:
            m = self.range_re.match(args[0])
            if m:
                (start, end) = (int(m.group(1)), int(m.group(2)))
                # sanity checks
                if start < 1 or start > end or end > 9999:
                    conn.write(_('Invalid message range.\n'))
                    return
                count = conn.user.clear_messages_range(start, end)
                if count is None:
                    conn.write(_('You have no messages in that range.\n'))
                    return
            else:
                sender = user.find.by_prefix_for_user(args[0], conn)
                if not sender:
                    return
                count = conn.user.clear_messages_from(sender)

        conn.write(ngettext('Cleared %d message.\n', 'Cleared %d messages.\n', count) % count)

@ics_command('fmessage', 'wd')
class Fmessage(Command):
    @requires_registration
    def run(self, args, conn):
        pass


@ics_command('messages', 'nT')
class Messages(Command, DisplayMessage):
    range_re = re.compile('(\d+)-(\d+)')
    @requires_registration
    def run(self, args, conn):
        if args[0] is None:
            # display all messages
            msgs = conn.user.get_messages_all()
            if not msgs:
                conn.write(_('You have no messages.\n'))
            else:
                conn.write(_('Messages:\n'))
                for msg in msgs:
                    conn.write(_('%d. ') % (msg['num']))
                    self._display_msg(msg, conn.user)
        elif args[1] is None:
            # display some messages
            if type(args[0]) == type(1):
                i = int(args[0])
                msgs = conn.user.get_messages_range(i, i)
            else:
                m = self.range_re.match(args[0])
                if m:
                    (start, end) = (int(m.group(1)), int(m.group(2)))
                    # sanity checks
                    if start < 1 or start > end or end > 9999:
                        conn.write(_('Invalid message range.\n'))
                        return
                    msgs = conn.user.get_messages_range(start, end)
                else:
                    u2 = user.find.by_prefix_for_user(args[0], conn)
                    if not u2:
                        return
                    msgs = u2.get_messages_from(conn.user)
                    if not msgs:
                        conn.write(_('You have no messages to %s.\n') % u2.name)
                    else:
                        conn.write(_('Messages to %s:\n') % u2.name)
                        for msg in msgs:
                            self._display_msg(msg, conn.user)
                    conn.write('\n')

                    msgs = conn.user.get_messages_from(u2)
                    if not msgs:
                        conn.write(_('You have no messages from %s.\n') % u2.name)
                    else:
                        conn.write(_('Messages from %s:\n') % u2.name)
                        for msg in msgs:
                            self._display_msg(msg, conn.user)
            for msg in msgs:
                conn.write(_('%d. ') % (msg['num']))
                self._display_msg(msg, conn.user)
        else:
            # send a message
            to = user.find.by_prefix_for_user(args[0], conn)
            if to:
                if to.is_guest:
                    conn.write(_('Only registered players can have messages.\n'))
                    return
                message_id = conn.user.send_message(to, args[1])
                msg = db.get_message_id(message_id)
                conn.write(_('The following message was sent to %s:\n') %
                    to.name)
                self._display_msg(msg, conn.user)
                if to.is_online:
                    to.write_('The following message was received:\n')
                    self._display_msg(msg, to)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

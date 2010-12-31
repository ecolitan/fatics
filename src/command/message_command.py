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
import email
from db import db

from command import Command, ics_command, requires_registration
# maximum line length is 1024, but leave some room for the date and
# user names
#MAX_LEN = 950

class FormatMessage(object):
    def _format_msg(self, msg, u):
        if msg['forwarder_name']:
            txt = u.translate('%s forwarded: %s at %s: %s\n',
                (msg['forwarder_name'], msg['sender_name'],
                u.format_datetime(msg['when_sent']), msg['txt']))
        else:
            txt = u.translate('%s at %s: %s\n',
                (msg['sender_name'], u.format_datetime(msg['when_sent']),
                msg['txt']))
        return txt

    def _write_msg(self, msg, u):
        u.write(self._format_msg(msg, u))

@ics_command('clearmessages', 'n')
class Clearmessages(Command):
    range_re = re.compile('(\d+)-(\d+)')
    @requires_registration
    def run(self, args, conn):
        if args[0] is None:
            conn.write(_('Use "clearmessages *" to clear all your messages.\n'))
            return

        if args[0] == '*':
            count = db.clear_messages_all(conn.user.id)
        elif type(args[0]) == type(1):
            i = int(args[0])
            count = db.clear_messages_range(conn.user.id, i, i)
            if count == 0:
                conn.write(_('There is no such message.\n'))
                return
        else:
            m = self.range_re.match(args[0])
            if m:
                (start, end) = (int(m.group(1)), int(m.group(2)))
                # sanity checks
                if start < 1 or start > end or end > 9999:
                    conn.write(_('Invalid message range.\n'))
                    return
                count = db.clear_messages_range(conn.user.id, start, end)
            else:
                sender = user.find_by_prefix_for_user(args[0], conn)
                if not sender:
                    return
                count = db.clear_messages_from_to(sender.id, conn.user.id)

        conn.write(ngettext('Cleared %d message.\n',
            'Cleared %d messages.\n', count) % count)

@ics_command('fmessage', 'wd')
class Fmessage(Command, FormatMessage):
    @requires_registration
    def run(self, args, conn):
        if conn.user.is_muted:
            conn.write(_('You are muted.\n'))
            return
        u2 = user.find_by_prefix_for_user(args[0], conn)
        if u2:
            if conn.user.name in u2.censor and not conn.user.is_admin:
                conn.write(_('%s is censoring you.\n') % u2.name)
                return
            msgs = db.get_messages_range(conn.user.id, args[1], args[1])
            if msgs:
                msg = msgs[0]
                message_id = msg['message_id']
                msg['forwarder_name'] = conn.user.name
                db.forward_message(conn.user.id, u2.id, message_id)
                msg_str_u2 = self._format_msg(msg, u2) # localized for receiver

                if u2.vars['mailmess']:
                    email.send_mail(conn.user, u2, msg_str_u2)
                    conn.write(_('The following message was forwarded and emailed to %s:\n') % u2.name)
                else:
                    conn.write(_('The following message was forwarded to %s:\n') % u2.name)
                if u2.is_online:
                    u2.write_('The following message was received:\n')
                    u2.write(msg_str_u2)
                self._write_msg(msg, conn.user)
            else:
                conn.write(_('There is no such message.\n'))

@ics_command('messages', 'nT')
class Messages(Command, FormatMessage):
    range_re = re.compile('(\d+)-(\d+)')
    @requires_registration
    def run(self, args, conn):
        if args[0] is None:
            # display all messages
            msgs = db.get_messages_all(conn.user.id)
            if not msgs:
                conn.write(_('You have no messages.\n'))
            else:
                conn.write(_('Messages:\n'))
                for msg in msgs:
                    conn.write(_('%d. ') % (msg['num']))
                    self._write_msg(msg, conn.user)
                db.set_messages_read_all(conn.user.id)
        elif args[0] == 'u':
            if args[1] is not None:
                raise BadCommandError
            msgs = db.get_messages_unread(conn.user.id)
            if not msgs:
                conn.write(_('You have no unread messages.\n'))
            else:
                conn.write(_('Unread messages:\n'))
                for msg in msgs:
                    conn.write(_('%d. ') % (msg['num']))
                    self._write_msg(msg, conn.user)
                db.set_messages_read_all(conn.user.id)
        elif args[1] is None:
            # display some messages
            if type(args[0]) == type(1):
                i = int(args[0])
                msgs = db.get_messages_range(conn.user.id, i, i)
                if not msgs:
                    conn.write(_('There is no such message.\n'))
                    return
            else:
                m = self.range_re.match(args[0])
                if m:
                    (start, end) = (int(m.group(1)), int(m.group(2)))
                    # sanity checks
                    if start < 1 or start > end or end > 9999:
                        conn.write(_('Invalid message range.\n'))
                        return
                    msgs = db.get_messages_range(conn.user.id, start, end)
                else:
                    u2 = user.find_by_prefix_for_user(args[0], conn)
                    if not u2:
                        return
                    msgs = db.get_messages_from_to(conn.user.id, u2.id)
                    if not msgs:
                        conn.write(_('You have no messages to %s.\n') % u2.name)
                    else:
                        conn.write(_('Messages to %s:\n') % u2.name)
                        for msg in msgs:
                            self._write_msg(msg, conn.user)
                    conn.write('\n')

                    msgs = db.get_messages_from_to(u2.id, conn.user.id)
                    if not msgs:
                        conn.write(_('You have no messages from %s.\n') % u2.name)
                        return
                    else:
                        conn.write(_('Messages from %s:\n') % u2.name)

            for msg in msgs:
                conn.write(_('%d. ') % (msg['num']))
                self._write_msg(msg, conn.user)
                if msg['unread']:
                    db.set_message_read(msg['message_id'])
        else:
            """ Send a message.  Note that the message may be localized
            differently for the sender and receiver. """
            to = user.find_by_prefix_for_user(args[0], conn)
            if to:
                if conn.user.is_muted:
                    conn.write(_('You are muted.\n'))
                    return
                if to.is_guest:
                    conn.write(_('Only registered players can have messages.\n'))
                    return
                if conn.user.name in to.censor and not conn.user.is_admin():
                    conn.write(_('%s is censoring you.\n') % to.name)
                    return
                message_id = db.send_message(conn.user.id, to.id, args[1])
                msg = db.get_message(message_id)
                msg_str_to = self._format_msg(msg, to) # localized for receiver

                if to.vars['mailmess']:
                    email.send_mail(conn.user, to, msg_str_to)
                    conn.write(_('The following message was sent and emailed to %s:\n') %
                        to.name)
                else:
                    conn.write(_('The following message was sent to %s:\n') %
                        to.name)
                self._write_msg(msg, conn.user)

                if to.is_online:
                    to.write_('The following message was received:\n')
                    to.write(msg_str_to)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

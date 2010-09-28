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

from command import Command, ics_command

import online
import admin
import user

from command_parser import BadCommandError

@ics_command('summon', 'w')
class Summon(Command):
    def run(self, args, conn):
        u = user.find.by_prefix_for_user(args[0], conn, online_only=True)
        if not u:
            return
        if u == conn.user:
            conn.write(_("You can't summon yourself.\n"))
        if conn.user.admin_level <= admin.level.user:
            if conn.user.name in u.censor:
                conn.write(_("%s is censoring you.\n") % u.name)
                return
            if conn.user.name not in u.notifiers:
                conn.write(_('You cannot summon a player who doesn\'t have you on his or her notify list.\n'))
                return
        u.write('\a\n')
        u.write_('%s needs to speak to you.  To contact him or her type "tell %s hello".\n', ((conn.user.name, conn.user.name)))
        conn.write(_('Summoning sent to "%s".\n') % u.name)
        conn.user.add_idlenotification(u)

@ics_command('znotify', 'o')
class Znotify(Command):
    def run(self, args, conn):
        if args[0] is not None:
            if args[0] != 'n':
                raise BadCommandError()
            show_idle = True
        else:
            show_idle = False
        notifiers = [name for name in conn.user.notifiers
            if online.online.is_online(name)]
        if len(notifiers) == 0:
            conn.write(_('No one from your notify list is logged on.\n'))
        else:
            conn.write(_('Present company on your notify list:\n   %s\n') %
                ' '.join(notifiers))

        name = conn.user.name
        notified = [u.name for u in online.online if name in u.notifiers]
        if len(notified) == 0:
            conn.write(_('No one logged in has you on their notify list.\n'))
        else:
            conn.write(_('The following players have you on their notify list:\n   %s\n') %
                ' '.join(notified))

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

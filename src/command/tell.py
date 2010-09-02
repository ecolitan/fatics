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

from command import *

class TellCommand(Command):
    def _do_tell(self, args, conn):
        u = None
        ch = None
        if args[0] == '.':
            u = conn.session.last_tell_user
            if not u:
                conn.write(_("No previous tell.\n"))
            elif not u.is_online:
                # try to find the user if he or she has logged off
                # and since reconnected
                name = u.name
                u = online.find_exact(name)
                if not u:
                    conn.write(_('%s is no longer online.\n') % name)
        elif args[0] == ',':
            ch = conn.session.last_tell_ch
            if not ch:
                conn.write(_('No previous channel.\n'))
        else:
            if type(args[0]) != str:
                try:
                    ch = channel.chlist[args[0]]
                except KeyError:
                    conn.write(_('Invalid channel number.\n'))
                else:
                    if conn.user not in ch.online and (
                            'TD' not in conn.user.get_titles()):
                        conn.user.write(_('''(Not sent because you are not in channel %s.)\n''') % ch.id)
                        ch = None
            else:
                u = user.find.by_prefix_for_user(args[0], conn, online_only=True)

        if ch:
            count = ch.tell(args[1], conn.user)
            conn.write(ngettext('(told %d player in channel %d)\n', '(told %d players in channel %d)\n', count) % (count, ch.id))
        elif u:
            if conn.user.name in u.censor and conn.user.admin_level <= \
                    admin.level.user:
                conn.write(_("%s is censoring you.\n") % u.name)
            else:
                u.write('\n' + _("%s tells you: ") % conn.user.get_display_name() + args[1] + '\n')
                conn.write(_("(told %s)") % u.name + '\n')

        return (u, ch)

@ics_command('tell', 'nS', admin.Level.user)
class Tell_(TellCommand):
    def run(self, args, conn):
        (u, ch) = self._do_tell(args, conn)
        if u is not None:
            conn.session.last_tell_user = u
        else:
            conn.session.last_tell_ch = ch

@ics_command('xtell', 'nS', admin.Level.user)
class Xtell(TellCommand):
    def run(self, args, conn):
        self._do_tell(args, conn)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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

from command import ics_command, Command, requires_registration

import admin
import channel
import user

@ics_command('inchannel', 'n', admin.Level.user)
class Inchannel(Command):
    def run(self, args, conn):
        if args[0] is not None:
            if type(args[0]) != str:
                try:
                    ch = channel.chlist[args[0]]
                except KeyError:
                    conn.write(_('Invalid channel number.\n'))
                else:
                    on = ch.get_online()
                    if len(on) > 0:
                        conn.write("%s: %s\n" % (ch.get_display_name(), ' '.join(on)))
                    count = len(on)
                    conn.write(ngettext('There is %d player in channel %d.\n', 'There are %d players in channel %d.\n', count) % (count, args[0]))
            else:
                conn.write("INCHANNEL USER\n")
        else:
            for ch in channel.chlist.all.values():
                on = ch.get_online()
                if len(on) > 0:
                    conn.write("%s: %s\n" % (ch.get_display_name(), ' '.join(on)))

@ics_command('chkick', 'dw', admin.Level.user)
class Chkick(Command):
    """ Kick a user from a channel. """
    @requires_registration
    def run(self, args, conn):
        (chid, name) = args
        u = user.find.by_prefix_for_user(name, conn)
        if not u:
            return
        try:
            ch = channel.chlist[chid]
        except KeyError:
            conn.write(_('Invalid channel number.\n'))
            return
        ch.kick(u, conn.user)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

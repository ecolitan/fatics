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

@ics_command('shout', 'S', admin.Level.user)
class Shout(Command):
    @requires_registration
    def run(self, args, conn):
        if not conn.user.vars['shout'] or conn.user.in_silence():
            conn.write(_("(Did not shout because you are not listening to shouts)\n"))
        else:
            count = 0
            name = conn.user.name
            dname = conn.user.get_display_name()
            for u in online.online:
                if u.vars['shout'] and not u.in_silence():
                    if name not in u.censor:
                        u.write(_("%s shouts: %s\n") % (dname, args[0]))
                        count += 1
            conn.write(ngettext("(shouted to %d player)\n", "(shouted to %d players)\n", count) % count)

@ics_command('it', 'S', admin.Level.user)
class It(Command):
    @requires_registration
    def run(self, args, conn):
        if not conn.user.vars['shout'] or conn.user.in_silence():
            conn.write(_("(Did not it-shout because you are not listening to shouts)\n"))
        else:
            count = 0
            name = conn.user.name
            dname = conn.user.get_display_name()
            for u in online.online:
                if u.vars['shout'] and not u.in_silence():
                    if name not in u.censor:
                        u.write(_("--> %s %s\n") %
                            (dname, args[0]))
                        count += 1
            conn.write(ngettext("(it-shouted to %d player)\n", "(it-shouted to %d players)\n", count) % count)

@ics_command('cshout', 'S', admin.Level.user)
class Cshout(Command):
    @requires_registration
    def run(self, args, conn):
        if not conn.user.vars['cshout'] or conn.user.in_silence():
            conn.write(_("(Did not c-shout because you are not listening to c-shouts)\n"))
        else:
            count = 0
            name = conn.user.name
            dname = conn.user.get_display_name()
            for u in online.online:
                if u.vars['cshout'] and not u.in_silence():
                    if name not in u.censor:
                        u.write_("%s c-shouts: %s\n", (dname, args[0]))
                        count += 1
            conn.write(ngettext("(c-shouted to %d player)\n", "(c-shouted to %d players)\n", count) % count)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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

@ics_command('ping', 'o')
class Ping(Command):
    def run(self, args, conn):
        if args[0] is not None:
            u2 = user.find.by_prefix_for_user(args[0], conn,
                online_only=True)
        else:
            u2 = conn.user

        if u2:
            pt = u2.session.ping_time
            if not u2.has_timeseal():
                conn.write(_('Ping time not available; %s is not using zipseal.\n') %
                    u2.name)
            elif len(pt) < 2:
                conn.write(_('Ping time not available; please wait.\n'))
            else:
                conn.write(_('Ping time for %s, based on %d samples:\n') %
                    (u2.name, len(pt)))
                avg = 1000.0 * sum(pt) / len(pt)
                conn.write(_('Average: %.3fms\n') % (avg))

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

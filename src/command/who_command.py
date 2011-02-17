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

from command import ics_command, Command

import online
import game
import time_format

@ics_command('showadmins', '')
class Showadmins(Command):
    def run(self, args, conn):
        conn.write('Admins:\n')
        conn.write('Name              Status       Idle time\n')
        admins = [u for u in online.online if u.is_admin()]
        for u in admins:
            if u.session.game and u.session.game.gtype == game.PLAYED:
                status = 'Playing'
            elif not u.on_duty_as('admin'):
                status = 'Off_duty'
            elif u.session.get_idle_time() >= 300:
                status = 'Idle'
            else:
                status = 'Available'
            idle = time_format.hms_words(u.session.get_idle_time())
            conn.write('%-17s %-12s %s\n' % (u.name, status, idle))
        conn.write(ngettext('\n%d admin logged in.\n',
            '\n%d admins logged in.\n', len(admins)) % len(admins))

@ics_command('who', 'T')
class Who(Command):
    def run(self, args, conn):
        count = 0
        conn.write('\n')
        for u in online.online:
            conn.write(u.get_display_name() + '\n')
            count = count + 1
        conn.write('\n')
        conn.write(ngettext('%d player displayed.\n\n', '%d players displayed.\n\n', count) % count)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

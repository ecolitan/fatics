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

import time

import admin
import rating
import user
import game

from command import ics_command, Command
from command_parser import BadCommandError
from db import db

class LogMixin(object):
    def _display_log(self, log, conn):
        for a in reversed(log):
            if conn.user.is_admin():
                ip = _(' from %s') % a['log_ip']
            else:
                ip = ''
            when = conn.user.format_datetime(a['log_when'])
            conn.write('%s: %-20s %-6s%s\n' %
                (when, a['log_who_name'], a['log_which'], ip))

@ics_command('finger', 'ooo')
class Finger(Command):
    def run(self, args, conn):
        if args[0] is not None:
            u = user.find.by_prefix_for_user(args[0], conn, min_len=2)
        else:
            u = conn.user
        if u:
            conn.write(_('Finger of %s:\n\n') % u.get_display_name())

            if u.is_online:
                conn.write(_('On for: %s   Idle: %s\n') % (u.session.get_online_time(), u.session.get_idle_time()))
                if u.vars['silence']:
                    conn.write(_('%s is in silence mode.\n') % u.name)

                if u.session.game:
                    g = u.session.game
                    if g.gtype == game.PLAYED:
                        conn.write(_('(playing game %d: %s vs. %s)\n') % (g.number, g.white.name, g.black.name))
                    elif g.gtype == game.EXAMINED:
                        conn.write(_('(examining game %d)\n') % (g.number))
                    else:
                        assert(False)
            else:
                if u.last_logout is None:
                    conn.write(_('%s has never connected.\n') % u.name)
                else:
                    conn.write(_('Last disconnected: %s\n') % time.strftime("%a %b %e, %H:%M %Z %Y", u.last_logout.timetuple()))

            conn.write('\n')

            #if u.is_guest:
            #    conn.write(_('%s is NOT a registered player.\n') % u.name)
            if not u.is_guest:
                rating.show_ratings(u, conn)
            if u.admin_level > admin.Level.user:
                conn.write(A_('Admin level: %s\n') % admin.level.to_str(u.admin_level))
            if conn.user.admin_level > admin.Level.user:
                if not u.is_guest:
                    conn.write(A_('Email:       %s\n') % u.email)
                    conn.write(A_('Real name:   %s\n') % u.real_name)
                if u.is_online:
                    conn.write(A_('Host:        %s\n') % u.session.conn.ip)

            if u.is_online:
                if u.session.use_timeseal:
                    conn.write(_('Timeseal:    On\n'))
                elif u.session.use_zipseal:
                    conn.write(_('Zipseal:     On\n'))
                else:
                    conn.write(_('Zipseal:     Off\n'))

            notes = u.notes
            if len(notes) > 0:
                conn.write('\n')
                prev_max = 0
                for (num, txt) in sorted(notes.iteritems()):
                    num = int(num)
                    assert(num >= prev_max + 1)
                    assert(num <= 10)
                    if num > prev_max + 1:
                        # fill in blank lines
                        for j in range(prev_max + 1, num):
                            conn.write(_("%2d: %s\n") % (j, ''))
                    conn.write(_("%2d: %s\n") % (num, txt))
                    prev_max = num
                conn.write('\n')

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

@ics_command('logons', 'o')
class Logons(Command, LogMixin):
    def run(self, args, conn):
        if args[0] is not None:
            u2 = user.find.by_prefix_for_user(args[0], conn)
        else:
            u2 = conn.user
        if u2:
            log = u2.get_log()
            if not log:
                conn.write('%s has not logged on.\n' % u2.name)
            else:
                self._display_log(log, conn)

@ics_command('llogons', 'p')
class Llogons(Command, LogMixin):
    def run(self, args, conn):
        if args[0] is not None:
            if args[0] < 0:
                raise BadCommandError
            limit = min(args[0], 200)
        else:
            limit = 200

        self._display_log(db.get_log_all(limit), conn)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

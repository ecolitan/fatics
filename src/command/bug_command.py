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

import var
import user
import partner
import online
import speed_variant
import game

from command_parser import BadCommandError
from command import Command, ics_command

@ics_command('partner', 'o')
class Partner(Command):
    def run(self, args, conn):
        if not args[0]:
            if conn.user.session.partner:
                p = conn.user.session.partner
                assert(p.is_online)
                assert(p.session.partner == conn.user)
                p.write_('%s has left the partnership.', conn.user.name)
                partner.end_partnership(conn.user, p)
            else:
                conn.write(_('You do not have a bughouse partner.\n'))
        else:
            u = user.find.by_prefix_for_user(args[0], conn, online_only=True)
            if not u:
                return

            if conn.user.name in u.censor:
                conn.write(_('%s is censoring you.\n') % u.name)
                return

            if u == conn.user:
                conn.write(_("You can't be your own bughouse partner.\n"))
                return
            if conn.user.session.partner:
                conn.write(_("You are already %s's bughouse partner.\n") %
                    conn.user.session.partner.name)
                return
            if u.session.partner:
                conn.write(_('%s already has a partner.\n') % u.name)
                return

            if not u.vars['bugopen']:
                conn.write(_('%s is not open for bughouse.\n') % u.name)
                return
            if not conn.user.vars['bugopen']:
                conn.write(_('Setting you open for bughouse.\n'))
                var.vars['bugopen'].set(conn.user, '1')

            partner.Partner(conn.user, u)


@ics_command('bugwho', 'o')
class Bugwho(Command):
    def run(self, args, conn):
        if args[0] not in [None, 'g', 'p', 'u']:
            raise BadCommandError
        if args[0] is None or args[0] == 'g':
            # bughouse games
            conn.write(_('Bughouse games in progress\n'))
            count = 0
            for g in game.games.values():
                if game.variant.name == 'bughouse':
                    count += 1
            conn.write(ngettext('%d game displayed.\n',
                '  %d games displayed.\n', count) % count)
        if args[0] is None or args[0] == 'p':
            conn.write(_('Partnerships not playing bughouse\n'))
            for p in partner.partners:
                [p1, p2] = list(p)
                conn.write('%s %s / %s %s\n' %
                    (p1.get_rating(speed_variant.from_names('blitz',
                        'bughouse')), p1.get_display_name(),
                        p2.get_rating(speed_variant.from_names('blitz',
                        'bughouse')), p2.get_display_name()))
            count = len(partner.partners)
            conn.write(ngettext('%d partnership displayed.\n',
                '  %d partnerships displayed.\n', count) % count)

        if args[0] is None or args[0] == 'u':
            conn.write(_('Unpartnered players with bugopen on\n'))
            ulist = [u for u in online.online if u.vars['bugopen'] and
                not u.session.partner]
            for u in ulist:
                conn.write('%s %s\n' %
                    (u.get_rating(speed_variant.from_names('blitz',
                        'bughouse')), u.get_display_name()))
            total = len(online.online)
            count = len(ulist)
            conn.write(ngettext('%(count)d player displayed (of %(total)d).\n',
                '  %(count)d players displayed (of %(total)d).\n', count)
                % {'count': count, 'total': total})

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

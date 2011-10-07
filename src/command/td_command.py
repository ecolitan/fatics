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

import match
import user
import game
import speed_variant

from command_parser import BadCommandError

@ics_command('rmatch', 'wwt')
class Rmatch(Command):
    def run(self, args, conn):
        if not conn.user.has_title('TD'):
            conn.write(_('Only TD programs are allowed to use this command.\n'))
            return
        u1 = user.find_by_prefix_for_user(args[0], conn, online_only=True)
        if not u1:
            return
        u2 = user.find_by_prefix_for_user(args[1], conn, online_only=True)
        if not u2:
            return
        # ignore censor lists, noplay lists, and open var
        if u1 == u2:
            conn.write(_("A player cannot match himself or herself.\n"))
            return
        if u1.session.game:
            conn.write(_("%s is playing a game.\n") % u1.name)
            return
        if u2.session.game:
            conn.write(_("%s is playing a game.\n") % u2.name)
            return
        match.Challenge(u1, u2, args[2])


@ics_command('tournset', 'wd')
class Tournset(Command):
    def run(self, args, conn):
        if not conn.user.has_title('TD'):
            conn.write(_('Only TD programs are allowed to use this command.\n'))
            return
        u2 = user.find_by_prefix_for_user(args[0], conn, online_only=True)
        if not u2:
            return
        # XXX how to handle guests?

        if args[1] not in [0, 1]:
            raise BadCommandError

        u2.vars['tourney'] = str(args[1])
        if args[1]:
            u2.write_('\n%s has set your tourney variable to ON.\n',
                (conn.user.name,))
        else:
            u2.write_('\n%s has set your tourney variable to OFF.\n',
                (conn.user.name,))

@ics_command('robserve', 'wi')
class Robserve(Command):
    def run(self, args, conn):
        if not conn.user.has_title('TD'):
            conn.write(_('Only TD programs are allowed to use this command.\n'))
            return

        u2 = user.find_by_prefix_for_user(args[0], conn, online_only=True)
        if not u2:
            return

        g = game.from_name_or_number(args[1], conn)
        if g:
            if u2 in g.observers or u2 in g.players:
                # TODO: how to print error message to TD?
                pass
            else:
                g.observe(u2)

@ics_command('getpi', 'w')
class Getpi(Command):
    def run(self, args, conn):
        if not conn.user.has_title('TD'):
            conn.write(_('Only TD programs are allowed to use this command.\n'))
            return
        try:
            u = user.find_by_name_exact(args[0], online_only=True)
            if u and u.is_online:
                if u.is_guest:
                    # it's not clear why the lasker server only prints
                    # 3 numbers here; I don't know if FICS is any
                    # different
                    conn.write('*getpi %s -1 -1 -1*\n' % u.name)
                else:
                    # on original FICS the wild, blitz, standard, and
                    # lightning ratings are given
                    # TODO: some way to update this for the new system
                    # where each speed and variant has a separate rating?
                    conn.write('*getpi %s %d %d %d %d*\n' % (u.name,
                        u.get_rating(speed_variant.blitz_chess960),
                        u.get_rating(speed_variant.blitz_chess),
                        u.get_rating(speed_variant.standard_chess),
                        u.get_rating(speed_variant.lightning_chess)))
            else:
                # do nothing
                pass
        except user.UsernameException:
            # do nothing
            pass

@ics_command('getgi', 'w')
class Getgi(Command):
    def run(self, args, conn):
        if not conn.user.has_title('TD'):
            conn.write(_('Only TD programs are allowed to use this command.\n'))
            return
        try:
            u = user.find_by_name_exact(args[0], online_only=True)
            if u and u.is_online and not u.is_guest:
                g = u.session.game
                if g and g.gtype == game.PLAYED:
                    conn.write('*getgi %s %s %s %d %d %d %d %d*\n' % (u.name,
                        g.white.name, g.black.name, g.number,
                        g.white_time, g.inc,
                        g.rated, g.private))
                else:
                    conn.write(_('%s is not playing a game.\n') % u.name)
            else:
                # do nothing
                pass
        except user.UsernameException:
            # do nothing
            pass

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

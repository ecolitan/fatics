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

@ics_command('rmatch', 'wwt')
class Rmatch(Command):
    def run(self, args, conn):
        if not conn.user.has_title('TD'):
            conn.write(_('Only TD programs are allowed to use this command\n'))
            return
        u1 = user.find.by_prefix_for_user(args[0], conn, online_only=True)
        if not u1:
            return
        u2 = user.find.by_prefix_for_user(args[1], conn, online_only=True)
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
        offer.Challenge(u1, u2, args[2])


@ics_command('tournset', 'wd')
class Tournset(Command):
    def run(self, args, conn):
        if not conn.user.has_title('TD'):
            conn.write(_('Only TD programs are allowed to use this command\n'))
            return
        u2 = user.find.by_prefix_for_user(args[0], conn, online_only=True)
        if not u2:
            return
        # XXX how to handle guests?

        if args[1] not in [0, 1]:
            raise BadCommandError

        u2.vars['tourney'] = str(args[1])
        if args[1]:
            u2.write_('%s has set your tourney variable to ON.\n',
                (conn.user.name,))
        else:
            u2.write_('%s has set your tourney variable to OFF.\n',
                (conn.user.name,))

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

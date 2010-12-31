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

import game
import user

@ics_command('observe', 'i')
class Observe(Command):
    def run(self, args, conn):
        if args[0] in ['/l', '/b', '/s', '/S', '/w', '/z', '/B', '/L', '/x']:
            conn.write('TODO: observe flag\n')
            return
        g = game.from_name_or_number(args[0], conn)
        if g:
            if g in conn.user.session.observed:
                conn.write(_('You are already observing game %d.\n' % g.number))
            elif conn.user in g.players:
                conn.write(_('You cannot observe yourself.\n'))
            else:
                assert(conn.user not in g.observers)
                g.observe(conn.user)

@ics_command('follow', 'o')
class Follow(Command):
    def run(self, args, conn):
        if args[0] is None:
            uf = conn.user.session.following
            if not uf:
                conn.write(_("You are not following any player's games.\n"))
            else:
                assert(uf.is_online)
                uf.session.followed_by.remove(conn.user)
                conn.user.session.following = None
                conn.write(_("You will not follow any player's games.\n"))
        else:
            u2 = user.find_by_prefix_for_user(args[0], conn,
                online_only=True)
            if u2:
                if u2 == conn.user:
                    conn.write(_("You can't follow your own games.\n"))
                    return
                if conn.user.session.following:
                    if u2 == conn.user.session.following:
                        conn.write(_("You are already following %s's games.\n")
                            % u2.name)
                        return
                    conn.user.write(_("You will no longer be following %s's games.\n") % conn.user.session.following.name)
                    conn.user.session.following.session.followed_by.remove(conn.user)
                    conn.user.session.following = None
                conn.write(_("You will now be following %s's games.\n")
                    % u2.name)
                conn.user.session.following = u2
                u2.session.followed_by.add(conn.user)

                # If there is a game in progress and we are not already
                # observing it, start observing it.
                if (u2.session.game and
                        u2.session.game not in conn.user.session.observed):
                    u2.session.game.observe(conn.user)
                    assert(u2.session.game in conn.user.session.observed)

@ics_command('allobservers', 'o')
class Allobservers(Command):
    def run(self, args, conn):
        if args[0] is not None:
            g = game.from_name_or_number(args[0], conn)
            if g:
                if not g.observers:
                    conn.write(_('No one is observing game %d.\n')
                        % g.number)
                else:
                    g.show_observers(conn)
        else:
            for g in game.games.itervalues():
                g.show_observers(conn)

@ics_command('unobserve', 'n')
class Unobserve(Command):
    def run(self, args, conn):
        if args[0] is not None:
            g = game.from_name_or_number(args[0], conn)
            if g:
                if g in conn.user.session.observed:
                    g.unobserve(conn.user)
                else:
                    conn.write(_('You are not observing game %d.\n')
                        % g.number)
        else:
            if not conn.user.session.observed:
                conn.write(_('You are not observing any games.\n'))
            else:
                for g in conn.user.session.observed.copy():
                    g.unobserve(conn.user)
                assert(not conn.user.session.observed)

@ics_command('primary', 'n')
class Primary(Command):
    def run(self, args, conn):
        if args[0] is None:
            if not conn.user.session.observed:
                conn.write(_('You are not observing any games.\n'))
            else:
                conn.write('TODO: primary no param\n')
        else:
            g = game.from_name_or_number(args[0], conn)
            if g:
                if g in conn.user.session.observed:
                    if g == conn.user.session.observed.primary():
                        conn.write(_('Game %d is already your primary game.\n') %
                            g.number)
                    else:
                        conn.user.session.observed.make_primary(g)
                        conn.write(_('Game %d is now your primary game.\n') %
                            g.number)

                else:
                    conn.write('You are not observing game %d.\n' % g.number)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

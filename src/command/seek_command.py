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


import seek
import match
import game
import user

from .match_command import MatchMixin
from command_parser import BadCommandError
from game_constants import *
from command import Command, ics_command

@ics_command('seek', 't')
class Seek(Command):
    def run(self, args, conn):
        if conn.user.session.game:
            if conn.user.session.game.gtype == game.EXAMINED:
                conn.write(_('You are examining a game.\n'))
            else:
                conn.write(_('You are playing a game.\n'))
            return

        if len(conn.user.session.seeks) >= seek.LIMIT:
            conn.write(_('You can only have %d active seeks.\n') % seek.LIMIT)
            return

        try:
            s = seek.Seek(conn.user, args[0])
        except match.MatchError as e:
            conn.write(e[0])
            return

        # Check if the user has already posted the same seek.  It might be
        # more efficient to do this check as part of seek.find_matching()
        if s in seek.seeks.values():
            conn.write(_('You already have an active seek with the same parameters.\n'))
            return

        (auto_matches, manual_matches) = seek.find_matching(s)
        if auto_matches:
            ad = auto_matches[0]
            assert(not ad.manual)
            assert(not ad.expired)
            conn.write(_('Your seek matches one posted by %s.\n') %
                ad.a.name)
            ad.a.write_('Your seek matches one posted by %s.\n',
                (conn.user.name,))
            ad.b = conn.user
            g = game.PlayedGame(ad)
            return

        if manual_matches:
            conn.write(_('Issuing match request since the seek was set to manual.\n'))
            for ad in manual_matches:
                tags = ad.tags.copy()
                # the challenge should use the same parameters as the
                # seek, except that the color requested (if any) is reversed
                if ad.side is not None:
                    tags['side'] = opp(ad.side)
                else:
                    tags['side'] = None
                match.Challenge(conn.user, ad.a, tags=tags)
            # go on to post the seek, too

        count = s.post()
        conn.write(_('Your seek has been posted with index %d.\n') % s.num)
        conn.write(ngettext('(%d player saw the seek.)\n',
            '(%d players saw the seek.)\n', count) % count)

@ics_command('unseek', 'p')
class Unseek(Command):
    def run(self, args, conn):
        n = args[0]
        if n:
            if n in seek.seeks and seek.seeks[n].a == conn.user:
                seek.seeks[n].remove()
                conn.write(_('Your seek %d has been removed.\n') % n)
            else:
                conn.write(_('You have no seek %d.\n') % n)
        else:
            if conn.user.session.seeks:
                for s in conn.user.session.seeks:
                    s.remove()
                conn.write(_('Your seeks have been removed.\n'))
            else:
                conn.write(_('You have no active seeks.\n'))

@ics_command('play', 'i')
class Play(Command, MatchMixin):
    def run(self, args, conn):
        if conn.user.session.game:
            if conn.user.session.game.gtype == game.EXAMINED:
                conn.write(_('You are examining a game.\n'))
            else:
                conn.write(_('You are playing a game.\n'))
            return

        ad = None
        if type(args[0]) == str:
            u = user.find.by_prefix_for_user(args[0], conn, online_only=True)
            if u:
                if not u.session.seeks:
                    conn.write(_("%s isn't seeking any games.\n") % u.name)
                elif len(u.session.seeks) > 1:
                    conn.write(_("%s is seeking several games.\n") % u.name)
                else:
                    ad = u.session.seeks[0]
                    assert(not ad.expired)
        else:
            try:
                ad = seek.seeks[args[0]]
            except KeyError:
                # no such seek
                ad = None
            else:
                if ad.expired:
                    ad = None
            if not ad:
                conn.write(_('That seek is not available.\n'))

        if ad:
            if not match.check_censor_noplay(conn.user, ad.a):
                ad = None
            # check formula
            elif not ad.check_formula(conn.user):
                conn.write(_('Match request does not fit formula for %s:') %
                    ad.a.name)
                ad = None
            # we don't check this user's formula, since using the "play"
            # command implicitly accepted the match terms

        if ad:
            if ad.manual:
                conn.write(_('Issuing match request since the seek was set to manual.\n'))
                tags = ad.tags.copy()
                if ad.side is not None:
                    tags['side'] = opp(ad.side)
                else:
                    tags['side'] = None
                match.Challenge(conn.user, ad.a, tags=tags)
            else:
                ad.a.write_('%s accepts your seek.' % (conn.user.name,))
                ad.accept(conn.user)

#  7 1500 SomePlayerA         5   2 rated   blitz      [white]  1300-9999 m
@ics_command('sought', 'o')
class Sought(Command):
    def run(self, args, conn):
        if args[0] is not None:
            if args[0] == 'all':
                slist = [s for s in seek.seeks.values() if not s.expired]
            else:
                raise BadCommandError
        else:
            slist = [s for s in seek.seeks.values() if not s.expired and
                not conn.user.censor_or_noplay(s.a) and
                s.check_formula(conn.user) and s.meets_formula_for(conn.user)]

        slist.sort(key=lambda s: s.num)
        count = 0
        for s in slist:
            conn.write('%s\n' % s)
            count += 1
        conn.write(ngettext('%d ad displayed.\n', '%d ads displayed.\n',
            count) % count)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

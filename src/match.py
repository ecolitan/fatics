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

import re
import copy

import game
import speed_variant
import clock
import command_parser
import formula
import var

from offer import Offer
from game_constants import *
from db import db


shortcuts = {
    'r': 'rated',
    'u': 'unrated',
    'w': 'white',
    'b': 'black',
    'fischerrandom': 'chess960',
    'fischerandom': 'chess960',
    'fr': 'chess960',
    'cra': 'crazyhouse',
    'zh': 'crazyhouse',
    # seeks only
    'm': 'manual',
    'f': 'formula',
}

class MatchError(Exception):
    pass

class MatchStringParser(object):
    """ Mixin used to parse both match and seek strings. """
    def _set_rated(self, val):
        assert(val in [True, False])
        if self.rated is not None:
            raise command_parser.BadCommandError()
        self.rated = val

    def _set_side(self, val):
        assert(val in [WHITE, BLACK])
        if self.side is not None:
            raise command_parser.BadCommandError()
        self.side = val

    def _set_variant_name(self, val):
        if self.variant_name is not None:
            # conflicting variants
            raise command_parser.BadCommandError()
        self.variant_name = val

    def _set_clock_name(self, val):
        if self.clock_name is not None:
            # conflicting clock types
            raise command_parser.BadCommandError()
        self.clock_name = val

    def _set_time(self, val):
        if self.time is not None:
            raise command_parser.BadCommandError()
        assert(val >= 0)
        self.time = val

    def _set_inc(self, val):
        if self.inc is not None:
            raise command_parser.BadCommandError()
        assert(val >= 0)
        self.inc = val

    def _set_manual(self, val):
        if self.manual is not None:
            raise command_parser.BadCommandError()
        self.manual = val

    def _set_formula(self, val):
        if self.formula is not None:
            raise command_parser.BadCommandError()
        self.formula = val

    _idn_re = re.compile(r'idn=(\d+)')
    _plus_re = re.compile(r'(\d+)\+(\d+)')
    # e.g. 40/90,sd/30+30
    _overtime_re = re.compile(r'(\d+)/(\d+),sd/(\d+)(?:\+(\d+))?', re.I)
    def _parse_args_common(self, args, u):
        """ Do the parsing of a match string that is common to both match
        commands and seek commands. Raises MatchError on invalid syntax
        or disallowed combinations of options. """
        self.variant_name = None
        self.clock_name = None

        self.time = None
        self.inc = None
        self.rated = None
        self.side = None # the side requested, if any
        self.idn = None
        # seeks only
        self.manual = None
        self.formula = None

        if args is None:
            words = []
        else:
            assert(args == args.lower())
            words = re.split(r'\s+', args)

        times = []
        for w in words:
            if w in shortcuts:
                w = shortcuts[w]

            try:
                times.append(int(w))
                continue
            except ValueError:
                pass

            if w == 'unrated':
                self._set_rated(False)
            elif w == 'rated':
                self._set_rated(True)
            elif w == 'white':
                self._set_side(WHITE)
            elif w == 'black':
                self._set_side(BLACK)

            elif w == 'manual':
                self._set_manual(True)
            elif w == 'auto':
                self._set_manual(False)
            elif w == 'formula':
                self._set_formula(True)
            # currently there no way to explicitly specify the default of
            # no formula

            elif w in speed_variant.variant_names:
                self._set_variant_name(w)

            elif w in clock.clock_names:
                self._set_clock_name(w)

            else:
                m = re.match(self._idn_re, w)
                if m:
                    # TODO: self._set_idn
                    if self.idn is not None:
                        raise command_parser.BadCommandError
                    self.idn = int(m.group(1))
                    if self.idn < -1 or self.idn > 959:
                        raise MatchError(_('An idn must be between 0 and 959.\n'))
                    continue

                m = re.match(self._plus_re, w)
                if m:
                    self._set_time(int(m.group(1)))
                    self._set_inc(int(m.group(2)))
                    continue

                m = re.match(self._overtime_re, w)
                if m:
                    self._set_clock_name('overtime')
                    # e.g. 40/90,sd/30+30
                    self.overtime_move_num = int(m.group(1))
                    self._set_time(int(m.group(2)))
                    self.overtime_bonus = int(int(m.group(3)))
                    if m.group(4) is not None:
                        self._set_inc(int(m.group(4)))
                    else:
                        self._set_inc(0)
                    continue

                #print('got unknown keyword "%s"' % w)
                raise command_parser.BadCommandError

        if len(times) > 2:
            # time odds not supported
            raise command_parser.BadCommandError
        elif len(times) == 2:
            self._set_time(times[0])
            self._set_inc(times[1])
        elif len(times) == 1:
            self._set_time(times[0])

        # validate the match parameters
        if self.rated and self.clock_name in ['hourglass', 'untimed']:
            raise MatchError(_('This clock type cannot be used in rated games.\n'))

        if self.clock_name == 'untimed':
            if self.time != 0:
                self._set_time(0)
            if self.inc != 0:
                self._set_inc(0)

        if self.time is None:
            self.time = u.vars['time']
        if self.inc is None:
            if self.clock_name == 'hourglass':
                # default to no increment
                self.inc = 0
            else:
                self.inc = u.vars['inc']

        if self.clock_name == 'bronstein' and not self.inc:
            raise MatchError(_('Games using a Bronstein clock must have an increment.\n'))
        if self.clock_name == 'hourglass' and self.inc:
            raise MatchError(_('Games using an hourglass clock may not have an increment.\n'))
        if self.clock_name == 'overtime':
            if self.time < 1:
                raise MatchError(_('Games using an overtime clock must have a positive initial time.\n'))
            if self.overtime_bonus < 1:
                raise MatchError(_('Games using an overtime clock must have a positive overtime bonus.\n'))
            # I would make the limit higher, but the test depends on it
            # being low....
            if self.overtime_move_num < 3:
                raise MatchError(_('Invalid number of moves before overtime bonus.\n'))

        if self.time == 0 and self.inc == 0:
            if self.clock_name != 'untimed':
                self._set_clock_name('untimed')

        # defaults
        if self.variant_name is None:
            self.variant_name = 'chess'

        if self.clock_name is None:
            self.clock_name = 'fischer'

        if self.idn is not None and (self.variant_name != 'chess960'
                or self.rated):
            raise MatchError(_('You may only specify an idn for unrated chess960 games.\n'))

        if self.clock_name == 'untimed':
            self.speed_name = 'untimed'
        else:
            expected_duration = self.time + self.inc * float(2) / 3
            if self.clock_name == 'overtime':
                expected_duration += self.overtime_bonus
            elif self.clock_name == 'hourglass':
                # ???
                expected_duration *= 3
            assert(expected_duration > 0)
            if expected_duration < 3.0:
                self.speed_name = 'lightning'
            elif expected_duration < 15.0:
                self.speed_name = 'blitz'
            elif expected_duration < 75.0:
                self.speed_name = 'standard'
            else:
                self.speed_name = 'slow'

        self.speed_variant = speed_variant.from_names(self.speed_name,
            self.variant_name)

def check_censor_noplay(a, b):
    """ Test whether a user can play a given opponent. """
    if a.name in b.censor:
        a.write(_("%s is censoring you.\n") % b.name)
        return False
    if a.name in b.noplay:
        a.write(_("You are on %s's noplay list.\n") % b.name)
        return False
    if b.name in a.censor:
        a.write(_("You are censoring %s.\n") % b.name)
        return False
    if b.name in a.noplay:
        a.write(_("You have %s on your noplay list.\n") % b.name)
        return False
    return True

class Challenge(Offer, MatchStringParser):
    """ represents a match offer from one player to another """
    def __init__(self, a, b, args=None, tags=None):
        """ Initiate a new offer.  "a" is the player issuing the offer;
        "b" receives the request """
        Offer.__init__(self, 'match offer')

        self.a = a
        self.b = b

        if a.is_guest or b.is_guest:
            self.adjourned = None
        else:
            self.adjourned = db.get_adjourned_between(a.id, b.id)
        if self.adjourned:
            if tags or args:
                a.write_('You have an adjourned game with %s.  You cannot start a new game until you finish it.\n', b.name)
                return
            tags = self.adjourned.copy()
            tags.update({
                'side': None
            })
        else:
            if not check_censor_noplay(a, b):
                return

        if tags:
            # copy match parameters
            self.side = tags['side']
            self.rated = tags['rated']
            self.speed_name = tags['speed_name']
            self.variant_name = tags['variant_name']
            self.clock_name = tags['clock_name']
            self.time = tags['time']
            self.inc = tags['inc']
            self.idn = tags['idn']
            self.speed_variant = speed_variant.from_names(self.speed_name,
                self.variant_name)
            self.a_rating = a.get_rating(self.speed_variant)
            self.b_rating = b.get_rating(self.speed_variant)
            # TODO: overtime move number, bonus
        else:
            # get match parameters from a string or use defaults
            try:
                self._check_open()
                self._parse_args(args, a, b)
            except MatchError as e:
                a.write(e[0])
                return

        # look for a matching offer from player b
        o = next((o for o in a.session.offers_received if
            o.name == self.name and o.equivalent_to(self)), None)
        if o:
            # a already received an identical offer, so just accept it
            a.write_("Your challenge intercepts %s's challenge.\n", (o.a.name,))
            b.write_("%s's challenge intercepts your challenge.\n", (a.name,))
            # XXX don't send "Accepting" and "USER accepts" messages?
            o.accept()
            return

        # build the "Challenge:" string
        if self.side is not None:
            side_str = ' [%s]' % game.side_to_str(self.side)
        else:
            side_str = ''

        rated_str = "rated" if self.rated else "unrated"

        if self.clock_name == 'untimed':
            time_str = ''
        else:
            time_str = ' %d %d' % (self.time, self.inc)

        # example: GuestABCD (++++) [white] hans (----) unrated blitz 5 0.
        challenge_str = '%s (%s)%s %s (%s) %s %s%s' % (self.a.name,
            self.a_rating, side_str, self.b.name, self.b_rating, rated_str,
            self.speed_variant, time_str)
        if self.idn is not None:
            challenge_str = '%s idn=%d' % (challenge_str, self.idn)
        if self.clock_name not in ['fischer', 'untimed']:
            challenge_str = '%s %s' % (challenge_str, self.clock_name)
        if self.clock_name == 'overtime':
            challenge_str = '%s %d/%d,SD/%d+%d' % (challenge_str,
                self.overtime_move_num, self.time, self.overtime_bonus,
                self.inc)
        if self.adjourned:
            challenge_str = '%s (adjourned)' % challenge_str
        #if self.board is not None:
        #    challenge_str = 'Loaded from a board'

        a_sent = a.session.offers_sent
        b_sent = b.session.offers_sent
        a_received = a.session.offers_received
        b_received = b.session.offers_received

        if self in a_sent:
            a.write_('You are already offering an identical match to %s.\n',
                (b.name,))
            return

        if not formula.check_formula(self, b.vars['formula']):
            a.write_('Match request does not meet formula for %s:\n', b.name)
            b.write_('Ignoring (formula): %s\n', challenge_str)
            return

        if self.variant_name == 'bughouse':
            # build the challenge string for the other game
            apart = a.session.partner
            bpart = b.session.partner
            challenge_str2 = '%s (%s)%s %s (%s) %s %s%s' % (apart.name,
                apart.get_rating(self.speed_variant), side_str,
                bpart.name, bpart.get_rating(self.speed_variant), rated_str,
                self.speed_variant, time_str)
            if self.idn is not None:
                challenge_str2 = '%s idn=%d' % (challenge_str2, self.idn)
            if self.clock_name not in ['fischer', 'untimed']:
                challenge_str2 = '%s %s' % (challenge_str2, self.clock_name)
            if self.clock_name == 'overtime':
                challenge_str2 = '%s %d/%d,SD/%d+%d' % (challenge_str2,
                    self.overtime_move_num, self.time, self.overtime_bonus,
                    self.inc)
            if self.adjourned:
                challenge_str2 = '%s (adjourned)' % challenge_str2

            # inform the other two players about the challenge
            apart.write_('Your bughouse partner issues: %s\n', challenge_str)
            apart.write_('Your game will be: %s\n', challenge_str2)
            bpart.write_('Your bughouse partner was challenged: %s\n',
                challenge_str)
            bpart.write_('Your game will be: %s\n', challenge_str2)


        o = next((o for o in b_sent if o.name == self.name and
            o.b == a), None)
        if o:
            a.write_('Declining the offer from %s and proposing a counteroffer.\n', (b.name,))
            b.write_('%s declines your offer and proposes a counteroffer.\n', (a.name,))
            o.decline(notify=False)

        o = next((o for o in a_sent if o.name == self.name and
            o.b == b), None)
        if o:
            a.write_('Updating the offer already made to %s.\n', (b.name,))
            b.write_('%s updates the offer.\n', (a.name,))
            a_sent.remove(o)
            b_received.remove(o)

        self._register()

        a.write('Issuing: %s\n' % challenge_str)
        b.write('Challenge: %s\n' % challenge_str)
        if a.has_title('abuser'):
            b.write_('--** %s is an abuser **--\n', (a.name,))
        if b.has_title('abuser'):
            a.write_('--** %s is an abuser **--\n', (b.name,))
        if a.has_title('computer'):
            b.write_('--** %s is a computer **--\n', (a.name,))
        if b.has_title('computer'):
            a.write_('--** %s is a computer **--\n', (b.name,))
        b.write_('You can "accept", "decline", or propose different parameters.\n')

    def _parse_args(self, args, a, b):
        """ Parse the arguments, including parsing specific to match
        requests (as opposed to seeks). """
        self._parse_args_common(args, a)

        # match-specific parsing
        if self.formula is not None or self.manual is not None:
            raise MatchError(_('The "formula" and "manual" keywords may not be used with match requests.\n'))
        if self.rated is None:
            if a.is_guest or b.is_guest or self.clock_name in [
                    'hourglass', 'untimed']:
                a.write_('Setting match offer to unrated.\n')
                self.rated = False
            else:
                # Original FICS uses the 'rated' var, but we default to True
                self.rated = True
        if self.rated and (a.is_guest or b.is_guest):
            raise MatchError(_('Only registered players can play rated games.\n'))
        if a.is_playbanned:
            raise MatchError(_('You may not play games.\n'))
        if b.is_playbanned:
            raise MatchError(_('%s may not play games.\n') % b.name)
        if self.rated:
            if a.is_ratedbanned:
                raise MatchError(_('You may not play rated games.\n'))
            if b.is_ratedbanned:
                raise MatchError(_('%s may not play rated games.\n') % b.name)

        # check bughouse partners' availability
        if self.variant_name == 'bughouse':
            if not a.session.partner:
                raise MatchError(_('You have no partner for bughouse.\n'))
            if not b.session.partner:
                raise MatchError(_('Your opponent has no partner for bughouse.\n'))
            apart = a.session.partner
            bpart = b.session.partner
            assert(a.vars['bugopen'])
            assert(b.vars['bugopen'])
            assert(apart.vars['bugopen'])
            assert(bpart.vars['bugopen'])
            if a == bpart:
                raise MatchError(_('You cannot challenge your own partner for bughouse.\n'))
            if not apart.vars['open'] or apart.session.game:
                raise MatchError(_('Your partner is not available to play right now.\n'))
            if not bpart.vars['open'] or bpart.session.game:
                raise MatchError(_("Your opponent's partner is not available to play right now.\n"))
            assert(b != apart)
            assert(apart != bpart)

            # check playban and ratedban lists
            if apart.is_playbanned:
                raise MatchError(_('Your partner may not play games.\n'))
            if bpart.is_playbanned:
                raise MatchError(_("Your opponent's partner may not play games.\n"))
            if self.rated:
                if apart.is_ratedbanned:
                    raise MatchError(_('Your partner may not play rated games.\n'))
                if bpart.is_ratedbanned:
                    raise MatchError(_("Your opponent's partner may not play rated games.\n"))

        self.a_rating = a.get_rating(self.speed_variant)
        self.b_rating = b.get_rating(self.speed_variant)

    def _check_open(self):
        """ Test whether an opponent is open to match requests, and
        open the challenging player to match requests if necessary. """
        [a, b] = [self.a, self.b]
        if not b.vars['open']:
            raise MatchError(_("%s is not open to match requests.\n") % b.name)
        if b.session.game:
            if b.session.game.gtype == game.EXAMINED:
                raise MatchError(_("%s is examining a game.\n") % b.name)
            else:
                raise MatchError(_("%s is playing a game.\n") % b.name)

        if not a.vars['open']:
            var.vars['open'].set(a, '1')

    def __eq__(self, other):
        if (self.name == other.name and
                self.a == other.a and
                self.b == other.b and
                self.time == other.time and
                self.inc == other.inc and
                self.side == other.side and
                self.variant_name == other.variant_name and
                self.clock_name == other.clock_name and
                self.idn == other.idn):
            return True
        return False

    def __hash__(self, other):
        return hash((self.a, self.b, self.time, self.inc, self.side))

    def equivalent_to(self, other):
        """ Check whether a player B has already offered an identical
        match to A, so that the challenges intercept. """
        if self.adjourned and self.a == other.b and self.b == other.a:
            assert(other.adjourned)
            return True

        if self.speed_variant.variant != other.speed_variant.variant:
            return False

        # opposite but equivalent?
        if (self.a == other.b and
                self.b == other.a and
                self.time == other.time and
                self.inc == other.inc and
                (self.side is None and other.side is None) or
                (self.side in [WHITE, BLACK] and
                    other.side in [WHITE, BLACK] and
                    self.side != other.side)):
            return True

        return False

    def accept(self):
        Offer.accept(self)

        g = game.PlayedGame(self)
        if self.variant_name == 'bughouse':
            chal2 = copy.copy(self)
            chal2.a = self.a.session.partner
            chal2.b = self.b.session.partner
            chal2.side = g.get_user_side(self.b)
            g2 = game.PlayedGame(chal2)
            g2.bug_link = g
            g.bug_link = g2
            g2.variant.pos.bug_link = g.variant.pos
            g.variant.pos.bug_link = g2.variant.pos

    def withdraw_logout(self):
        Offer.withdraw_logout(self)
        self.a.write_('Challenge to %s withdrawn.\n',
            (self.b.name,))
        self.b.write_('%s, who was challenging you, has departed.\n',
            (self.a.name,))
        self.b.write_('Challenge from %s removed.\n',
            (self.a.name,))

    def decline_logout(self):
        Offer.decline_logout(self)
        self.b.write_('Challenge from %s removed.\n',
            (self.a.name,))
        self.a.write_('%s, whom you were challenging, has departed.\n',
            (self.b.name,))
        self.a.write_('Challenge to %s withdrawn.\n',
            (self.b.name,))

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

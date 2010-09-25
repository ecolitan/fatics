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

import game
import speed_variant
import clock
import command_parser
import formula

from offer import Offer
from game_constants import *


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
    'f': 'formula' # seeks only
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

    _wild_re = re.compile(r'w(\d+)')
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

            elif w in speed_variant.variant_names:
                self._set_variant_name(w)

            elif w in clock.clock_names:
                self._set_clock_name(w)

            else:
                m = re.match(self._wild_re, w)
                if m:
                    self._set_variant_name(m.group(1))
                    continue

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

class Challenge(Offer, MatchStringParser):
    """ represents a match offer from one player to another """
    def __init__(self, a, b, args):
        """ Initiate a new offer.  "a" is the player issuing the offer;
        "b" receives the request """
        Offer.__init__(self, "match offer")

        self.a = a
        self.b = b

        try:
            self._parse_args(args, a, b)
        except MatchError as e:
            a.write(e[0])
            return

        # look for a matching offer from player b
        o = next((o for o in a.session.offers_received if
            o.name == self.name and o.equivalent_to(self)), None)
        if o:
            # a already received an identical offer, so just accept it
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

        # example: Guest (++++) [white] hans (----) unrated blitz 5 0.
        challenge_str = '%s (%s)%s %s (%s) %s %s%s' % (self.a.name, self.a_rating, side_str, self.b.name, self.b_rating, rated_str, self.speed_variant, time_str)
        if self.idn is not None:
            challenge_str = '%s idn=%d' % (challenge_str, self.idn)
        if self.clock_name not in ['fischer', 'untimed']:
            challenge_str = '%s %s' % (challenge_str, self.clock_name)
        if self.clock_name == 'overtime':
            challenge_str = '%s %d/%d,SD/%d+%d' % (challenge_str,
                self.overtime_move_num, self.time, self.overtime_bonus,
                self.inc)

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

        o = next((o for o in b_sent if o.name == self.name), None)
        if o:
            a.write_('Declining the offer from %s and proposing a counteroffer.\n', (b.name,))
            b.write_('%s declines your offer and proposes a counteroffer.\n', (a.name,))
            o.decline(notify=False)

        o = next((o for o in a_sent if o.name == self.name), None)
        if o:
            a.write_('Updating the offer already made to %s.\n', (b.name,))
            b.write_('%s updates the offer.\n', (a.name,))
            a_sent.remove(o)
            b_received.remove(o)

        a_sent.append(self)
        b_received.append(self)

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
        self.speed_variant

        # match-specific parsing
        if self.rated is None:
            if a.is_guest or b.is_guest or self.clock_name in [
                    'hourglass', 'untimed']:
                a.write_('Setting match offer to unrated.\n')
                self.rated = False
            else:
                # Original FICS uses the 'rated' var, but we default to True
                self.rated = True
        elif self.rated and (a.is_guest or b.is_guest):
            raise MatchError(_('Only registered players can play rated games.\n'))
            return

        self.a_rating = a.get_rating(self.speed_variant)
        self.b_rating = b.get_rating(self.speed_variant)

    def __eq__(self, other):
        if (self.name == other.name and
                self.a == other.a and
                self.b == other.b and
                self.time == other.time and
                self.inc == other.inc and
                self.side == other.side):
            return True
        return False

    def __hash__(self, other):
        return hash((self.a, self.b, self.time, self.inc, self.side))

    def equivalent_to(self, other):
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

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

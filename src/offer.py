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

class Offer(object):
    """represents an offer from one player to another"""
    def __init__(self, name):
        self.name = name
        self.game = None

    def accept(self):
        """player b accepts"""
        self.a.session.offers_sent.remove(self)
        self.b.session.offers_received.remove(self)

        self.b.write(_("Accepting the %(offer)s from %(name)s.\n") % {
            'offer': self.name, 'name': self.a.name})
        self.a.write(_("%(name)s accepts your %(offer)s.\n") % {
            'name': self.b.name, 'offer': self.name})
        if self.game:
            for p in self.game.observers:
                p.write(_("%(name)s accepts the %(offer)s.\n") % {
                    'name': self.b.name, 'offer': self.name})

    def decline(self, notify=True):
        """player b declines"""
        if notify:
            self.a.write(_("%s declines your %s.\n") % (self.b.name,
                self.name))
            self.b.write(_("Declining the %s from %s.\n") % (self.name,
                self.a.name))
            if self.game:
                for p in self.game.observers:
                    p.write(_("%(name)s declines the %(offer)s.\n") % {
                        'name': self.b.name, 'offer': self.name})
        self.a.session.offers_sent.remove(self)
        self.b.session.offers_received.remove(self)

    def withdraw(self, notify=True):
        """player a withdraws the offer"""
        if notify:
            self.a.write(_("Withdrawing your %s to %s.\n") % (self.name,
                self.b.name))
            self.b.write(_("%s withdraws the %s.\n") % (self.a.name,
                self.name))
            if self.game:
                for p in self.game.observers:
                    p.write(_("%(name)s withdraws the %(offer)s.\n") % {
                        'name': self.a.name, 'offer': self.name})
        self.a.session.offers_sent.remove(self)
        self.b.session.offers_received.remove(self)

class Abort(Offer):
    def __init__(self, game, user):
        Offer.__init__(self, 'abort request')

        self.a = user
        self.b = game.get_opp(user)
        self.game = game
        offers = [o for o in game.pending_offers if o.name == self.name]
        if len(offers) > 1:
            raise RuntimeError('more than one abort request in game %d' \
                % game.number)
        if len(offers) > 0:
            o = offers[0]
            if o.a == self.a:
                user.write_('You are already offering to abort game %d.\n', (game.number,))
            else:
                o.accept()
        else:
            game.pending_offers.append(self)
            user.write_('Requesting to abort game %d.\n', (game.number,))
            self.b.write_('%(name)s requests to abort game %(num)d.\n', {
                'name': user.name, 'num': game.number})
            for p in game.observers:
                p.write_('%(name)s requests to abort game %(num)d.\n', {
                    'name': user.name, 'num': game.number})
            a_sent = user.session.offers_sent
            b_received = self.b.session.offers_received
            a_sent.append(self)
            b_received.append(self)

    def decline(self, notify=True):
        Offer.decline(self, notify)
        self.game.pending_offers.remove(self)

    def accept(self):
        Offer.accept(self)
        self.game.pending_offers.remove(self)
        self.game.result('Game aborted by agreement', '*')

    def withdraw(self, notify=True):
        Offer.withdraw(self, notify)
        self.game.pending_offers.remove(self)

class Adjourn(Offer):
    def __init__(self, game, user):
        Offer.__init__(self, 'adjourn request')

        self.a = user
        self.b = game.get_opp(user)
        self.game = game
        offers = [o for o in game.pending_offers if o.name == self.name]
        if len(offers) > 1:
            raise RuntimeError('more than one adjourn offer in game %d' \
                % game.number)
        if len(offers) > 0:
            o = offers[0]
            if o.a == self.a:
                user.write_('You are already offering to adjourn game %d.\n', (game.number,))
            else:
                # XXX should we disallow adjourning games in the first few
                # moves?
                o.accept()
        else:
            game.pending_offers.append(self)
            user.write_('Requesting to adjourn game %d.\n', (game.number,))
            self.b.write_('%s requests to adjourn game %d.\n', (user.name, game.number))
            for p in game.observers:
                p.write_('%s requests to adjourn game %d.\n', (user.name, game.number))
            a_sent = user.session.offers_sent
            b_received = self.b.session.offers_received
            a_sent.append(self)
            b_received.append(self)

    def decline(self, notify=True):
        Offer.decline(self, notify)
        self.game.pending_offers.remove(self)

    def accept(self):
        Offer.accept(self)
        self.game.pending_offers.remove(self)
        self.game.adjourn('Game adjourned by agreement')

    def withdraw(self, notify=True):
        Offer.withdraw(self, notify)
        self.game.pending_offers.remove(self)

class Draw(Offer):
    def __init__(self, game, user):
        Offer.__init__(self, 'draw offer')

        self.a = user
        self.b = game.get_opp(user)
        self.game = game
        offers = [o for o in game.pending_offers if o.name == self.name]
        if len(offers) > 1:
            raise RuntimeError('more than one draw offer in game %d' \
                % game.number)
        if len(offers) > 0:
            o = offers[0]
            if o.a == self.a:
                user.write_('You are already offering a draw.\n')
            else:
                o.accept()
        else:
            # check for draw by 50-move rule, repetition
            # The old fics checked for 50-move draw before repetition,
            # and we do the same so the adjudications are identical.
            if game.variant.pos.is_draw_fifty():
                game.result('Game drawn by the 50 move rule', '1/2-1/2')
                return
            elif game.variant.pos.is_draw_repetition(game.get_user_side(
                    self.a)):
                game.result('Game drawn by repetition', '1/2-1/2')
                return

            game.pending_offers.append(self)
            user.write_('Offering a draw to %s.\n', (self.b.name,))
            self.b.write_('%s offers a draw.\n', (user.name,))
            for p in self.game.observers:
                p.write_('%s offers a draw.\n', (user.name,))

            a_sent = user.session.offers_sent
            b_received = self.b.session.offers_received
            a_sent.append(self)
            b_received.append(self)

    def accept(self):
        Offer.accept(self)
        self.game.pending_offers.remove(self)
        self.game.result('Game drawn by agreement', '1/2-1/2')

    def decline(self, notify=True):
        Offer.decline(self, notify)
        self.game.pending_offers.remove(self)

    def withdraw(self, notify=True):
        if notify:
            self.a.write(_('You cannot withdraw a draw offer.\n'))

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

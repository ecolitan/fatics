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

from offer import Offer

partners = []

class Partner(Offer):
    def __init__(self, a, b):
        Offer.__init__(self, 'partnership request')

        # check for existing offers
        a_sent = a.session.offers_sent
        b_sent = b.session.offers_sent
        o = next((o for o in b_sent if o.name == self.name and
            o.b == a), None)
        if o:
            # offers intercept
            o.accept()
            return
        o = next((o for o in a_sent if o.name == self.name and
            o.b == b), None)
        if o:
            a.write(_("You are already offering to be %s's partner.\n") %
                b.name)
            return

        self.a = a
        self.b = b
        a.write(_('Making a partnership offer to %s.\n') % b.name)
        b.write_('%s offers to be your bughouse partner.\n', (a.name,))
        self._register()

    def accept(self):
        Offer.accept(self)
        self.a.write_("You agree to be %s's partner.\n", (self.b.name,))
        self.b.write_("%s agrees to be your partner.\n", (self.a.name,))
        self.a.session.partner = self.b
        self.b.session.partner = self.a
        partners.append(set([self.a, self.b]))

    def withdraw_logout(self):
        Offer.withdraw_logout(self)
        self.a.write_('Partnership offer to %s withdrawn.\n', (self.b.name,))
        self.b.write_('%s, who was offering a partnership with you, has departed.\n',
            (self.a.name,))

    def decline_logout(self):
        Offer.decline_logout(self)
        self.a.write_('%s, whom you were offering a partnership with, has departed.\n', (self.b.name,))
        self.b.write_('Partnership offer from %s removed.\n', (self.a.name,))

def end_partnership(p1, p2):
    assert(p1.session.partner == p2)
    assert(p2.session.partner == p1)
    p1.write_('You no longer have a bughouse partner.\n')
    p2.write_('You no longer have a bughouse partner.\n')
    p1.session.partner = None
    p2.session.partner = None

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

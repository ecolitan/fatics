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

import connection

from online import online
from db import db

def notify_users(user, arrived):
    """ Send a message to all users notified about the given user. """

    assert(not user.is_guest)
    name = user.name
    # notify of adjourned games
    adjourned_opps = []
    if arrived:
        for adj in db.get_adjourned(user.id):
            if adj['white_user_id'] == user.id:
                opp_name = adj['black_name']
            else:
                assert(adj['black_user_id'] == user.id)
                opp_name = adj['white_name']
            assert(opp_name)
            opp = online.find_exact(opp_name)
            if opp:
                opp.write_('\nNotification: %s, who has an adjourned game with you, has arrived.\n', (name,))
                adjourned_opps.append(opp_name)
        if adjourned_opps:
            user.nwrite_('%d player who has an adjourned game with you is online: %s\n',
            '%d players who have an adjourned game with you are online: %s\n',
            len(adjourned_opps), (len(adjourned_opps), ' '.join(adjourned_opps)))

    nlist = []
    for nname in user.notified:
        u = online.find_exact(nname)
        if u:
            if arrived:
                if u.name not in adjourned_opps:
                    u.write_("\nNotification: %s has arrived.\n", name)
                    nlist.append(u.name)
            else:
                u.write_("\nNotification: %s has departed.\n", name)
                nlist.append(u.name)

    if nlist and user.vars['notifiedby']:
        if arrived:
            user.write(_('The following players were notified of your arrival: %s\n') % ' '.join(nlist))
        else:
            user.write(_('The following players were notified of your departure: %s\n') % ' '.join(nlist))

    for nname in user.notifiers:
        u = online.find_exact(nname)
        if u and u.vars['notifiedby']:
            if arrived:
                u.write_("\nNotification: %s has arrived and isn't on your notify list.\n", name)
            else:
                u.write_("\nNotification: %s has departed and isn't on your notify list.\n", name)

def notify_pin(user, arrived):
    """ Notify users who have the pin variable or ivariable set. """
    if online.pin_ivar:
        if arrived:
            pin_ivar_str = '\n<wa> %s 011106 0P0P0P0P0P0P0P0P\n' % user.name
            #pin_ivar_str = '\n<wa> %s 001222 1326P1169P0P0P0P0P0P0P\n' % user.name
        else:
            pin_ivar_str = '\n<wd> %s\n' % user.name
        for u in online.pin_ivar:
            u.write_nowrap(pin_ivar_str)
            connection.written_users.add(u)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

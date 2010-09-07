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

from online import online

def notify_users(user, arrived):
    """ Send a message to all users notified about the given user. """
    name = user.name
    nots = user.notifiers
    nlist = []
    for u in online:
        if name in u.notifiers:
            if arrived:
                u.write_("Notification: %s has arrived.\n", name)
                nlist.append(u.name)
            else:
                u.write_("Notification: %s has departed.\n", name)
                nlist.append(u.name)
        elif u.name in nots and u.vars['notifiedby']:
            if arrived:
                u.write_("Notification: %s has arrived and isn't on your notify list.\n", name)
            else:
                u.write_("Notification: %s has departed and isn't on your notify list.\n", name)

    if nlist and user.vars['notifiedby']:
        if arrived:
            user.write(_('The following players were notified of your arrival: %s\n') % ' '.join(nlist))
        else:
            user.write(_('The following players were notified of your departure: %s\n') % ' '.join(nlist))



# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

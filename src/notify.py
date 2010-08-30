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

class Notify(object):
    """Send a message to all users notified about the given user."""
    def users(self, user, msg):
        name = user.name
        for u in online:
            if name in u.notifiers:
                u.write(msg)
notify = Notify()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

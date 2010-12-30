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

import datetime
import pytz
import time

import time_format

from command import ics_command, Command

from server import server

@ics_command('date', '')
class Date(Command):
    def run(self, args, conn):
        dt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        conn.write(_("Local time     - %s\n") %
            dt.astimezone(conn.user.tz).strftime('%a %b %e, %H:%M %Z %Y'))
        conn.write(_("Server time    - %s\n") %
            dt.strftime("%a %b %e, %H:%M %Z %Y"))
        # same as above, just included in case scripts parse it
        #conn.write(_("GMT            - %s\n") %
        #    dt.strftime("%a %b %e, %H:%M GMT %Y"))

@ics_command('uptime', '')
class Uptime(Command):
    def run(self, args, conn):
        conn.write(_("FatICS version : %s\n") % server.version)
        conn.write(_("Server location: %s\n" % server.location))
        conn.write(_("The server has been up since %s.\n")
            % time.strftime("%a %b %e, %H:%M UTC %Y", time.gmtime(server.start_time)))
        conn.write(_("Up for: %s\n") % time_format.hms_words(time.time() -
            server.start_time))

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

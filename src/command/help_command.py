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

import os.path
import re

from command import ics_command, Command, command_list
from server import server

import admin

# New help file system ~ilknight - 8-5-2011
@ics_command('help', 'o', admin.Level.user)
class Help(Command):
    def run(self, args, conn):
        # for legal reasons, the license help file should be in the code
        # and not in a separate file
        if args[0] in ['license', 'license', 'copying', 'copyright']:
            conn.write(server.get_license())
            return

        # Create list for all commands. If user is not admin, populate only with
        # regular user commands. If user is admin, populate with all commands.
        if conn.user.admin_level > admin.level.user:
            help_cmds = [c.name for c in command_list.admin_cmds.itervalues()]
        else:
            help_cmds = [c.name for c in command_list.cmds.itervalues()]

        if not args[0]:
            # TODO: some help text for "help" with no arguments
            args[0] = 'help'

        # Search for actual .txt help file and return text inside that file
        help_file = 'help/%s.txt' % args[0]
        if args[0] in help_cmds and os.path.exists(help_file):
            # security safeguard
            assert(re.match('[a-z]+', args[0]))
            help_file = open(help_file, "r")
            conn.write((_('Help file documentation for "%s":\n\n') % args[0])
                + help_file.read())
        else:
            conn.write(_('There is no help available for "%s".')
                % args[0])

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

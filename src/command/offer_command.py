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

from command import *

@ics_command('accept', 'n', admin.Level.user)
class Accept(Command):
    def run(self, args, conn):
        if not conn.user.session.offers_received:
            conn.write(_('You have no pending offers from other players.\n'))
            return
        if args[0] is None:
            if len(conn.user.session.offers_received) > 1:
                conn.write(_('You have more than one pending offer. Use "pending" to see them and "accept n" to choose one.\n'))
                return
            conn.user.session.offers_received[0].accept()
        else:
            conn.write('TODO: ACCEPT PARAM\n')

@ics_command('decline', 'n', admin.Level.user)
class Decline(Command):
    def run(self, args, conn):
        if len(conn.user.session.offers_received) == 0:
            conn.write(_('You have no pending offers from other players.\n'))
            return
        if args[0] is None:
            if len(conn.user.session.offers_received) > 1 and args[0] is None:
                conn.write(_('You have more than one pending offer. Use "pending" to see them and "decline n" to choose one.\n'))
                return
            conn.user.session.offers_received[0].decline()
        else:
            conn.write('TODO: DECLINE PARAM\n')

@ics_command('withdraw', 'n', admin.Level.user)
class Withdraw(Command):
    def run(self, args, conn):
        if len(conn.user.session.offers_sent) == 0:
            conn.write(_('You have no pending offers to other players.\n'))
            return
        if args[0] is None:
            if len(conn.user.session.offers_sent) > 1:
                conn.write(_('You have more than one pending offer. Use "pending" to see them and "withdraw n" to choose one.\n'))
                return
            conn.user.session.offers_sent[0].withdraw()
        else:
            conn.write('TODO: WITHDRAW PARAM\n')

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

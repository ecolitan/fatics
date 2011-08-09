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

# Implementation of botless tournaments on FatICS ~ilknight
# Tournament commands here in this file
import tourney
import user

from command import *

@ics_command('tourneylist', '', admin.Level.user)
class Tourneylist(Command):
    def run(self, args, conn):
        if conn.user.is_guest:
            conn.write("Only registered players may use tourney commands.")
            return
        conn.write('Current Tournaments :\n')
        conn.write('ID   Tourney             Manager        |\n')
        conn.write('-----------------------------------------\n')
        for t in tourney.tourneys:
            conn.write('%-20s %-12s %s\n' %
                (tourney.tourneys.index(t), t.name, tourney.managers[tourney.tourneys.index(t)]))
        conn.write(ngettext('\n\nFound %d tournament.\n',
            '\n\nFound %d tournaments.\n', len(tourney.tourneys)) % len(tourney.tourneys))
        
@ics_command('createtourney', '', admin.Level.user)
class Createtourney(Command):
    def run(self, args, conn):
        if not conn.user.has_title('TM'):
            conn.write("You are not a tournament manager (TM).")
            return
        tourney.tourneys[tourney.assign_number()] = tourney.Tournament()
        conn.write("New tournament created with ID %d." % len(tourney.tourneys))

##@ics_command('settourneyname', 'dS', admin.Level.user)
##class Settourneyname(Command):
##    def run(self, args, conn):
##        number = args[0]
##        name = args[1]
##        tournament = tourney.tourneys.
##        if not conn.user.has_title('TM'):
##            conn.write("You are not a tournament manager (TM).")
##            return
        
        

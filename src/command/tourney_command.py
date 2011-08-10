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

@ics_command('listtourneys', '', admin.Level.user)
class Listtourneys(Command):
    def run(self, args, conn):
        if conn.user.is_guest:
            conn.write("Only registered players may use tourney commands.")
            return
        conn.write(' -----------------------------------------------------------------------\n')
        conn.write('| Current Tournaments                                                   |\n')
        conn.write('|-----------------------------------------------------------------------|\n')
        conn.write('| ID  | Tourney Name                | T.Ctrl. | Pair. | Manager         |\n')
        conn.write('|-----------------------------------------------------------------------|\n')
        for t in tourney.tourneys:
            conn.write('| %-4d| %-28s| %-8s| %-6s| %-16s|\n' %
                (t.number, t.name, t.time_control, t.pairing_method, t.manager))
        conn.write(' -----------------------------------------------------------------------\n')
        conn.write(ngettext('\n\nFound %d tournament.\n',
            '\n\nFound %d tournaments.\n', len(tourney.tourneys)) % len(tourney.tourneys))
        
@ics_command('createtourney', '', admin.Level.user)
class Createtourney(Command):
    def run(self, args, conn):
        if not conn.user.has_title('TM'):
            conn.write("You are not a tournament manager (TM).\n")
            return
        tourney.new_tournament(tourney.Tournament())
        tournament = tourney.tourneys[-1]
        number = tourney.tourneys.index(tournament)
        tournament.manager = conn.user.name
        conn.write("New tournament created with ID %d.\n" % number)

@ics_command('jointourney', 'd', admin.Level.user)
class Jointourney(Command):
    def run(self, args, conn):
        number = int(args[0])
        if number >= len(tourney.tourneys):
            conn.write('Tourney number %d not found.\n' % number)
            return
        tourney.tourneys[number].players.append(conn.user.name)
        tourney.tourneys[number].player_scores[conn.user.name] = 0
        time_control = tourney.tourneys[number].time_control.split(" ")
        time_minute = int(time_control[0])
        time_second = int(time_control[1])
        # no variants yet
        if time_minute > 10:
            tourney.tourneys[number].player_ratings[conn.user.name] = conn.user.get_rating('standard')
        elif time_minute > 2:
            tourney.tourneys[number].player_ratings[conn.user.name] = conn.user.get_rating('blitz')
        elif time_minute <= 2:
            tourney.tourneys[number].player_ratings[conn.user.name] = conn.user.get_rating('lightning')
        tourney.tourneys[number].players_in.append(conn.user.name)
        conn.write("You have successfully joined tournament number %d!\n" % number)
        tourney.tourneys[number].announce("%s(%d) has joined tournament #%d" %
            (conn.user.name, tourney.tourneys[number].player_ratings[conn.user.name], number))
        return
                
@ics_command('setpairingmethod', 'dw', admin.Level.user)
class Setpairingmethod(Command):
    def run(self, args, conn):
        number = args[0]
        method = args[1]
        if not conn.user.has_title('TM'):
            conn.write("You are not a tournament manager (TM).\n")
            return
        if number >= len(tourney.tourneys):
            conn.write('Tourney number %d not found.\n' % number)
            return
        if not method in ('ss', 'rr', 'ko'):
            conn.write('"%s" is not a valid pairing method\n' % method)
            return
        tourney.tourneys[number].pairing_method = method

@ics_command('settimecontrol', 'dS', admin.Level.user)
class Settimecontrol(Command):
    def run(self, args, conn):
        number = args[0]
        time_control = args[1]
        if not conn.user.has_title('TM'):
            conn.write("You are not a tournament manager (TM).\n")
            return
        if number >= len(tourney.tourneys):
            conn.write('Tourney number %d not found.\n' % number)
            return
        if not len(time_control.split(" ")) == 2:
            conn.write('That is not a valid time control.')
        tourney.tourneys[number].time_control = time_control
        conn.write('Time control of tourney number %d changed to "%s".\n' % (number, time_control))

@ics_command('settourneyname', 'dS', admin.Level.user)
class Settourneyname(Command):
    def run(self, args, conn):
        number = args[0]
        name = args[1]
        if not conn.user.has_title('TM'):
            conn.write("You are not a tournament manager (TM).\n")
            return
        if number >= len(tourney.tourneys):
            conn.write('Tourney number %d not found.\n' % number)
            return    
        tourney.tourneys[number].name = name
        conn.write('Name of tourney number %d changed to "%s".\n' % (number, name))  
        

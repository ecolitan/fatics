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
import speed_variant
import tourney
import user

from command import *

@ics_command('listtourneys', '', admin.Level.user)
class Listtourneys(Command):
    def run(self, args, conn):
        if conn.user.is_guest:
            conn.write("Only registered players may use tourney commands.")
            return
        conn.write('+-----------------------------------------------------------------------+\n')
        conn.write('| Current Tournaments                                                   |\n')
        conn.write('+-----------------------------------------------------------------------+\n')
        conn.write('| ID  | Tourney Name                | T.Ctrl. | Pair. | Manager         |\n')
        conn.write('+-----------------------------------------------------------------------+\n')
        for t in tourney.tourneys:
            conn.write('| %-4d| %-28s| %-8s| %-6s| %-16s|\n' %
                (t.number, t.name, t.time_control, t.pairing_method, t.manager))
        conn.write('+-----------------------------------------------------------------------+\n')
        conn.write(ngettext('\nFound %d tournament.\n',
            '\nFound %d tournaments.\n', len(tourney.tourneys)) % len(tourney.tourneys))
        
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

@ics_command('deletetourney', 'd', admin.Level.user)
class Deletetourney(Command):
    def run(self, args, conn):
        number = args[0]
        if not conn.user.has_title('TM'):
            conn.write("You are not a tournament manager (TM).\n")
            return
        if number >= len(tourney.tourneys):
            conn.write('Tourney number %d not found.\n' % number)
            return
        tourney.tourneys[number].announce('Tournament deleted by %s!' % conn.user.name)
        tourney.remove_tournament_number(number)
        conn.write('Tournament #%d deleted.\n' % number)
        

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
            tourney.tourneys[number].player_ratings[conn.user.name] = conn.user.get_rating(
                speed_variant.standard_chess)
        elif time_minute > 2:
            tourney.tourneys[number].player_ratings[conn.user.name] = conn.user.get_rating(
                speed_variant.blitz_chess)
        elif time_minute <= 2:
            tourney.tourneys[number].player_ratings[conn.user.name] = conn.user.get_rating(
                speed_variant.lightning_chess)
        if conn.user.name in tourney.tourneys[number].players_in:
            conn.write('You are already in tourney #%d!' % number)
            return
        tourney.tourneys[number].players_in.append(conn.user.name)
        conn.write("You have successfully joined tournament number %d!\n" % number)
        tourney.tourneys[number].announce("%s(%d) has joined tournament #%d!" %
            (conn.user.name, tourney.tourneys[number].player_ratings[conn.user.name], number))
        return

@ics_command('listplayers', 'd', admin.Level.user)
class Listplayers(Command):
    def run(self, args, conn):
        number = args[0]
        if number >= len(tourney.tourneys):
            conn.write('Tourney number %d not found.\n' % number)
            return
        conn.write('+----------------------------------------------------------+\n')
        conn.write('| Player Handle             | Rating | Score | Status      |\n')
        conn.write('+---------------------------+--------+-------+-------------+\n')
        for u in tourney.tourneys[number].players:
            rating = tourney.tourneys[number].player_ratings[u]
            score = tourney.tourneys[number].player_scores[u]
            # get status of player
            if not user.find_by_name_exact(u).is_online:
                status = "Offline"
            elif u in tourney.tourneys[number].players_bye:
                status = "Ready (BYE)"
            elif user.find_by_name_exact(u).session.game:
                status = "Playing"
            else:
                status = "Ready"
            conn.write('| %-26s| %-7s| %-6s| %-12s|\n' % (u, rating, score, status))
        conn.write('+----------------------------------------------------------+\n')

@ics_command('starttourney', 'd', admin.Level.user)
class Starttourney(Command):
    def run(self, args, conn):
        number = args[0]
        if not conn.user.has_title('TM'):
            conn.write("You are not a tournament manager (TM).\n")
            return
        if number >= len(tourney.tourneys):
            conn.write('Tourney number %d not found.\n' % number)
            return
        # check if already started
        if tourney.tourneys[number].started:
            conn.write('Tourney number %d already in progress!\n' % number)
            return
        # check if there's enough players to start
        num_players = len(tourney.tourneys[number].players_in)
        if tourney.tourneys[number].pairing_method.lower() == "ko" or tourney.tourneys[number].pairing_method.lower() == "ss":
            min_players = 8
        elif tourney.tourneys[number].pairing_method.lower() == "rr":
            min_players = 6
        else:
            min_players = 8
        if num_players < min_players:
            conn.write('Too few players to start tourney #%d. Need minimum of %d players\n' % (number, min_players))
            return
        conn.write('Tourney #%d has started!\n')
        tourney.tourneys[number].announce('Tourney starting NOW!!!')
        tourney.tourneys[number].pair()
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
            conn.write('That is not a valid time control.\n')
            return
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
        

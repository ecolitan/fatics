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
# Tournament classes go in this file

import online
import user

# List for tournament storage
tourneys = []
managers = []

def assign_number():
    return len(tourneys)

def new_tournament(t):
    tourneys.append(t)

class Tournament(object):
    def __init__(self):
        # default tournament setup
        self.manager = None
        self.name = "New Tournament"
        self.number = assign_number()
        self.open = False
        self.round = 0
        self.time_control = "5 0"
        self.pairing_method = "SS"
        self.players = []
        self.player_scores = {}
        self.player_ratings = {}
        self.players_in = []
        self.players_bye = []
        self.white_players = []
        self.black_players = []

    def announce(self, message):
        for user_name in self.players_in:
            u = user.find_by_name_exact(user_name)
            if u.is_online:
                u.write(message+"\n")

            # this doesn't look like the right place to announce this -- Wil
            #else:
            #    announce("%s has disconnected." % user.name)

    def increment_round(self):
        self.round = self.round + 1
        # move all players with byes last round into active players
        index = 0
        while (index < len(self.players_bye)):
            self.players_bye.pop[index]
            index = index + 1
        return

    def pair(self):
        self.increment_round()
        # Swiss System
        if self.pairing_method == "SS":
            if self.round == 1:
                sortPlayersByRating()
            else:
                sortPlayersByScore()
            # even number of players
            if len(players_in) % 2 == 1:
                # lowest score - bye
                sortPlayersByScore()
                self.players_bye.append(self.players_in[len(self.players_in)-1])
                self.players_in.pop(len(self.players_in)-1)
            # 1 paired with 5, 2 with 6, 3 with 7, 4 with 8 (8 players)
            differential = len(self.players_in) / 2
            counter = 0
            while (counter < differential):
                if (counter % 2 == 0):
                    self.white_players[counter] = self.players_in[counter]
                    self.black_players[counter] = self.players_in[counter+differential]
                else:
                    self.black_players[counter] = self.players_in[counter]
                    self.white_players[counter] = self.players_in[counter + differential]
                counter = counter + 1
            return
        # Round robin
        elif self.pairing_method == "RR":
            return
        # Knockout
        else:
            sortPlayersByRating()
            player_index_end = len(self.players_in) / 2
            index = 0
            while (index < player_index_end):
                # alternates between black and white
                if (index % 2 == 0):
                    self.white_players[index] = self.players_in[index]
                    self.black_players[index] = self.players_in[len(self.players_in)-1-index]
                else:
                    self.black_players[index] = self.players_in[index]
                    self.white_players[index] = self.players_in[len(self.players_in)-1-index]
                index = index + 1
            announce_str = "  White                   Black\n"
            index = 0
            while (index < (len(self.players_in) / 2)):
                announce_str = announce_str + ('%-19d %s\n' %
                        ((index+1), self.white_players[index], self.black_players[index]))
                index = index + 1
            return

    def removePlayer(self, name):
        if name in self.players_in:
            self.players_in.remove(name)

    def sortPlayersByRating(self):
        self.player_ratings = reversed(sorted(self.player_ratings.values()))
        players_in_idx = 0
        for username in self.player_ratings:
            self.players_in[players_in_idx] = username
            player_in_idx = player_in_idx + 1

    def sortPlayersByScore(self):
        self.player_scores = reversed(sorted(self.player_scores.values()))
        players_in_idx = 0
        for username in self.player_scores:
            self.players_in[players_in_idx] = username
            player_in_idx = player_in_idx + 1

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

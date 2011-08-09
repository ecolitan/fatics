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

class Tournament(object):
    def __init__(self):
        # default tournament setup
        self.number = assign_number()
        self.round = 0
        self.pairing_method = "SS"
        self.players = []
        self.player_scores = {}
        self.player_ratings = {}
        self.players_in = []
        self.white_players = []
        self.black_players = []

    def announce(self, message):
        player_index = 0
        while (player_index < len(self.players_in)):
            user = user.find_by_name_exact(self.players_in[player_index])
            if user in online.online:
                user.write(message+"\n")
            else:
                announce("%s has disconnected." & user.name)

    def changeManager(self, name):
        managers[self.number] = name

    def changeName(self, name):
        tourneys[self.number] = name

    def increment_round(self):
        self.round = self.round + 1
        
    def pair(self):
        self.increment_round()
        # Swiss System
        if self.pairing_method == "SS":
            return
        # Round robin
        elif self.pairing_method == "RR":
            return
        # Knockout
        else:
            if self.round == 1:
                sortPlayersByRating()
            else:
                sortPlayersByScore()
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
                announce_str = announce_str + ('%-19d %-17s %s\n' %
                        ((index+1), self.white_players[index], self.black_players[index]))
                index = index + 1
            return

    def sortPlayersByRating(self):
        self.player_ratings = sorted(self.player_ratings.values())
        players_in_idx = 0
        for username in self.player_ratings:
            self.players_in[players_in_idx] = username
            player_in_idx = player_in_idx + 1

    def sortPlayersByScore(self):
        self.player_scores = sorted(self.player_scores.values())
        players_in_idx = 0
        for username in self.player_scores:
            self.players_in[players_in_idx] = username
            player_in_idx = player_in_idx + 1

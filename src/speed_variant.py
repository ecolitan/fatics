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

from db import db

speed_ids = {}
variant_ids = {}
speed_names = {}
variant_names = {}
variant_abbrevs = {}

class IllegalMoveError(Exception):
    def __init__(self, reason):
        self.reason = reason

class Speed(object):
    def __init__(self, id, name, abbrev):
        self.id = id
        self.name = name
        self.abbrev = abbrev
        speed_ids[id] = self
        speed_names[name] = self

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return self.name

class Variant(object):
    def __init__(self, id, name, abbrev):
        self.id = id
        self.name = name
        self.abbrev = abbrev
        variant_ids[id] = self
        variant_names[name] = self
        variant_abbrevs[abbrev] = self

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return self.name

class SpeedAndVariant(object):
    def __init__(self, speed, variant):
        self.speed = speed
        self.variant = variant

    def __hash__(self):
        return self.speed.id | (self.variant.id << 3)

    def __eq__(self, other):
        return self.speed == other.speed and self.variant == other.variant

    def __str__(self):
        if self.variant.name == 'chess':
            # normal chess is not given explicitly, e.g. "blitz"
            return self.speed.name
        else:
            return '%s %s' % (self.speed.name, self.variant.name)

def init():
    for row in db.get_speeds():
        Speed(row['speed_id'], row['speed_name'], row['speed_abbrev'])
    for row in db.get_variants():
        Variant(row['variant_id'], row['variant_name'], row['variant_abbrev'])
init()

def from_names(speed_name, variant_name):
    return SpeedAndVariant(speed_names[speed_name],
        variant_names[variant_name])

def from_ids(speed_id, variant_id):
    return SpeedAndVariant(speed_ids[speed_id],
        variant_ids[variant_id])

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

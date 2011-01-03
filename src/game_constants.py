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

(WHITE, BLACK) = range(2)
# game types
(EXAMINED, PLAYED) = range(2)

[A8, B8, C8, D8, E8, F8, G8, H8] = range(0x70, 0x78)
[A7, B7, C7, D7, E7, F7, G7, H7] = range(0x60, 0x68)
[A6, B6, C6, D6, E6, F6, G6, H6] = range(0x50, 0x58)
[A5, B5, C5, D5, E5, F5, G5, H5] = range(0x40, 0x48)
[A4, B4, C4, D4, E4, F4, G4, H4] = range(0x30, 0x38)
[A3, B3, C3, D3, E3, F3, G3, H3] = range(0x20, 0x28)
[A2, B2, C2, D2, E2, F2, G2, H2] = range(0x10, 0x18)
[A1, B1, C1, D1, E1, F1, G1, H1] = range(0x00, 0x08)

def opp(side):
    assert(side in [WHITE, BLACK])
    return BLACK if side == WHITE else WHITE

def side_to_str(side):
    assert(side in [WHITE, BLACK])
    return "white" if side == WHITE else "black"

def rank(sq):
    return sq // 0x10

def file(sq):
    return sq % 8

def valid_sq(sq):
    return not (sq & 0x88)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

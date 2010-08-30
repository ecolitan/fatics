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

#!/usr/bin/env python

"""This is a script to read a database of ECO openings in EPD format
and insert into the database in the format the server expects.  The
EPD file I use comes from scid by way of its eco2epd tool. """

import sys
import MySQLdb
import re

import __builtin__
__builtin__.__dict__['N_'] = lambda s: s
__builtin__.__dict__['A_'] = lambda s: s

sys.path.insert(0, 'src/')
import variant.chess

epd_file = 'data/scid.epd'
nic_file = 'data/nic999.idx'

def main():
    db = MySQLdb.connect(host='localhost', db='chess',
        read_default_file="~/.my.cnf")
    cursor = db.cursor()

    f = open(epd_file, 'r')

    cursor.execute("""DELETE FROM eco""")
    count = 0
    txt = None
    for line in f:
        line = line.decode('iso-8859-1').encode('utf-8')
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        m = re.match(r'(.+) +eco +([A-Z]\d\d\S*) +(.+);', line)
        if not m:
            print 'failed to match: %s' % line
        assert(m)
        (fen, eco, long) = (m.group(1), m.group(2), m.group(3))
        pos = variant.chess.Position(fen + ' 0 1')
        cursor.execute("""INSERT INTO eco SET eco=%s, long_=%s, hash=%s, fen=%s""",
            (eco,long,pos.hash,fen))
        count += 1
    print 'imported %d eco codes' % count

    cursor.execute("""DELETE FROM nic""")
    count = 0
    f = open(nic_file, 'r')
    fen = None
    for line in f:
        line = line.strip()
        if fen is None:
            assert(re.match(r'\S+ \S+ \S+ \S+', line))
            fen = line
        else:
            nic = line
            m = re.match(r'([A-Z][A-Z]\.\d\d)\*?', line) 
            if not m:
                raise RuntimeError('failed to match %s', line)
            nic = m.group(1)
            pos = variant.chess.Position(fen + ' 0 1')
            try:
                cursor.execute("""INSERT INTO nic SET nic=%s, hash=%s, fen=%s""",
                    (nic,pos.hash,fen))
            except:
                print 'dupe for %s' % nic
                raise
            count += 1
            fen = None
    print 'imported %d nic codes' % count
    
if __name__ == "__main__":
    main()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

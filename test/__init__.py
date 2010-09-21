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

import sys
from test import connect, admin_passwd

def check_server():
    t = connect()
    if not t:
        print 'ERROR: Unable to connect.  A running server is required to do the tests.\r\n'
        sys.exit(1)

    # remove players possibly left over from an old run
    remove_list = ['testplayer', 'testtwo', 'admintwo']
    t.write('admin\n')
    t.write('%s\n' % admin_passwd)
    for r in remove_list:
        t.write('remplayer %s\n' % r)
    t.write('aclearhist admin\n')
    t.close()

check_server()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

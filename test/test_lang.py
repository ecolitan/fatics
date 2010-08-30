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

from test import *

class TestLang(Test):
    def test_lang_guest(self):
        t = self.connect_as_guest()
        t.write("who\n")
        self.expect("1 player displayed", t)
        
        t.write('set lang arst\n')
        self.expect('Bad value', t)

        t.write('set lang compat\n')
        t.write("who\n")
        self.expect("1 Players Displayed.", t)

        self.close(t)
    
    def test_lang_admin(self):
        t = self.connect_as_admin()
        t.write('set lang en\n')
        t.write("who\n")
        self.expect("1 player displayed", t)
        t.write('set lang compat\n')
        self.close(t)

        t = self.connect_as_admin()
        t.write("who\n")
        self.expect("1 Players Displayed.", t)

        t2 = self.connect_as_guest()
        t2.write("who\n")
        self.expect("2 players displayed.", t2)
        self.close(t2)

        t.write('set lang en\n')
        self.close(t)
        
# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

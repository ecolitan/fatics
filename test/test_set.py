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

class TestSet(Test):
    def test_set(self):
        t = self.connect_as_guest()

        # abbreviated var
        t.write("set te 0\n")
        self.expect("You will not hear direct tells from unregistered", t)

        t.write('set t 1\n')
        self.expect("Ambiguous variable", t)

        t.write("set formula\n")
        self.expect("formula unset", t)
        
        t.write("set shout off\n")
        self.expect("You will not hear shouts", t)
        t.write("set shout ON\n")
        self.expect("You will now hear shouts", t)

        self.close(t)

    def test_bad_set(self):
        t = self.connect_as_guest()
        t.write('set too bar\n')
        self.expect("No such variable", t)
        t.write('set shout bar\n')
        self.expect("Bad value given", t)
        self.close(t)

    def test_toggle(self):
        t = self.connect_as_guest()
        t.write('set tell 1\n')
        self.expect("You will now hear", t)
        t.write('set tell\n')
        self.expect("You will not hear", t)
        t.write('set tell\n')
        self.expect("You will now hear", t)
        self.close(t)

    def test_set_persistence(self):
        t = self.connect_as_admin()
        t.write('set shout 0\n')
        t.write('vars\n')
        self.expect('shout=0', t)
        self.close(t)

        t = self.connect_as_admin()
        t.write('vars\n')
        self.expect('shout=0', t)
        t.write('set shout 1\n')
        self.close(t)

        t = self.connect_as_admin()
        t.write('vars\n')
        self.expect('shout=1', t)
        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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

# GuestFXLR (++++) seeking 5 0 unrated blitz m ("play 37" to respond)

class TestSeek(Test):
    def test_seek_guest(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as_guest()

        t.write('seek 3 0\n')
        m = self.expect_re('Your seek has been posted with index (\d+).', t)
        n = int(m.group(1))
        self.expect('GuestABCD(U) (++++) seeking 3 0 unrated blitz ("play %d" to respond)' % n, t2)
        self.expect('(1 player saw the seek.)', t)

        t.write('seek 3 0\n')
        self.expect('You already have an active seek with the same parameters.', t)

        t.write('seek 15+5\n')
        self.expect('Your seek has been posted with index %d.' %
            (n  + 1), t)
        self.expect('GuestABCD(U) (++++) seeking 15 5 unrated standard ("play %d" to respond)' % (n + 1), t2)
        self.expect('(1 player saw the seek.)', t)

        t.write('unseek\n')
        self.expect('Your seeks have been removed.', t)

        self.close(t)
        self.close(t2)

    def test_matching_seek(self):
        t = self.connect_as('GuestABCD', '')
        t2 = self.connect_as('GuestEFGH', '')

        t.write('seek 15+5 bronstein zh\n')
        self.expect('Your seek has been posted with index ', t)
        self.expect('(1 player saw the seek.)', t)
        self.expect('GuestABCD(U) (++++) seeking 15 5 unrated standard crazyhouse bronstein ("play ', t2)

        t2.write('seek 15 5 bronstein crazyhouse\n')
        self.expect('Your seek matches one posted by GuestABCD.', t2)
        self.expect('Your seek matches one posted by GuestEFGH.', t)

        self.expect('Creating:', t)
        self.expect('unrated standard crazyhouse 15 5', t)
        self.expect('Creating:', t2)
        self.expect('unrated standard crazyhouse 15 5', t2)

        self.close(t)
        self.close(t2)

    def test_showownseek(self):
        """ Test the showownseek var and ivar. """
        t = self.connect_as('GuestABCD', '')
        t.write('see 3+0\n')
        self.expect('(0 players saw the seek.)', t)

        t.write('set showownseek 1\n')
        self.expect('You will now see your own seeks.', t)
        t.write('see 4+0\n')
        self.expect('(1 player saw the seek.)', t)

        t.write('iset showownseek 0\n')
        self.expect('showownseek unset.', t)
        t.write('see 5+0\n')
        self.expect('(0 players saw the seek.)', t)

        t.write('unseek\n')
        self.expect('Your seeks have been removed.', t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

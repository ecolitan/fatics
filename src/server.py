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

import time

class Server(object):
    location = "USA"
    version = "0.1"

    def __init__(self):
        self.start_time = time.time()

    def get_copyright_notice(self):
        return """Copyright (C) 2010 Wil Mahan
This server is free software licensed under the GNU Affero General Public
License, version 3 or any later version.  Type "help license" for details.
The source code for the version of the server you are using is
available here: %s

""" % self.get_server_link()


    def get_license(self):
        f = open('COPYING', 'r')
        return 'Copyright(C) 2010 Wil Mahan\n\n%s\nThe source code for the version of the server you are using is available here:\n%s\n\n' % (f.read(), self.get_server_link())

    def get_server_link(self):
        return 'http://bitbucket.org/wmahan/fatics'

server = Server()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

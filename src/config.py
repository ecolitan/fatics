# -*- coding: utf-8 -*-
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

class Config(object):
    port = 5000
    zipseal_port = 5001
    compatibility_port = 5003

    db_host = "localhost"
    db_db = "chess"

    # login timout in seconds
    login_timeout = 30
    min_login_name_len = 3

    # max idle time in seconds
    idle_timeout = 60 * 60

    # limit on number of channels one user can own
    max_channels_owned = 8

    # Silly Babas requires freechess.org to be in the welcome message,
    # so work it into a disclaimer.
    prompt = 'fics% '

config = Config()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

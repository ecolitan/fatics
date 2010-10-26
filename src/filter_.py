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

from netaddr import IPAddress, IPNetwork

import list_

from db import db

def add_filter(pattern, conn):
    # Don't check whether this filter is a subset of any existing filter,
    # because it could be reasonable to block overlapping ranges, such as
    # when expiring filters are implemented.
    try:
        net = IPNetwork(pattern, implicit_prefix=False).cidr
    except:
        raise list_.ListError(A_('Invalid filter pattern.\n'))
    if net in filters:
        raise list_.ListError(_('%s is already on the filter list.\n') % net)
    filters.add(net)
    db.add_filtered_ip(str(net))
    conn.write(_('%s added to the filter list.\n') % net)

def remove_filter(pattern, conn):
    try:
        net = IPNetwork(pattern, implicit_prefix=False).cidr
    except:
        raise list_.ListError(A_('Invalid filter pattern.\n'))
    try:
        filters.remove(net)
    except KeyError:
        raise list_.ListError(_('%s is not on the filter list.\n') % net)
    db.del_filtered_ip(str(net))
    conn.write(_('%s removed from the filter list.\n') % net)

def check_filter(addr):
    ip = IPAddress(addr)
    return any(ip in net for net in filters)

def _init_filters():
    # sanity checks
    IPNetwork('127.0.0.1')
    IPNetwork('127.0.0.1/16')

    global filters
    filters = set([IPNetwork(pat) for pat in db.get_filtered_ips()])
_init_filters()


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

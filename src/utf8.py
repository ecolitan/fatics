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

import re

legal_chars_re = re.compile('''^[\x20-\xfd]*$''')
def check_user_utf8(s):
    ret =  legal_chars_re.match(s)
    if ret:
        try:
            unicode(s, 'utf-8')
        except UnicodeDecodeError:
            ret = False
    return ret

illegal_char_re = re.compile('''[^\x20-\xfd]''')
def utf8_to_ascii(s):
    """ Try to gracefully convert UTF-8 to ASCII.  Non-ASCII chars are
    replaced by '?'. """
    try:
        return unicode(s, 'utf-8').encode('ascii', 'replace')
    except UnicodeDecodeError:
        return re.sub(illegal_char_re, '?', s)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

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

from gettext import ngettext

class Timer(object):
    def hms_words(self, secs):
        secs = int(secs)
        days = int(secs // 86400)
        secs = secs % 86400 #- 86400 * days
        hours = int(secs // 3600)
        secs = secs % 3600 #secs - 3600 * hours
        mins = int(secs // 60)
        secs = secs % 60 #secs - 60 * mins
        ret = ''
        if days != 0:
            ret = ret + ngettext("%d day", "%d days", days) % days + " "
        if days != 0 or hours != 0:
            ret = ret + ngettext("%d hour", "%d hours", hours) % hours + " "
        if days != 0 or hours != 0 or mins != 0:
            ret = ret + ngettext("%d minute", "%d minutes", mins) % mins + " "
        ret = ret + ngettext("%d second", "%d seconds", secs) % secs
        return ret

    def hms(self, secs, user):
        hours = int(secs // 3600)
        secs = secs % 3600
        mins = int(secs // 60)
        secs = secs % 60

        if user.session.ivars['ms']:
            if hours != 0:
                ret = '%d:%02d:%06.3f' % (hours, mins, secs)
            else:
                ret = '%d:%06.3f' % (mins, secs)
        else:
            if hours != 0:
                ret = '%d:%02d:%02d' % (hours, mins, secs)
            else:
                ret = '%d:%02d' % (mins, secs)
        return ret

timer = Timer()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

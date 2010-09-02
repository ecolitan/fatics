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

from command import *

@ics_command('news', 'p', admin.Level.user)
class News(Command):
    def run(self, args, conn):
        if args[0] is not None:
            conn.write('TODO: news #\n')
        else:
            news = db.get_recent_news(is_admin=False)
            if len(news) == 0:
                conn.write(_('There is no news.\n'))
            for item in reversed(news):
                conn.write('%4d (%s) %s\n' % (item['news_id'], item['news_date'], item['news_title']))

@ics_command('cnewsd', 'd', admin.Level.admin)
class Cnewsd(Command):
    def run(self, args, conn):
        pass

@ics_command('cnewse', 'dp', admin.Level.admin)
class Cnewse(Command):
    def run(self, args, conn):
        exp = args[1]
        if exp is None:
            exp = 0
        if exp != 0:
            conn.write(A_('News expiration dates are not currently supported.\n'))
            return
        try:
            db.delete_news(args[0])
        except DeleteError:
            conn.write(A_('News item %d not found.\n') % args[0])
        else:
            conn.write(A_('Deleted news item %d.\n') % args[0])

@ics_command('cnewsf', 'dT', admin.Level.admin)
class Cnewsf(Command):
    def run(self, args, conn):
        pass

@ics_command('cnewsi', 'S', admin.Level.admin)
class Cnewsi(Command):
    def run(self, args, conn):
        if len(args[0]) > 45:
            conn.write(A_('The news title exceeds the 45-character maximum length; not posted.\n'))
            return
        news_id = db.add_news(args[0], conn.user, is_admin=False)
        conn.write(A_('Created news item %d.\n') % news_id)

@ics_command('cnewsp', 'd', admin.Level.admin)
class Cnewsp(Command):
    def run(self, args, conn):
        pass

@ics_command('cnewst', 'dS', admin.Level.admin)
class Cnewst(Command):
    def run(self, args, conn):
        pass

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

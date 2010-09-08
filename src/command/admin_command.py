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

import user
import command_parser

from command import *

@ics_command('aclearhistory', 'w', admin.Level.admin)
class Aclearhistory(Command):
    def run(self, args, conn):
        name = args[0]
        u = user.find.by_name_exact_for_user(name, conn)
        if u:
            # disallow clearing history for higher adminlevels?
            u.clear_history()
            conn.user.write(A_('History of %s cleared.\n') % u.name)

@ics_command('addplayer', 'WWS', admin.Level.admin)
class Addplayer(Command):
    def run(self, args, conn):
        [name, email, real_name] = args
        try:
            u = user.find.by_name_exact(name)
        except user.UsernameException as e:
            conn.write(e.reason + '\n')
        else:
            if u:
                conn.write(A_('A player named %s is already registered.\n') % name)
            else:
                passwd = user.create.passwd()
                user.create.new(name, email, passwd, real_name)
                conn.write(A_('Added: >%s< >%s< >%s< >%s<\n') % (name, real_name, email, passwd))

@ics_command('announce', 'S', admin.Level.admin)
class Announce(Command):
    def run(self, args, conn):
        count = 0
        # the announcement message isn't localized
        for u in online.itervalues():
            if u != conn.user:
                count = count + 1
                u.write("\n\n    **ANNOUNCEMENT** from %s: %s\n\n" % (conn.user.name, args[0]))
        conn.write("(%d) **ANNOUNCEMENT** from %s: %s\n\n" % (count, conn.user.name, args[0]))

@ics_command('annunreg', 'S', admin.Level.admin)
class Annunreg(Command):
    def run(self, args, conn):
        count = 0
        # the announcement message isn't localized
        for u in online.itervalues():
            if u != conn.user and u.is_guest:
                count = count + 1
                u.write("\n\n    **UNREG ANNOUNCEMENT** from %s: %s\n\n" % (conn.user.name, args[0]))
        conn.write("(%d) **UNREG ANNOUNCEMENT** from %s: %s\n\n" % (count, conn.user.name, args[0]))

@ics_command('areload', '', admin.Level.god)
class Areload(Command):
    def run(self, args, conn):
        reload.reload_all(conn)

@ics_command('asetadmin', 'wd', admin.Level.admin)
class Asetadmin(Command):
    def run(self, args, conn):
        [name, level] = args
        u = user.find.by_name_exact_for_user(name, conn)
        if u:
            # Note: it's possible to set the admin level
            # of a guest.
            if not admin.checker.check_user_operation(conn.user, u):
                conn.write(A_('You can only set the adminlevel for players below your adminlevel.\n'))
            elif not admin.checker.check_level(conn.user.admin_level, level):
                conn.write('''You can't promote someone to or above your adminlevel.\n''')
            else:
                u.set_admin_level(level)
                conn.write('''Admin level of %s set to %d.\n''' % (name, level))
                if u.is_online:
                    u.write(A_('''\n\n%s has set your admin level to %d.\n\n''') % (conn.user.name, level))
#Asetadmin('asetadmin', 'wd', admin.Level.admin)

@ics_command('asetpasswd', 'wW', admin.Level.admin)
class Asetpasswd(Command):
    def run(self, args, conn):
        (name, passwd) = args
        u = user.find.by_name_exact_for_user(name, conn)
        if u:
            if u.is_guest:
                conn.write('You cannot set the password of an unregistered player!\n')
            elif not admin.checker.check_user_operation(conn.user, u):
                conn.write('You can only set the password of players below your adminlevel.\n')
            elif not user.is_legal_passwd(passwd):
                conn.write('"%s" is not a valid password.\n' % passwd)
            else:
                u.set_passwd(passwd)
                conn.write('Password of %s changed to %s.\n' % (name, '*' * len(passwd)))
                if u.is_online:
                    u.write_('\n%s has changed your password.\n', (conn.user.name,))

@ics_command('asetrating', 'wwwddfddd', admin.Level.admin)
class Asetrating(Command):
    def run(self, args, conn):
        (name, speed_name, variant_name, urating, rd, volatility, win,
            loss, draw) = args
        u = user.find.by_prefix_for_user(name, conn)
        if not u:
            return
        if u.is_guest:
            conn.write(A_('You cannot set the rating of an unregistered player.\n'))
            return
        try:
            sv = speed_variant.from_names(speed_name, variant_name)
        except KeyError:
            conn.write(A_('Unknown speed and variant "%s %s".\n') %
                (speed_name, variant_name))
            return
        if urating == 0:
            u.del_rating(sv)
            conn.write(A_('Cleared %s %s rating for %s.\n' %
                (speed_name, variant_name, name)))
        else:
            u.set_rating(sv, urating, rd, volatility, win, loss, draw,
                datetime.datetime.utcnow())
            conn.write(A_('Set %s %s rating for %s.\n' %
                (speed_name, variant_name, name)))
        # XXX notify the user?

@ics_command('nuke', 'w', admin.Level.admin)
class Nuke(Command):
    def run(self, args, conn):
        u = user.find.by_name_exact_for_user(args[0], conn)
        if u:
            if not admin.checker.check_user_operation(conn.user, u):
                conn.write("You need a higher adminlevel to nuke %s!\n" % u.name)
            elif not u.is_online:
                conn.write("%s is not logged in.\n"  % u.name)
            else:
                u.write_('\n\n**** You have been kicked out by %s! ****\n\n', (conn.user.name,))
                u.session.conn.loseConnection('nuked')
                conn.write('Nuked: %s\n' % u.name)

@ics_command('pose', 'wS', admin.Level.admin)
class Pose(Command):
    def run(self, args, conn):
        u2 = user.find.by_prefix_for_user(args[0], conn.user,
            online_only=True)
        if u2:
            if not admin.checker.check_user_operation(conn.user, u2):
                conn.write(A_('You can only pose as players below your adminlevel.\n'))
            else:
                conn.write(A_('Command issued as %s.\n') % u2.name)
                u2.write_('%s has issued the following command on your behalf: %s\n', (conn.user.name, args[1]))
                command_parser.parser.parse(args[1], 0.0, u2.session.conn)

@ics_command('remplayer', 'w', admin.Level.admin)
class Remplayer(Command):
    def run(self, args, conn):
        name = args[0]
        u = user.find.by_name_exact_for_user(name, conn)
        if u:
            if not admin.checker.check_user_operation(conn.user, u):
                conn.write(A_('''You can't remove an admin with a level higher than or equal to yourself.\n'''))
            elif u.is_online:
                conn.write(A_("%s is logged in.\n") % u.name)
            else:
                u.remove()
                conn.write(A_("Player %s removed.\n") % name)



# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

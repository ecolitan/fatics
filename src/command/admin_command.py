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

import datetime

import user
import command_parser
import online
import admin
import speed_variant
import list_
from reload import reload

from db import db
from command import Command, ics_command, requires_registration
from config import config

@ics_command('admin', '', admin.Level.admin)
class Admin(Command):
    # requires registration because I did not implement light toggling
    # for guest admins; the concept of a guest admin is a weird case
    @requires_registration
    def run(self, args, conn):
        title_id = list_.lists['admin'].id
        conn.user.toggle_light(title_id)
        # ugly hack
        if '(*)' in conn.user.get_display_name():
            conn.write(A_('Admin mode (*) is now shown.\n'))
        else:
            conn.write(A_('Admin mode (*) is now not shown.\n'))

@ics_command('aclearhistory', 'w', admin.Level.admin)
class Aclearhistory(Command):
    def run(self, args, conn):
        u = user.find_by_name_exact_for_user(args[0], conn)
        if u:
            # disallow clearing history for higher adminlevels?
            u.clear_history()
            conn.user.write(A_('History of %s cleared.\n') % u.name)

@ics_command('addplayer', 'WWS', admin.Level.admin)
class Addplayer(Command):
    def run(self, args, conn):
        [name, email, real_name] = args
        u = user.find_by_name_exact_for_user(name, conn)
        if u:
            conn.write(A_('A player named %s is already registered.\n')
                % u.name)
        else:
            passwd = user.make_passwd()
            user_id = user.add_user(name, email, passwd, real_name)
            #db.add_comment(conn.user.id, user_id,
            #    'Player added by %s using addplayer.' % conn.user.name)
            conn.write(A_('Added: >%s< >%s< >%s< >%s<\n')
                % (name, real_name, email, passwd))

@ics_command('announce', 'S', admin.Level.admin)
class Announce(Command):
    def run(self, args, conn):
        count = 0
        # the announcement message isn't localized
        for u in online.online:
            if u != conn.user:
                count = count + 1
                u.write("\n\n    **ANNOUNCEMENT** from %s: %s\n\n" % (conn.user.name, args[0]))
        conn.write("(%d) **ANNOUNCEMENT** from %s: %s\n\n" % (count, conn.user.name, args[0]))

@ics_command('annunreg', 'S', admin.Level.admin)
class Annunreg(Command):
    def run(self, args, conn):
        count = 0
        # the announcement message isn't localized
        for u in online.online:
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
        u = user.find_by_name_exact_for_user(name, conn)
        if u:
            # Note: it's possible to set the admin level
            # of a guest.
            if u == conn.user:
                conn.write(A_("You can't change your own adminlevel.\n"))
                return
            if not admin.checker.check_user_operation(conn.user, u):
                conn.write(A_('You can only set the adminlevel for players below your adminlevel.\n'))
            elif not admin.checker.check_level(conn.user.admin_level, level):
                conn.write('''You can't promote someone to or above your adminlevel.\n''')
            else:
                u.set_admin_level(level)
                conn.write('''Admin level of %s set to %d.\n''' %
                    (u.name, level))
                if u.is_online:
                    u.write(A_('''\n\n%s has set your admin level to %d.\n\n''') % (conn.user.name, level))

@ics_command('asetmaxplayer', 'p', admin.Level.admin)
class Asetmaxplayer(Command):
    def run(self, args, conn):
        if args[0] is not None:
            # basic sanity checks XXX
            if args[0] < 10 or args[0] > 100000:
                raise BadCommandError
            conn.write(A_("Previously %d total connections allowed....\n")
                % config.maxplayer)
            config.maxplayer = args[0]

        conn.write(A_('There are currently %d regular and %d admin connections available.\n') %
            (config.maxplayer - config.admin_reserve, config.admin_reserve))
        conn.write(A_('Total allowed connections: %d.\n') % config.maxplayer)

@ics_command('asetmaxguest', 'p', admin.Level.admin)
class Asetmaxguest(Command):
    def run(self, args, conn):
        if args[0] is not None:
            if args[0] < 0 or args[0] + config.admin_reserve > config.maxplayer:
                raise BadCommandError
            conn.write(A_("Previously %d guest connections allowed....\n")
                % config.maxguest)
            config.maxguest = args[0]

        conn.write(A_('Allowed guest connections: %d.\n') % config.maxguest)

@ics_command('asetpasswd', 'wW', admin.Level.admin)
class Asetpasswd(Command):
    def run(self, args, conn):
        (name, passwd) = args
        u = user.find_by_name_exact_for_user(name, conn)
        if u:
            if u.is_guest:
                conn.write('You cannot set the password of an unregistered player!\n')
            elif not admin.checker.check_user_operation(conn.user, u):
                conn.write('You can only set the password of players below your adminlevel.\n')
            elif not user.is_legal_passwd(passwd):
                conn.write('"%s" is not a valid password.\n' % passwd)
            else:
                u.set_passwd(passwd)
                conn.write('Password of %s changed to %s.\n' % (u.name, '*' * len(passwd)))
                if u.is_online:
                    u.write_('\n%s has changed your password.\n', (conn.user.name,))

@ics_command('asetrating', 'wwwddfddd', admin.Level.admin)
class Asetrating(Command):
    def run(self, args, conn):
        (name, speed_name, variant_name, urating, rd, volatility, win,
            loss, draw) = args
        u = user.find_by_prefix_for_user(name, conn)
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
                (speed_name, variant_name, u.name)))
        else:
            u.set_rating(sv, urating, rd, volatility, win, loss, draw,
                datetime.datetime.utcnow())
            conn.write(A_('Set %s %s rating for %s.\n' %
                (speed_name, variant_name, u.name)))
        # XXX notify the user?

@ics_command('asetemail', 'ww', admin.Level.admin)
class Asetemail(Command):
    def run(self, args, conn):
        u = user.find_by_prefix_for_user(args[0], conn)
        if u:
            if not admin.checker.check_user_operation(conn.user, u):
                conn.write("You need a higher adminlevel to change the email address of %s.\n" % u.name)
                return
            if u.is_guest:
                conn.write(A_('You can only set the email for registered players.\n'))
                return

            email = args[1]
            if email is None:
                # TODO?
                assert(False)
            else:
                if '@' not in email:
                    conn.write(A_('That does not look like an email address.\n'))
                    return
                old_email = u.email
                u.set_email(email)
                db.add_comment(conn.user.id, u.id,
                    'Changed email address from "%s" to "%s".' % (
                        old_email, email))
                if u.is_online:
                    u.write_('%(aname)s has changed your email address to "%(email)s".\n',
                        {'aname': conn.user.name, 'email': email})
                conn.write(A_('Email address of %(uname)s changed to "%(email)s".\n') %
                    {'uname': u.name, 'email': email})

@ics_command('nuke', 'w', admin.Level.admin)
class Nuke(Command):
    def run(self, args, conn):
        u = user.find_by_name_exact_for_user(args[0], conn)
        if u:
            if not admin.checker.check_user_operation(conn.user, u):
                conn.write("You need a higher adminlevel to nuke %s!\n" % u.name)
            elif not u.is_online:
                conn.write("%s is not logged in.\n"  % u.name)
            else:
                u.write_('\n\n**** You have been kicked out by %s! ****\n\n', (conn.user.name,))
                u.session.conn.loseConnection('nuked')
                if not u.is_guest:
                    db.add_comment(conn.user.id, u.id, 'Nuked.')
                conn.write('Nuked: %s\n' % u.name)

@ics_command('pose', 'wS', admin.Level.admin)
class Pose(Command):
    def run(self, args, conn):
        u2 = user.find_by_prefix_for_user(args[0], conn.user,
            online_only=True)
        if u2:
            if not admin.checker.check_user_operation(conn.user, u2):
                conn.write(A_('You can only pose as players below your adminlevel.\n'))
            else:
                conn.write(A_('Command issued as %s.\n') % u2.name)
                u2.write_('%s has issued the following command on your behalf: %s\n', (conn.user.name, args[1]))
                # XXX set u2.session.timeseal_last_timestamp?
                command_parser.parser.parse(args[1], u2.session.conn)

@ics_command('remplayer', 'w', admin.Level.admin)
class Remplayer(Command):
    def run(self, args, conn):
        u = user.find_by_name_exact_for_user(args[0], conn)
        if u:
            if not admin.checker.check_user_operation(conn.user, u):
                conn.write(A_('''You can't remove an admin with a level higher than or equal to yourself.\n'''))
            elif u.is_online:
                conn.write(A_("%s is logged in.\n") % u.name)
            else:
                u.remove()
                conn.write(A_("Player %s removed.\n") % u.name)

@ics_command('addcomment', 'wS', admin.Level.admin)
class Addcomment(Command):
    def run(self, args, conn):
        u = user.find_by_prefix_for_user(args[0], conn)
        if u:
            if u.is_guest:
                conn.write(A_('Unregistered players cannot have comments.\n'))
            else:
                db.add_comment(conn.user.id, u.id, args[1])
                conn.write(A_('Comment added for %s.\n') % u.name)

@ics_command('showcomment', 'w', admin.Level.admin)
class Showcomment(Command):
    def run(self, args, conn):
        u = user.find_by_prefix_for_user(args[0], conn)
        if u:
            if u.is_guest:
                conn.write(A_('Unregistered players cannot have comments.\n'))
            else:
                comments = db.get_comments(u.id)
                if not comments:
                    conn.write(A_('There are no comments for %s.\n') % u.name)
                else:
                    for c in comments:
                        conn.write(A_('%s at %s: %s\n') % (c['admin_name'], c['when_added'], c['txt']))

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

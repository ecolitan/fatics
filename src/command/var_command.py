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

import var

@ics_command('iset', 'wS', admin.Level.user)
class Iset(Command):
    def run(self, args, conn):
        [name, val] = args
        try:
            v = var.ivars.get(name)
            v.set(conn.user, val)
        except trie.NeedMore as e:
            assert(len(e.matches) >= 2)
            conn.write(_('Ambiguous ivariable "%(ivname)s". Matches: %(matches)s\n') % {'ivname': name, 'matches': ' '.join([v.name for v in e.matches])})
        except KeyError:
            conn.write(_('No such ivariable "%s".\n') % name)
        except var.BadVarError:
            conn.write(_('Bad value given for ivariable "%s".\n') % v.name)

@ics_command('set', 'wT', admin.Level.user)
class Set(Command):
    def run(self, args, conn):
        # val can be None if the user gave no value
        [name, val] = args
        try:
            v = var.vars.get(name)
            v.set(conn.user, val)
        except trie.NeedMore as e:
            assert(len(e.matches) >= 2)
            conn.write(_('Ambiguous variable "%(vname)s". Matches: %(matches)s\n') % {'vname': name, 'matches': ' '.join([v.name for v in e.matches])})
        except KeyError:
            conn.write(_('No such variable "%s".\n') % name)
        except var.BadVarError:
            conn.write(_('Bad value given for variable "%s".\n') % v.name)

@ics_command('ivariables', 'o', admin.Level.user)
class Ivariables(Command):
    def run(self, args, conn):
        if args[0] is None:
            u = conn.user
        else:
            u = user.find.by_prefix_for_user(args[0], conn,
                online_only=True)

        if u:
            conn.write(_("Interface variable settings of %s:\n\n") % u.name)
            for (vname, val) in u.session.ivars.iteritems():
                v = var.ivars[vname]
                if val is not None and v.display_in_vars:
                    conn.write("%s\n" % v.get_display_str(val))
            conn.write("\n")

@ics_command('variables', 'o', admin.Level.user)
class Variables(Command):
    def run(self, args, conn):
        if args[0] is None:
            u = conn.user
        else:
            u = user.find.by_prefix_for_user(args[0], conn)

        if u:
            conn.write(_("Variable settings of %s:\n\n") % u.name)
            for (vname, val) in u.vars.iteritems():
                v = var.vars[vname]
                if val is not None and v.display_in_vars:
                    conn.write("%s\n" % v.get_display_str(val))
            conn.write("\n")

            if u.vars['formula']:
                conn.write('Formula: %s\n' % u.vars['formula'])
            for i in range(1, 10):
                fname = 'f' + str(i)
                if u.vars[fname]:
                    conn.write(' %s: %s\n' % (fname, u.vars[fname]))

@ics_command('style', 'd', admin.Level.user)
class Style(Command):
    def run(self, args, conn):
        #conn.write('Warning: the "style" command is deprecated.  Please use "set style" instead.\n')
        var.vars['style'].set(conn.user, str(args[0]))

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

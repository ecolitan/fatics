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

import copy

import trie
import lang
import formula

from config import config

vars = trie.Trie()
ivars = trie.Trie()
ivar_number = {}

class BadVarError(Exception):
    pass

class Var(object):
    """This class represents the form of a variable but does not hold
    a specific value.  For example, the server has one global instance of
    this class (actually, a subclass of this class) for the "tell" variable,
    not a separate instance for each user."""
    def __init__(self, name, default):
        assert(name == name.lower())
        self.name = name
        self.default = default
        self.db_store = lambda user_id, name, val: None
        self.is_persistent = False
        self.is_formula_or_note = False
        # display in vars output
        self.display_in_vars = True

    def hide_in_vars(self):
        self.display_in_vars = False
        return self

    def add_as_var(self):
        vars[self.name] = self
        self.is_ivar = False
        return self

    def add_as_ivar(self, number): 
        ivars[self.name] = self
        ivar_number[number] = self
        self.is_ivar = True
        return self

    def persist(self):
        """Make a variable persistent with the given key in the
        user table."""
        self.is_persistent = True
        return self

    def set(self, user, val):
        """This checks whether the given value for a var is legal and
        sets a user's value of the var.  Returns the message to display to
        the user. On an error, raises BadVarError."""
        pass

class StringVar(Var):
    def __init__(self, name, default, max_len=1023):
        Var.__init__(self, name, default)
        self.max_len = max_len

    def set(self, user, val):
        if val is not None and len(val) > self.max_len:
            raise BadVarError()
        if self.is_ivar:
            user.session.set_ivar(self, val)
        else:
            user.set_var(self, val)
        if val is None:
            user.write(_('''%s unset.\n''') % self.name)
        else:
            user.write((_('''%(name)s set to "%(val)s".\n''') % {'name': self.name, 'val': val}))

    def get_display_str(self, val):
        return '''%s="%s"''' % (self.name, val)

class PromptVar(StringVar):
    def set(self, user, val):
        if val is not None and len(val) > self.max_len - 1:
            raise BadVarError()
        assert(not self.is_ivar)
        if val is None:
            user.set_var(self, val)
            user.write(_('''%s unset.\n''') % self.name)
        else:
            val += ' '
            user.set_var(self, val)
            user.write((_('''%(name)s set to "%(val)s".\n''') % {'name': self.name, 'val': val}))

class LangVar(StringVar):
    def set(self, user, val):
        if val not in lang.langs:
            raise BadVarError()
        assert(not self.is_ivar)
        user.set_var(self, val)
        # Start using the new language right away.
        lang.langs[val].install(names=['ngettext'])
        user.write(_('''%(name)s set to "%(val)s".\n''') % {'name': self.name, 'val': val})

class FormulaVar(Var):
    max_len = 1023
    def __init__(self, num):
        name = 'formula' if num == 0 else 'f' + str(num)
        super(FormulaVar, self).__init__(name, None)
        self.num = num
        self.display_in_vars = False
        self.is_formula_or_note = True

    def set(self, user, val):
        if val is None:
            user.set_formula(self, val)
            user.write(_('''%s unset.\n''') % self.name)
        else:
            if len(val) > self.max_len:
                raise BadVarError()
            try:
                formula.check_formula(None, val, self.num)
            except formula.FormulaError:
                raise BadVarError()
            user.set_formula(self, val)
            user.write((_('''%(name)s set to "%(val)s".\n''') % {'name': self.name, 'val': val}))

    def get_display_str(self, val):
        return '''%s=%s''' % (self.name, val)

class NoteVar(Var):
    max_len = 1023

    def __init__(self, name, default):
        Var.__init__(self, name, default)
        self.display_in_vars = False # don't display in "vars" output
        self.is_formula_or_note = True

    def set(self, user, val):
        if val is not None and len(val) > self.max_len:
            raise BadVarError()
        user.set_note(self, val)
        if val is None:
            user.write(_('''Note %s unset.\n''') % self.name)
        else:
            user.write((_('''Note %(name)s set: %(val)s\n''') % {'name': self.name, 'val': val}))

"""An integer variable."""
class IntVar(Var):
    def __init__(self, name, default, min=-99999, max=99999):
        Var.__init__(self, name, default)
        self.min = min
        self.max = max

    def set(self, user, val):
        try:
            val = int(val, 10)
        except ValueError:
            raise BadVarError()
        if val < self.min or val > self.max:
            raise BadVarError()
        if self.is_ivar:
            user.session.set_ivar(self, val)
        else:
            user.set_var(self, val)
        user.write(_("%(name)s set to %(val)s.\n") % {'name': self.name, 'val': val})

    def get_display_str(self, val):
        return '''%s=%d''' % (self.name, val)

"""A boolean variable."""
class BoolVar(Var):
    def __init__(self, name, default, on_msg=None, off_msg=None):
        Var.__init__(self, name, default)

        self.on_msg = on_msg
        self.off_msg = off_msg

    def set(self, user, val):
        if val is None:
            # toggle
            if self.is_ivar:
                val = not user.session.ivars[self.name]
            else:
                val = not user.vars[self.name]
        else:
            val = val.lower()
            if val == 'on':
                val = '1'
            elif val == 'off':
                val = '0'
            elif val not in ['0', '1']:
                raise BadVarError()
            val = int(val, 10)
        if self.is_ivar:
            user.session.set_ivar(self, val)
        else:
            user.set_var(self, val)
        if val:
            if self.on_msg is not None:
                user.write(_(self.on_msg))
            else:
                user.write(_(("%s set.\n") % self.name))
        else:
            if self.off_msg is not None:
                user.write(_(self.off_msg))
            else:
                user.write(_("%s unset.\n") % self.name)

    def get_display_str(self, val):
        return '''%s=%d''' % (self.name, int(val))

class VarList(object):
    def __init__(self):
        self.init_vars()
        self.init_ivars()

    def init_vars(self):
        BoolVar("shout", True, N_("You will now hear shouts.\n"), N_("You will not hear shouts.\n")).persist().add_as_var()
        BoolVar("cshout", True, N_("You will now hear cshouts.\n"), N_("You will not hear cshouts.\n")).persist().add_as_var()
        BoolVar("tell", True, N_("You will now hear direct tells from unregistered users.\n"), N_("You will not hear direct tells from unregistered users.\n")).persist().add_as_var()
        BoolVar("ctell", True, N_("You will now hear channel tells from unregistered users.\n"), N_("You will not hear channel tells from unregistered users.\n")).persist().add_as_var()
        BoolVar("chanoff", False, N_("You will not hear channel tells.\n"), N_("You will now hear channel tells.\n")).persist().add_as_var()

        BoolVar("open", True, N_("You are now open to receive match requests.\n"), N_("You are no longer open to receive match requests.\n")).persist().add_as_var()
        BoolVar("silence", False, N_("You will now play games in silence.\n"), N_("You will not play games in silence.\n")).persist().add_as_var()
        BoolVar("bell", True, N_("You will now hear beeps.\n"), N_("You will not hear beeps.\n")).persist().add_as_var()
        BoolVar("autoflag", True, N_("Auto-flagging enabled.\n"), N_("Auto-flagging disabled.\n")).persist().add_as_var()
        BoolVar("ptime", False, N_("Your prompt will now show the time.\n"), N_("Your prompt will now not show the time.\n")).persist().add_as_var()
        BoolVar("kibitz", True, N_("You will now hear kibitzes.\n"), N_("You will not hear kibitzes.\n")).persist().add_as_var()
        BoolVar("notifiedby", True, N_("You will now hear if people notify you, but you don't notify them.\n"), N_("You will not hear if people notify you, but you don't notify them.\n")).persist().add_as_var()
        BoolVar("minmovetime", True, N_("You will request minimum move time when games start.\n"), N_("You will not request minimum move time when games start.\n")).persist().add_as_var()
        BoolVar("noescape", True, N_("You will request noescape when games start..\n"), N_("You will not request noescape when games start.\n")).persist().add_as_var()
        BoolVar("seek", True, N_("You will now see seek ads.\n"), N_("You will not see seek ads.\n")).persist().add_as_var()
        #BoolVar("echo", True, N_("You will not hear communications echoed.\n"), N_("You will now not hear communications echoed.\n")).persist().add_as_var()
        BoolVar("examine", False, N_("You will now enter examine mode after a game.\n"), N_("You will now not enter examine mode after a game.\n")).persist().add_as_var()
        BoolVar("mailmess", False, N_("Your messages will be mailed to you.\n"), N_("Your messages will not be mailed to you.\n")).persist().add_as_var()
        BoolVar("showownseek", False, N_("You will now see your own seeks.\n"), N_("You will not see your own seeks.\n")).persist().add_as_var()

        # non-persistent
        BoolVar("tourney", False, N_("Your tournament variable is now set.\n"), N_("Your tournament variable is no longer set.\n")).add_as_var()

        IntVar("time", 2, min=0).persist().add_as_var()
        IntVar("inc", 12, min=0).persist().add_as_var()
        IntVar("height", 24, min=5).persist().add_as_var()
        IntVar("width", 79, min=32).persist().add_as_var()

        IntVar("style", 12, min=0, max=12).persist().add_as_var()
        IntVar("kiblevel", 0, min=0, max=9999).add_as_var()
        StringVar("interface", None).add_as_var()
        PromptVar("prompt", config.prompt).add_as_var()

        LangVar("lang", "en").persist().add_as_var()

        for i in range(0, 10):
            FormulaVar(i).persist().add_as_var()

        for i in range(1, 11):
            NoteVar(str(i), None).persist().add_as_var()

        self.default_vars = {}
        self.transient_vars = {}
        self.persistent_vars = set()
        for var in vars.itervalues():
            if var.is_persistent:
                self.default_vars[var.name] = var.default
                if not var.is_formula_or_note:
                    self.persistent_vars.add(var.name)
            else:
                self.transient_vars[var.name] = var.default

    def init_ivars(self):
        # "help iv_list" on original FICS has this list
        BoolVar("compressmove", False).add_as_ivar(0)
        BoolVar("audiochat", False).add_as_ivar(1)
        BoolVar("seekremove", False).add_as_ivar(2)
        BoolVar("defprompt", False).add_as_ivar(3)
        BoolVar("lock", False).add_as_ivar(4)
        BoolVar("startpos", False).add_as_ivar(5)
        BoolVar("block", False).add_as_ivar(6)
        BoolVar("gameinfo", False).add_as_ivar(7)
        BoolVar("xdr", False).add_as_ivar(8) # ignored
        BoolVar("pendinfo", False).add_as_ivar(9)
        BoolVar("graph", False).add_as_ivar(10)
        BoolVar("seekinfo", False).add_as_ivar(11)
        BoolVar("extascii", False).add_as_ivar(12)
        BoolVar("nohighlight", False).add_as_ivar(13)
        BoolVar("highlight", False).add_as_ivar(14)
        BoolVar("showserver", False).add_as_ivar(15)
        BoolVar("pin", False).add_as_ivar(16)
        BoolVar("ms", False).add_as_ivar(17)
        BoolVar("pinginfo", False).add_as_ivar(18)
        BoolVar("boardinfo", False).add_as_ivar(19)
        BoolVar("extuserinfo", False).add_as_ivar(20)
        BoolVar("seekca", False).add_as_ivar(21)
        BoolVar("showownseek", True).add_as_ivar(22)
        BoolVar("premove", False).add_as_ivar(23)
        BoolVar("smartmove", False).add_as_ivar(24)
        BoolVar("movecase", False).add_as_ivar(25)
        BoolVar("suicide", False).add_as_ivar(26)
        BoolVar("crazyhouse", False).add_as_ivar(27)
        BoolVar("losers", False).add_as_ivar(28)
        BoolVar("wildcastle", False).add_as_ivar(29)
        BoolVar("fr", False).add_as_ivar(30)
        BoolVar("nowrap", False).add_as_ivar(31)
        BoolVar("allresults", False).add_as_ivar(32)
        BoolVar("obsping", False).add_as_ivar(33) # ignored
        BoolVar("singleboard", False).add_as_ivar(34)

        self.default_ivars = {}
        for ivar in ivars.itervalues():
            self.default_ivars[ivar.name] = ivar.default

    def get_persistent_var_names(self):
        """ For reading a user's vars from the database;
        does not include formula variables. """
        return copy.copy(self.persistent_vars)

    def get_default_vars(self):
        return copy.copy(self.default_vars)

    def get_transient_vars(self):
        return copy.copy(self.transient_vars)

    def get_default_ivars(self):
        return copy.copy(self.default_ivars)

varlist = VarList()


'''
ivars:
allresults atomic audiochat
block boardinfo
compressmove crazyhousea
defprompt
extascii extuserinfo
fr
gameinfo graph
lock losers
nohighlight nowrap
pendinfo pin pinginfo premove
seekca seekinfo seekremove showserver singleboard smartmove startpos suicide
vthighlight
wildcastle
xml ?
'''


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

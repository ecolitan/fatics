import copy

import trie
import lang

vars = trie.Trie()
ivars = trie.Trie()

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
        # display in vars output
        self.display_in_vars = True
        
    def add_as_var(self): 
        vars[self.name] = self
        self.is_ivar = False
        return self
    
    def add_as_ivar(self): 
        ivars[self.name] = self
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
    max_len = 1023
    def set(self, user, val):
        assert(val == None or len(val) <= self.max_len)
        user.set_var(self, val)
        if val == None:
            user.write(_('''%s unset.\n''') % self.name)
        else:
            user.write((_('''%(name)s set to "%(val)s".\n''') % {'name': self.name, 'val': val}))

    def get_display_str(self, val):
        return '''%s="%s"''' % (self.name, val)

class LangVar(Var):
    def set(self, user, val):
        if not val in lang.langs:
            raise BadVarError()
        user.set_var(self, val)
        user.write(_('''%(name)s set to "%(val)s".\n''') % {'name': self.name, 'val': val})

    def get_display_str(self, val):
        return '''%s="%s"''' % (self.name, val)

class FormulaVar(Var):
    max_len = 1023
    def set(self, user, val):
        assert(val == None or len(val) <= self.max_len)
        user.set_formula(self, val)
        if val == None:
            user.write(_('''%s unset.\n''') % self.name)
        else:
            user.write((_('''%(name)s set to "%(val)s".\n''') % {'name': self.name, 'val': val}))

    def get_display_str(self, val):
        return '''%s=%s''' % (self.name, val)

class NoteVar(Var):
    max_len = 1023

    def __init__(self, name, default):
        Var.__init__(self, name, default)
        self.display_in_vars = False # don't display in "vars" output

    def set(self, user, val):
        assert(val == None or len(val) <= self.max_len)
        user.set_note(self, val)
        if val == None:
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
        user.set_var(self, val)
        user.write(_("%(name)s set to %(val)s.\n") % {'name': self.name, 'val': val})
    
    def get_display_str(self, val):
        return '''%s=%d''' % (self.name, val)

"""A boolean variable."""
class BoolVar(Var):
    def __init__(self, name, default, on_msg, off_msg):
        Var.__init__(self, name, default)
        self.on_msg = on_msg
        self.off_msg = off_msg

    def set(self, user, val):
        if val == None:
            # toggle
            if self.is_ivar:
                val = not user.ivars[self.name]
            else:
                val = not user.vars[self.name]
        else:
            if not val in ['0', '1']:
                raise BadVarError()
            val = int(val, 10)
        user.set_var(self, val)
        if val:
            user.write(_(self.on_msg) + '\n')
        else:
            user.write(_(self.off_msg) + '\n')
    
    def get_display_str(self, val):
        return '''%s=%d''' % (self.name, int(val))

class VarList(object):
    def __init__(self):
        self.init_vars()
        self.init_ivars()

    def init_vars(self):
        BoolVar("shout", True, N_("You will now hear shouts."), N_("You will not hear shouts.")).persist().add_as_var()
        BoolVar("cshout", True, N_("You will now hear cshouts."), N_("You will not hear cshouts.")).persist().add_as_var()
        BoolVar("tell", False, N_("You will now hear direct tells from unregistered users."), N_("You will not hear direct tells from unregistered users.")).persist().add_as_var()
        BoolVar("open", True, N_("You are now open to receive match requests."), N_("You are no longer open to receive match requests.")).persist().add_as_var()
        BoolVar("silence", True, N_("You will now play games in silence."), N_("You will not play games in silence.")).persist().add_as_var()
        BoolVar("bell", True, N_("You will now hear beeps."), N_("You will not hear beeps.")).persist().add_as_var()

        IntVar("time", 2, min=0).persist().add_as_var()
        IntVar("inc", 12, min=0).persist().add_as_var()
        
        IntVar("style", 12, min=0, max=12).add_as_var()

        StringVar("interface", None).add_as_var()

        LangVar("lang", "en").persist().add_as_var()

        FormulaVar("formula", None).persist().add_as_var()
        for i in range(1, 10):
            FormulaVar("f%d" % i, None).persist().add_as_var()

        for i in range(1, 11):
            NoteVar(str(i), None).persist().add_as_var()

        self.default_vars = {}
        self.transient_vars = {}
        for var in vars.itervalues():
            if var.is_persistent:
                self.default_vars[var.name] = var.default
            else:
                self.transient_vars[var.name] = var.default

    def init_ivars(self):
        BoolVar("smartmove", False, N_("smartmove set."), N_("smartmove unset.")).add_as_ivar()
        BoolVar("ms", False, N_("ms set."), N_("ms unset.")).add_as_ivar()
        self.default_ivars = {}
        for ivar in ivars.itervalues():
            self.default_ivars[ivar.name] = ivar.default

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
seekca seekinfo seekremove showownseek showserver singleboard smartmove startpos suicide
vthighlight
wildcastle
ms ?
xml ?
'''


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

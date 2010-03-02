import copy
import trie
from db import db

vars = trie.Trie()

"""This class represents the form of a variable but does not hold
a specific value.  For example, the server has one global instance of
this class (actually, a subclass of this class) for the "tell" variable,
not a separate instance for each user."""
class Var(object):
    def __init__(self, name, default):
        assert(name == name.lower())
        self.name = name
        self.default = default
        vars[self.name] = self
        self.db_store = lambda user_id, name, val: None
        self.is_persistent = False
        # display in vars output
        self.display_in_vars = True

    """Make a variable persistent with the given key in the
    user table."""
    def persist(self):
        self.is_persistent = True

    """This checks whether the given value for a var is legal and
    sets a user's value of the var.  Returns the message to display to
    the user. On an error, raises BadVarError."""
    def set(self, user, val):
        pass

class BadVarError(Exception):
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
        if not val in user.session.conn.factory.langs:
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
    def set(self, user, val):
        try:
            val = int(val, 10)
        except ValueError:
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
        def _(message): return message
        BoolVar("shout", True, _("You will now hear shouts."), _("You will not hear shouts.")).persist()
        BoolVar("tell", False, _("You will now hear direct tells from unregistered users."), _("You will not hear direct tells from unregistered users.")).persist()
        BoolVar("open", True, _("You are now open to receive match requests."), _("You are no longer open to receive match requests.")).persist()
        BoolVar("silence", True, _("You will now play games in silence."), _("You will not play games in silence.")).persist()
        BoolVar("bell", True, _("You will now hear beeps."), _("You will not hear beeps.")).persist()

        IntVar("time", 2).persist()
        IntVar("inc", 12).persist()

        StringVar("interface", None)

        LangVar("lang", "en").persist()

        FormulaVar("formula", None).persist()
        for i in range(1, 10):
            FormulaVar("f%d" % i, None).persist()

        for i in range(1, 11):
            NoteVar(str(i), None).persist()

        self.default_vars = {}
        self.transient_vars = {}
        for var in vars.itervalues():
            if var.is_persistent:
                self.default_vars[var.name] = var.default
            else:
                self.transient_vars[var.name] = var.default

    def get_default_vars(self):
        return copy.copy(self.default_vars)

    def get_transient_vars(self):
        return copy.copy(self.transient_vars)

varlist = VarList()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

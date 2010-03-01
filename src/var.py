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

        """Make a variable persistent with the given key in the
        user table."""
        def persist(self, func=db.user_set_var):
                self.is_persistent = True
                self.db_store = func

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
                        user.write((_('''%s set to "%s".\n''') % (self.name, val)))

"""An integer variable."""
class IntVar(Var):
        def set(self, user, val):
                try:
                        val = int(val, 10)
                except ValueError:
                        raise BadVarError
                user.set_var(self, val)
                user.write(_("%s set to %d.\n") % (self.name, val))

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
                                raise BadVarError
                        val = int(val, 10)
                user.set_var(self, val)
                if val:
                        user.write(self.on_msg + '\n')
                else:
                        user.write(self.off_msg + '\n')

class VarList(object):
        def __init__(self):
                BoolVar("shout", True, _("You will now hear shouts."), _("You will not hear shouts.")).persist()
                BoolVar("tell", False, _("You will now hear direct tells from unregistered users."), _("You will not hear direct tells from unregistered users.")).persist()
                BoolVar("open", True, _("You are now open to receive match requests."), _("You are no longer open to receive match requests.")).persist()
                BoolVar("silence", True, _("You will now play games in silence."), _("You will not play games in silence.")).persist()
                BoolVar("bell", True, _("You will now hear beeps."), _("You will not hear beeps.")).persist()

                IntVar("time", 2).persist()
                IntVar("inc", 12).persist()

                StringVar("interface", None)
                StringVar("formula", None).persist(db.user_set_formula)
                StringVar("1", None).persist(db.user_set_note)

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

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

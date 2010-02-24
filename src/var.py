import copy
import trie

vars = trie.Trie()

class Var(object):
        def __init__(self, name, default):
                assert(name == name.lower())
                self.name = name
                self.dbname = name
                self.default = default
                vars[self.name] = self

class BadVarException(Exception):
        pass
        
class StringVar(Var):
        pass
class IntVar(Var):
        def parse_val(self, val):
                try:
                        ret = int(val, 10)
                except ValueError:
                        raise BadVarException
                return ret
        
        def get_message(self, val):
                return _("%s set to %d.") % (self.name, val)

class BoolVar(Var):
        def __init__(self, name, default, on_msg, off_msg):
                Var.__init__(self, name, default)
                self.on_msg = on_msg
                self.off_msg = off_msg
        
        def parse_val(self, val):
                if not val in ['0', '1']:
                        raise BadVarException
                return int(val, 10)

        def get_message(self, val):
                if val:
                        msg = self.on_msg
                else:
                        msg = self.off_msg
                return msg

class VarList(object):
        def __init__(self):
                BoolVar("shout", True, _("You will now hear shouts."), _("You will not hear shouts."))
                BoolVar("tell", False, _("You will now hear direct tells from unregistered users."), _("You will not hear direct tells from unregistered users."))
                IntVar("time", 2)
                self.default_vars = {}
                for var in vars.itervalues():
                        self.default_vars[var.name] = var.default

        def get_default_vars(self):
                return copy.copy(self.default_vars)

varlist = VarList()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

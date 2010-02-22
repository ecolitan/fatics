import copy
import trie

vars = {}

class Var(object):
        def __init__(self, name, default):
                self.name = name
                self.dbname = name
                self.default = default
                vars[self.name] = self

class BadVarException(Exception):
        pass
        
class StringVar(Var):
        pass
class IntVar(Var):
        pass
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

shout = BoolVar("shout", True, _("You will now hear shouts."), _("You will not hear shouts."))
tell = BoolVar("tell", False, _("You will now hear direct tells from unregistered users."), _("You will not hear direct tells from unregistered users."))

default_vars = {}
for var in vars.values():
        default_vars[var.name] = var.default

def get_default_vars():
        return copy.copy(default_vars)

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

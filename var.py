import copy
import trie

vars = {}

class Var(object):
        def __init__(self, name, default):
                self.name = name
                self.default = default
                vars[self.name] = self

class StringVar(Var):
        pass
class IntVar(Var):
        pass
class BoolVar(Var):
        def __init__(self, name, default, on_msg, off_msg):
                Var.__init__(self, name, default)
                self.on_msg = on_msg
                self.off_msg = off_msg

shout = BoolVar("shout", True, _("You will now hear shouts."), _("You will not hear shouts."))
tell = BoolVar("tell", False, _("You will now hear tells from unregistered users."), _("You will not hear tells from unregistered users."))

default_vars = {}
for var in vars.values():
        default_vars[var.name] = var.default

def get_default_vars():
        return copy.copy(default_vars)

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

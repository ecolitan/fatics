class Variant(object):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name

normal = Variant("normal")

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent


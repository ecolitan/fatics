import normal

class VariantFactory(object):
    def __init__(self):
        self.variants = {'normal': normal.Normal}

    def get(self, name, game):
        return self.variants[name](game)
variant_factory = VariantFactory()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

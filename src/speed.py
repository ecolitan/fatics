class Speed(object):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name

nonstandard = Speed('nonstandard')
lightning = Speed('lightning')
blitz = Speed('blitz')
standard = Speed('standard')
slow = Speed('slow')
correspondence = Speed('correspondence')

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

import trie

#class AmbiguousException(Exception):
#        def __init__(self, matches):
#                self.matches = matches
class Online(object):
        def __init__(self):
                self.online = trie.Trie()

        def add(self, u):
                self.online[u.name.lower()] = u

        def remove(self, u):
                del self.online[u.name.lower()]

        def is_online(self, name):
                return name.lower() in self.online

        def find_exact(self, name):
                name = name.lower()
                try:
                        u = self.online[name]
                except trie.NeedMore:
                        u = None
                except KeyError:
                        u = None
                return u
        
        def find_matching(self, prefix):
                assert(not self.is_online(prefix))
                prefix = prefix.lower()
                try:
                        ulist = self.online.all_children(prefix)
                except KeyError:
                        ulist = []
                return ulist

        def itervalues(self):
                return self.online.itervalues()

online = Online()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

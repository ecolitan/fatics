import re
#import curses.ascii

class Alias(object):
        """Expand system and user aliases in a given command."""
        def expand(self, s, syslist, userlist):
                m = re.match(r'''^([@!#$%^&*\-+'"\/.,]+)(.*)''', s)
                if m:
                        word = m.group(1)
                        rest = m.group(2)
                else:
                        m = re.match(r'^(\S+)(?:\s+(.*))?$', s)
                        if m:
                                word = m.group(1)
                                rest = m.group(2)

                if m:
                        if word in userlist:
                                s = self._expand_params(userlist[word], rest)
                        elif word in syslist:
                                s = self._expand_params(syslist[word], rest)
                return s

        def _expand_params(self, alias_str, rest):
                if '$@' in alias_str:
                        ret = alias_str.replace('$@', rest if rest != None else '')
                elif rest != None:
                        ret = alias_str + ' ' + rest
                else:
                        ret = alias_str
                        
                return ret

alias = Alias()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent

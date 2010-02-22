import re

class Checker:
        def check_user_utf8(self, s):
                return re.match('''^[\t\x20-\xfd]*$''', s)
        
        def check_utf8(self, s):
                return re.match('''^[\a\r\n\t\x20-\xfd]*$''', s)

checker = Checker()


# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

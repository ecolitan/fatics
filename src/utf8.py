import re

class Checker:
        def check_user_utf8(self, s):
                ret =  re.match('''^[\t\x20-\xfd]*$''', s)
                if ret:
                        try:
                                s.decode('utf8')
                        except UnicodeDecodeError:
                                ret = False
                return ret
        
        #def check_utf8(self, s):
        #        return re.match('''^[\a\r\n\t\x20-\xfd]*$''', s)

checker = Checker()


# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

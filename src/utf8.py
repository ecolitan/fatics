import re

class Checker(object):
    legal_chars_re = re.compile('''^[\t\x20-\xfd]*$''')
    def check_user_utf8(self, s):
        ret =  self.legal_chars_re.match(s)
        if ret:
            try:
                s.decode('utf8')
            except UnicodeDecodeError:
                ret = False
        return ret

checker = Checker()


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

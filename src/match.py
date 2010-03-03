import re

class Request(object):
    def __init__(self, a, b, args):
        a.write('Issuing: \n')
        b.write('Challenge: \n')

    def parse_request(s):
        args = re.split(r'\s+', s)





# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

import re
import subprocess

class Timeseal(object):
    _timeseal_pat = re.compile(r'''^(\d+): (.*)\n$''')
    _zipseal_pat = re.compile(r'''^([0-9a-f]+): (.*)\n$''')
    def __init__(self):
        self.timeseal = subprocess.Popen(['timeseal/openseal_decoder'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        self.zipseal = subprocess.Popen(['timeseal/zipseal_decoder'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    def decode_timeseal(self, line):
        self.timeseal.stdin.write(line + '\n')
        dec = self.timeseal.stdout.readline()
        m = self._timeseal_pat.match(dec)
        if not m:
            return (0, None)
        return (int(m.group(1), 10), m.group(2))

    def decode_zipseal(self, line):
        self.zipseal.stdin.write(line + '\n')
        dec = self.zipseal.stdout.readline()
        m = self._zipseal_pat.match(dec)
        if not m:
            return (0, None)
        return (int(m.group(1), 16), m.group(2))
timeseal = Timeseal()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

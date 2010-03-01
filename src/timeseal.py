import re
import subprocess

class Timeseal(object):
    def __init__(self):
        self.timeseal = subprocess.Popen(['timeseal/openseal_decoder'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        self.zipseal = subprocess.Popen(['timeseal/zipseal_decoder'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    def decode_timeseal(self, line):
        self.timeseal.stdin.write(line + '\n')
        dec = self.timeseal.stdout.readline()
        m = re.match(r'''^(\d+): (.*)\n$''', dec)
        if not m:
            return (0, None)
        return (m.group(1), m.group(2))

    def decode_zipseal(self, line):
        self.zipseal.stdin.write(line + '\n')
        dec = self.zipseal.stdout.readline()
        m = re.match(r'''^(\d+): (.*)\n$''', dec)
        if not m:
            return (0, None)
        return (m.group(1), m.group(2))
timeseal = Timeseal()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

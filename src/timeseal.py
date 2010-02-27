import re
import subprocess

class TimesealError(Exception):
        pass

class Timeseal(object):
        def __init__(self):
                self.timeseal = subprocess.Popen(['timeseal/openseal_decoder'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                self.zipseal = subprocess.Popen(['timeseal/zipseal_decoder'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)

        def decode_timeseal(self, line):
                self.timeseal.stdin.write(line + '\n')
                dec = self.timeseal.stdout.readline()
                m = re.match('^(\d+): (.*)\n$', dec)
                if not m:
                        raise TimesealError()
                return (m.group(1), m.group(2))
        
        def decode_zipseal(self, line):
                self.zipseal.stdin.write(line + '\n')
                dec = self.zipseal.stdout.readline()
                m = re.match('^(\d+): (.*)\n$', dec)
                if not m:
                        raise TimesealError()
                return (m.group(1), m.group(2))
timeseal = Timeseal()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

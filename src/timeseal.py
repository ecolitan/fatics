import re
import subprocess

class TimesealException(Exception):
        pass

class Timeseal(object):
        def __init__(self):
                self.process = subprocess.Popen(['timeseal/openseal_decoder'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)

        def decode(self, line):
                self.process.stdin.write(line + '\n')
                dec = self.process.stdout.readline()
                m = re.match('^(\d+): (.*)\n$', dec)
                if not m:
                        raise TimesealException()
                return (m.group(1), m.group(2))
timeseal = Timeseal()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

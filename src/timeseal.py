import re
import subprocess

class Timeseal(object):
    _timeseal_pat = re.compile(r'''^(\d+): (.*)\n$''')
    _zipseal_pat = re.compile(r'''^([0-9a-f]+): (.*)\n$''')
    def __init__(self):
        self.timeseal = subprocess.Popen(['timeseal/openseal_decoder'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        self.zipseal_decoder = subprocess.Popen(['timeseal/zipseal_decoder'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        self.zipseal_encoder = subprocess.Popen(['timeseal/zipseal_encoder'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    def decode_timeseal(self, line):
        self.timeseal.stdin.write(line + '\n')
        dec = self.timeseal.stdout.readline()
        m = self._timeseal_pat.match(dec)
        if not m:
            print 'failed to match: {{%s}}' % dec
            return (0, None)
        return (int(m.group(1), 10), m.group(2))

    def decode_zipseal(self, line):
        self.zipseal_decoder.stdin.write(line + '\n')
        dec = self.zipseal_decoder.stdout.readline()
        m = self._zipseal_pat.match(dec)
        if not m:
            return (0, None)
        return (int(m.group(1), 16), m.group(2))
    
    def compress_zipseal(self, line):
        print('%04x%s' % (len(line),repr(line)))
        self.zipseal_encoder.stdin.write('%04x%s' % (len(line),line))
        count = int(self.zipseal_encoder.stdout.read(4), 16)
        print 'count %d -> %d' % (len(line), count)
        ret = self.zipseal_encoder.stdout.read(count)
        print '1got "%s"\n' % ''.join(['\\x%02x' % ord(c) for c in ret])
        return ret

timeseal = Timeseal()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

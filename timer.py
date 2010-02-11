
class Timer:
        def hms(self, secs):
                days = int(secs / (60*60*24))
                secs = secs - 60*60*24*days
                hours = int(secs / (60*60))
                secs = secs - 60*60*hours
                mins = int(secs / 60)
                secs = secs - 60*mins
                ret = ''
                if days != 0:
                        ret = ret + "%d day%s " % (days, 's' if days != 1 else '')
                if days != 0 or hours != 0:
                        ret = ret + "%d hr%s " % (hours, 's' if hours != 1 else '')
                if days != 0 or hours != 0 or mins != 0:
                        ret = ret + "%d min%s " % (mins, 's' if mins != 1 else '')
                ret = ret + "%d sec%s" % (secs, 's' if secs != 1 else '')
                return ret

timer = Timer()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

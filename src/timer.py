from gettext import ngettext

class Timer(object):
    def hms(self, secs):
        secs = int(secs)
        days = int(secs / (60*60*24))
        secs = secs - 60*60*24*days
        hours = int(secs / (60*60))
        secs = secs - 60*60*hours
        mins = int(secs / 60)
        secs = secs - 60*mins
        ret = ''
        if days != 0:
            ret = ret + ngettext("%d day", "%d days", days) % days + " "
        if days != 0 or hours != 0:
            ret = ret + ngettext("%d hour", "%d hours", hours) % hours + " "
        if days != 0 or hours != 0 or mins != 0:
            ret = ret + ngettext("%d minute", "%d minutes", mins) % mins + " "
        ret = ret + ngettext("%d second", "%d seconds", secs) % secs
        return ret

timer = Timer()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

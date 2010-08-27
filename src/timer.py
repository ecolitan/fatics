from gettext import ngettext

class Timer(object):
    def hms_words(self, secs):
        secs = int(secs)
        days = int(secs // 86400)
        secs = secs % 86400 #- 86400 * days
        hours = int(secs // 3600)
        secs = secs % 3600 #secs - 3600 * hours
        mins = int(secs // 60)
        secs = secs % 60 #secs - 60 * mins
        ret = ''
        if days != 0:
            ret = ret + ngettext("%d day", "%d days", days) % days + " "
        if days != 0 or hours != 0:
            ret = ret + ngettext("%d hour", "%d hours", hours) % hours + " "
        if days != 0 or hours != 0 or mins != 0:
            ret = ret + ngettext("%d minute", "%d minutes", mins) % mins + " "
        ret = ret + ngettext("%d second", "%d seconds", secs) % secs
        return ret

    def hms(self, secs, user):
        hours = int(secs // 3600)
        secs = secs % 3600
        mins = int(secs // 60)
        secs = secs % 60

        if user.session.ivars['ms']:
            if hours != 0:
                ret = '%d:%02d:%06.3f' % (hours, mins, secs)
            else:
                ret = '%d:%06.3f' % (mins, secs)
        else:
            if hours != 0:
                ret = '%d:%02d:%02d' % (hours, mins, secs)
            else:
                ret = '%d:%02d' % (mins, secs)
        return ret

timer = Timer()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

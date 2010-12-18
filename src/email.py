# -*- coding: utf-8 -*-
# Copyright (C) 2010  Wil Mahan <wmahan+fatics@gmail.com>
#
# This file is part of FatICS.
#
# FatICS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FatICS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with FatICS.  If not, see <http://www.gnu.org/licenses/>.
#

import subprocess

SENDMAIL = "/usr/sbin/sendmail"
FROM = "FatICS <noreply@fatics.org>"

class EmailError(Exception):
    def __init__(self, msg):
        self.msg = msg

def send_mail(fr, to, body):
    subject = "FatICS message from %s (Don't reply by email)" % fr.name

    message = """From: %s\nTo: %s <%s>\nSubject: %s\n\n%s""" % (FROM,
        to.name, to.email, subject, body)

    p = subprocess.Popen([SENDMAIL, '-t', '-i'], stdin=subprocess.PIPE)
    p.stdin.write(message)
    p.stdin.close()
    if p.wait() != 0:
        raise EmailError('error sending mail to %s' % to.email)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

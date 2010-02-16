import user

class Login(object):
        # return a user object if one exists; otherwise make a 
        # guest user
        def get_user(self, name, conn):
                if name.lower() == 'g' or name.lower() == 'guest':
                        u = user.GuestUser(None)
                        conn.write(_('\nLogging you in as "%s"; you may use this name to play unrated games.\n(After logging in, do "help register" for more info on how to register.)\n\nPress return to enter as "%s":') % (u.name, u.name))
                else:
                        try:
                                u = user.find.by_name_exact(name)
                        except user.UsernameException as e:
                                conn.write('\n' + e.reason + '\n')
                        else:
                                if u:
                                        if u.is_guest:
                                                # It's theoretically possible that
                                                # a new user registers but is blocked
                                                # from logging in by a guest with the
                                                # same name.  We ignore that case.
                                                conn.write(_('Sorry, %s is already logged in. Try again.\n') % name)
                                                u = None
                                        else:
                                                conn.write(_('\n%s is a registered name.  If it is yours, type the password.\nIf not, just hit return to try another name.\n\npassword: ') % name)
                                else:
                                        u = user.GuestUser(name)
                                        conn.write(_('\n"%s" is not a registered name.  You may play unrated games as a guest.\n(After logging in, do "help register" for more info on how to register.)\n\nPress return to enter as "%s":') % (name, name))
                return u

login = Login()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

class Config(object):
    port = 5001

    db_host = "localhost"
    db_db = "chess"
    db_user = "chess"
    db_passwd = "Luu9yae7"

    login_timeout = 5
    min_login_name_len = 3

    welcome_msg = '''*** Welcome to the Open Internet Chess Server! ***\n\n'''
    login_msg = '''If you are not a registered player, enter the login name "guest".\n\n''' 
    logout_msg = '''*** Thank you for using the Open Internet Chess Server! ***\n'''

config = Config()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

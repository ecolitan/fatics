class Config(object):
    port = 5000

    db_host = "localhost"
    db_db = "chess"

    login_timeout = 30
    min_login_name_len = 3

    # Silly Babas requires freechess.org to be in the welcome message,
    # so work it into a disclaimer.
    welcome_msg = '''*** Welcome to the Open Internet Chess Server! ***\n\nThis server is not affiliated with or endorsed by freechess.org.\n'''
    login_msg = '''If you are not a registered player, enter the login name "guest".\n\n''' 
    logout_msg = '''*** Thank you for using the Open Internet Chess Server! ***\n'''

config = Config()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

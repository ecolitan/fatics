import sys
from test import connect

def check_server():
        t = connect()
        if not t:
                print 'ERROR: Unable to connect.  A running server is required to do the tests.\r\n'
                sys.exit(1)
        t.close()
        
check_server()

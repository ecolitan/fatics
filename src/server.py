import time

class Server(object):
    location = "USA"
    version = "0.1"

    def __init__(self):
        self.start_time = time.time()

server = Server()

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

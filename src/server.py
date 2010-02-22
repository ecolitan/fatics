import time

class Server(object):
        location = "USA"
        version = "0.1"

        def __init__(self):
                self.start_time = time.time()

server = Server()

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

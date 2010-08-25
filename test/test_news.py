from test import *

class TesNews(Test):
    def test_news_guest(self):
        t = self.connect_as_guest()
        t.write("news\n")
        self.expect("There is no news", t)

        t.write("cnewsi test\n")
        self.expect("cnewsi: Command not found", t)

        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

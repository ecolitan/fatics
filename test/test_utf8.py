# coding=utf-8

from test import *

class TestUtf8(Test):
    def test_unprintable(self):
        t = self.connect_as_admin()
        t.write('t admin \x07test\n')
        self.expect("invalid characters", t)

        t.write('fi \xffadmin\n')
        self.expect("invalid characters", t)

        self.close(t)

    def test_utf8(self):
        t = self.connect_as_admin()
        t.write('t admin ¢\n')
        self.expect("tells you: ¢", t)

        t.write('t admin · ¥ £ € $ ¢ ₡ ₢ ₣ ₤ ₥ ₦ ₧ ₨ ₩ ₪ ₫ ₭ ₮  ₯\n')
        self.expect("tells you: · ¥ £ € $ ¢ ₡ ₢ ₣ ₤ ₥ ₦ ₧ ₨ ₩ ₪ ₫ ₭ ₮  ₯", t)

        t.write('t admin ᚠᛇᚻ᛫ᛒᛦᚦ᛫ᚠᚱᚩᚠᚢᚱ᛫ᚠᛁᚱᚪ᛫ᚷᛖᚻᚹᛦᛚᚳᚢᛗ\n')
        self.expect("tells you: ᚠᛇᚻ᛫ᛒᛦᚦ᛫ᚠᚱᚩᚠᚢᚱ᛫ᚠᛁᚱᚪ᛫ᚷᛖᚻᚹᛦᛚᚳᚢᛗ", t)

        self.close(t)

    # test a few languages
    # this isn't meant to be comprehensive
    def test_german(self):
        t = self.connect_as_admin()
        t.write('t admin Im finſteren Jagdſchloß am offenen Felsquellwaſſer patzte der affig-flatterhafte kauzig-höfliche Bäcker über ſeinem verſifften kniffligen C-Xylophon.\n')
        self.expect("tells you: Im finſteren Jagdſchloß am offenen Felsquellwaſſer patzte der affig-flatterhafte kauzig-höfliche Bäcker über ſeinem verſifften kniffligen C-Xylophon", t)

        self.close(t)

    def test_polish(self):
        t = self.connect_as_admin()
        t.write('t admin Pchnąć w tę łódź jeża lub ośm skrzyń fig.\n')
        self.expect("tells you: Pchnąć w tę łódź jeża lub ośm skrzyń fig", t)
        self.close(t)

    def test_russian(self):
        t = self.connect_as_admin()
        t.write('t admin В чащах юга жил-был цитрус? Да, но фальшивый экземпляр! ёъ.\n')
        self.expect("tells you: В чащах юга жил-был цитрус? Да, но фальшивый экземпляр! ёъ", t)
        self.close(t)

    def test_french(self):
        t = self.connect_as_admin()
        t.write('''t admin Les naïfs ægithales hâtifs pondant à Noël où il gèle sont sûrs d'être déçus et de voir leurs drôles d'œufs abîmés.\n''')
        self.expect('''Les naïfs ægithales hâtifs pondant à Noël où il gèle sont sûrs d'être déçus et de voir leurs drôles d'œufs abîmés''', t)
        self.close(t)
    
    def test_other(self):
        t = self.connect_as_admin()
        t.write('t admin ル 東京 й ц у к е н г ш щ з х ъ ф ы в а п р о л д ж э я ч с м и т ь б ю Й Ц У К Е Н Г Ш Щ З Х Ъ Ф Ы В А П Р О Л Д Ж Э Я Ч С М И Т Ь Б Ю\n')
        self.expect('tells you: ル 東京 й ц у к е н г ш щ з х ъ ф ы в а п р о л д ж э я ч с м и т ь б ю Й Ц У К Е Н Г Ш Щ З Х Ъ Ф Ы В А П Р О Л Д Ж Э Я Ч С М И Т Ь Б Ю', t)
        self.close(t)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent

# coding=utf-8

from test import *

class TestUtf8(Test):
	def test_unprintable(self):
		t = self.connect_as_admin()
		t.write('t admin \x07test\n')
                self.expect("unprintable characters", t)
		
                t.write('fi \xffadmin\n')
                self.expect("unprintable characters", t)
                
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


# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python

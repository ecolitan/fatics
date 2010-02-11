--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(32) NOT NULL,
  `user_passwd` char(64) DEFAULT NULL,
  `user_real_name` varchar(64) NOT NULL,
  `user_email` varchar(32) NOT NULL,
  `user_admin_level` smallint(11) unsigned NOT NULL,
  `user_fics_name` varchar(18) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_name` (`user_name`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
-- admin account with password 'admin'
INSERT INTO `user` VALUES (1,'admin','$2a$12$vUOlVpT6HhRBH3hCNrPW8.bqUwEZ/cRzLOOT142vmNYYxhq5bO4Sy','Admin Account','lics@openchess.dyndns.org',1000,NULL);
UNLOCK TABLES;

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
  `user_last_logout` datetime DEFAULT NULL,
  `shout` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'show shouts',
  `tell` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'show tells from guests',
  `time` SMALLINT(4) NOT NULL DEFAULT 2 COMMENT 'default seek time',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_name` (`user_name`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `channel`;
CREATE TABLE `channel` (
  `channel_id` int(11) NOT NULL,
  `name` varchar(32) DEFAULT NULL,
  `descr` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`channel_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `channel_user`;
CREATE TABLE `channel_user` (
  `channel_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  UNIQUE KEY (`user_id`,`channel_id`)
) ENGINE=MyISAM;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
-- admin account with password 'admin'
INSERT INTO `user` VALUES (1,'admin','$2a$12$vUOlVpT6HhRBH3hCNrPW8.bqUwEZ/cRzLOOT142vmNYYxhq5bO4Sy','Admin Account','lics@openchess.dyndns.org',1000,NULL,NULL,1,0,2);
UNLOCK TABLES;

LOCK TABLES `channel` WRITE;
INSERT INTO `channel` VALUES (1,'help','Help for new (and not-so-new) users. :-)');
UNLOCK TABLES;

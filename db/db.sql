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
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_name` (`user_name`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- user variables
DROP TABLE IF EXISTS `var`;
CREATE TABLE `var` (
  `var_id` int(11) NOT NULL,
  `var_name` varchar(16) NOT NULL,
  `var_type` int(11) NOT NULL,
  PRIMARY KEY (`var_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `var_int`;
CREATE TABLE `var_int` (
  `var_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `var_int` int(11) NOT NULL,
  UNIQUE KEY (`var_id`, `user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `var_str`;
CREATE TABLE `var_str` (
  `var_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `var_str` int(11) NOT NULL,
  UNIQUE KEY (`var_id`, `user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
-- admin account with password 'admin'
INSERT INTO `user` VALUES (1,'admin','$2a$12$vUOlVpT6HhRBH3hCNrPW8.bqUwEZ/cRzLOOT142vmNYYxhq5bO4Sy','Admin Account','lics@openchess.dyndns.org',1000,NULL,NULL);
INSERT INTO `user` VALUES (2,'admintw','$2a$12$vUOlVpT6HhRBH3hCNrPW8.bqUwEZ/cRzLOOT142vmNYYxhq5bO4Sy','Admin Account','lics@openchess.dyndns.org',1000,NULL,NULL);
UNLOCK TABLES;

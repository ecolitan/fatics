-- db schema
CREATE TABLE `user` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(32) UNIQUE NOT NULL,
  `user_passwd` char(64),
  `user_real_name` varchar(64) NOT NULL,
  `user_email` varchar(32) NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


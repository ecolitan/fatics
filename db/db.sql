--
-- Table structure for table `user`
--

-- CREATE DATABASE chess;
-- USE chess
-- CREATE USER 'chess'@'localhost' IDENTIFIED BY 'thepassword';
-- GRANT ALL ON chess.* TO 'chess'@'localhost';

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `user_id` int(8) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(32) NOT NULL,
  `user_passwd` char(64) DEFAULT NULL,
  `user_real_name` varchar(64) NOT NULL,
  `user_email` varchar(32) NOT NULL,
  `user_admin_level` smallint(4) unsigned NOT NULL,
  `user_fics_name` varchar(18) DEFAULT NULL,
  `user_last_logout` datetime DEFAULT NULL,

  -- vars
  `time` SMALLINT(4) NOT NULL DEFAULT 2 COMMENT 'default seek time',
  `private` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'private games',
  `shout` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'see shouts',
  `pin` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'notify whenever someone logs on or off',
  `style` SMALLINT(4) NOT NULL DEFAULT 1 COMMENT 'board style',
  `inc` SMALLINT(4) NOT NULL DEFAULT 12 COMMENT 'default increment',
  `jprivate` SMALLINT(4) NOT NULL DEFAULT 0 COMMENT 'private journal',
  `cshout` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'see c-shouts',
  `notifiedby` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'notify when others are notified',
  `flip` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'notify when others are notified',
  -- `rated` OBSOLETE
  `kibitz` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'show kibitzes',
  -- `availinfo`
  `highlight` SMALLINT(4) NOT NULL DEFAULT 0 COMMENT 'terminal highlight style',
  `open` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'open to match requests',
  -- `automail` BOOLEAN NOT NULL DEFAULT 0,
  `kiblevel` SMALLINT(4) NOT NULL DEFAULT 0 COMMENT 'limit kibitzes',
  -- `availmin` SMALLINT(4) NOT NULL DEFAULT 0,
  `bell` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'beep on board updates',
  -- `pgn` BOOLEAN NOT NULL DEFAULT 1,
  `tell` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'show tells from guests',
  -- `availmax` SMALLINT(4) NOT NULL DEFAULT 0,
  `width` SMALLINT(4) NOT NULL DEFAULT 79 COMMENT 'terminal width in characters',
  `bugopen` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'open for bughouse',
  `ctell` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'show channel tells from guests',
  `gin` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'show channel tells from guests',
  
  `height` SMALLINT(4) NOT NULL DEFAULT 24 COMMENT 'terminal height in characters',
  `mailmess` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'email a copy of messages',
  `seek` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'show seeks',
  `ptime` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'show time in prompt',
  `tourney` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'currently in a tourney',
  `messreply` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'send email address in mailed messages',
  `chanoff` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'hide all channel tells',
  `showownseek` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'show own seeks',
  `tzone` varchar(8) NOT NULL DEFAULT 'SERVER' COMMENT 'time zone',
  `provshow` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'show provisional ratings',
  `silence` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'hide shouts and tells while playing',
  `autoflag` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'automatically flag opp',
  `unobserve` TINYINT NOT NULL DEFAULT 0 COMMENT 'automatically unobserve games',
  -- `echo`
  -- `examine` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'automatically examine after a game',
  `minmovetime` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'use minimum move time in games',
  -- `tolerance`
  `noescape` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'agree to forfeit on disconnect',
  `notakeback` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'automatically reject takeback requests',

  -- other flags
  -- `admin_light` BOOLEAN DEFAULT NULL COMMENT 'whether to show the (*) tag',
  `simopen` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'open for simul',
  `lang` VARCHAR(6) NOT NULL DEFAULT 'en' COMMENT 'user language',
  -- not persistent `prompt` varchar(16) NOT NULL DEFAULT 'fics% ' COMMENT 'command prompt',
  `is_abuser` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'is an abuser?',
  `is_banned` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'banned from logging in?',
  -- `is_online` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'logged in?',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_name` (`user_name`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `formula`;
CREATE TABLE formula (
  `formula_id` int(8) NOT NULL AUTO_INCREMENT,
  `user_id` int(8) NOT NULL,
  `num` tinyint(1) NOT NULL COMMENT 'the variable number; formula=0, f1=1',
  `f` VARCHAR(1024) NOT NULL COMMENT 'formula text',
  UNIQUE KEY (`user_id`, `num`),
  PRIMARY KEY (`formula_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `note`;
CREATE TABLE note (
  `note_id` int(8) NOT NULL AUTO_INCREMENT,
  `user_id` int(8) NOT NULL,
  `num` tinyint(1) NOT NULL COMMENT 'the note number',
  `txt` VARCHAR(1024) NOT NULL COMMENT 'note text',
  UNIQUE KEY (`user_id`, `num`),
  PRIMARY KEY (`note_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `channel`;
CREATE TABLE `channel` (
  `channel_id` int(8) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) DEFAULT NULL,
  `descr` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`channel_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `channel_user`;
CREATE TABLE `channel_user` (
  `channel_id` int(8) NOT NULL,
  `user_id` int(8) NOT NULL,
  UNIQUE KEY (`user_id`,`channel_id`)
) ENGINE=MyISAM;

-- titles
DROP TABLE IF EXISTS `title`;
CREATE TABLE `title` (
  `title_id` int(8) NOT NULL AUTO_INCREMENT,
  `title_name` varchar(32) COMMENT 'the corresponding list name',
  `title_descr` varchar(48) NOT NULL COMMENT 'a human-readable description',
  `title_flag` varchar(3) COMMENT 'e.g. * for admins or TM for tourney manager', 
  PRIMARY KEY (`title_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `user_title`;
CREATE TABLE `user_title` (
  `user_id` int(8) NOT NULL,
  `title_id` int(8) NOT NULL,
  `display` BOOLEAN DEFAULT 1 COMMENT 'admin light, tm light, etc.',
  UNIQUE INDEX(`user_id`,`title_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- game
DROP TABLE IF EXISTS `game`;
CREATE TABLE `game` (
  `game_id` int(8) NOT NULL AUTO_INCREMENT,
  `white_id` int(8) NOT NULL,
  `white_rating` smallint(4),
  `black_id` int(8) NOT NULL,
  `black_rating` smallint(4),
  `eco` char(5) NOT NULL,
  `variant` ENUM('normal', 'crazyhouse') NOT NULL,
  `speed` ENUM ('lightning', 'blitz', 'standard', 'slow', 'correspondence')
    NOT NULL,
  `private` BOOLEAN NOT NULL DEFAULT 0,
  `initial_time` int(3),
  `inc` int(3) COMMENT 'increment',
  `result` ENUM('1-0', '0-1', '1/2-1/2', '*') NOT NULL, 
  `rated` BOOLEAN NOT NULL,
  `result_code` ENUM('Adj', 'Agr', 'Dis', 'Fla', 'Mat', 'NM', 'Rep', 'Res',
    'TM', 'WLM', 'WNM', '50') NOT NULL,
  `when_ended` datetime NOT NULL,
  INDEX(`white_id`),
  INDEX(`black_id`),
  INDEX(`when_ended`),
  PRIMARY KEY (`game_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ECO codes
-- use import-eco.py to populate 
DROP TABLE IF EXISTS `eco`;
CREATE TABLE `eco` (
  `eco_id` int(4) NOT NULL AUTO_INCREMENT,
  `eco` char(5) NOT NULL,
  `long_` varchar(128) NOT NULL,
  `hash` bigint(12) UNSIGNED NOT NULL UNIQUE,
  PRIMARY KEY (`eco_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE utf8_bin;

-- notifications
DROP TABLE IF EXISTS `user_notify`;
CREATE TABLE `user_notify` (
  `notified` int(8) NOT NULL COMMENT 'id of the user receiving the notification',
  `notifier` int(8) NOT NULL COMMENT 'id of the user causing the notification',
  UNIQUE INDEX(`notified`, `notifier`)
);

-- censor lists
DROP TABLE IF EXISTS `censor`;
CREATE TABLE censor (
  `censorer` int(8) NOT NULL COMMENT 'id of the censoring user',
  `censored` int(8) NOT NULL COMMENT 'id of the user being censored',
  UNIQUE INDEX(`censorer`, `censored`)
);

-- noplay lists
DROP TABLE IF EXISTS `noplay`;
CREATE TABLE noplay (
  `noplayer` int(8) NOT NULL COMMENT 'id of the noplaying user',
  `noplayed` int(8) NOT NULL COMMENT 'id of the user being noplayed',
  UNIQUE INDEX(`noplayer`, `noplayed`)
);

-- user aliases  
DROP TABLE IF EXISTS `user_alias`;
CREATE TABLE user_alias (
  `alias_id` int(8) NOT NULL AUTO_INCREMENT,
  `user_id` int(8) NOT NULL,
  `name` VARCHAR(16) NOT NULL COMMENT 'alias word',
  `val` VARCHAR(1024) NOT NULL COMMENT 'alias value',
  UNIQUE KEY (`user_id`, `name`),
  PRIMARY KEY (`alias_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- data
LOCK TABLES `user` WRITE;
-- admin account with password 'admin'
INSERT INTO `user` SET user_id=1,user_name='admin',user_passwd='$2a$12$vUOlVpT6HhRBH3hCNrPW8.bqUwEZ/cRzLOOT142vmNYYxhq5bO4Sy',user_real_name='Admin Account',user_email='ics@openchess.dyndns.org',user_admin_level=10000;
UNLOCK TABLES;

LOCK TABLES `channel` WRITE;
INSERT INTO `channel` VALUES (1,'help','Help for new (and not-so-new) users. :-)');
UNLOCK TABLES;

LOCK TABLES `title` WRITE;
INSERT INTO `title` VALUES (NULL,'admin','Administrator','*');
INSERT INTO `title` VALUES (NULL,'CM','Candidate Master','CM');
INSERT INTO `title` VALUES (NULL,'FM','FIDE Master','FM');
INSERT INTO `title` VALUES (NULL,'IM','International Master','IM');
INSERT INTO `title` VALUES (NULL,'GM','Grandmaster','GM');
INSERT INTO `title` VALUES (NULL,'WCM','Woman Candidate Master','WCM');
INSERT INTO `title` VALUES (NULL,'WFM','Woman FIDE Master','WFM');
INSERT INTO `title` VALUES (NULL,'WIM','Woman International Master','WIM');
INSERT INTO `title` VALUES (NULL,'WGM','Woman Grandmaster','WGM');
INSERT INTO `title` VALUES (NULL,'blind','Blind','B');
INSERT INTO `title` VALUES (NULL,'computer','Computer','C');
INSERT INTO `title` VALUES (NULL,'CA','Chess Advisor','CA');
INSERT INTO `title` VALUES (NULL,'TM','Tournament Manager','TM');
INSERT INTO `title` VALUES (NULL,'TD','Technical Device','TD');
INSERT INTO `title` VALUES (NULL,'SR','Service Representative','SR');
UNLOCK TABLES;

LOCK TABLES `user_title` WRITE;
INSERT INTO `user_title` VALUES (1,1,1);
UNLOCK TABLES;


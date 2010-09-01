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
  `user_name` varchar(17) NOT NULL,
  `user_passwd` char(64) DEFAULT NULL,
  `user_real_name` varchar(64) NOT NULL,
  `user_email` varchar(32) NOT NULL,
  `user_admin_level` smallint(4) unsigned NOT NULL,
  `user_fics_name` varchar(18) DEFAULT NULL,
  `user_last_logout` timestamp NULL DEFAULT NULL,

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
  `num` tinyint(1) NOT NULL COMMENT 'note number',
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

-- history
DROP TABLE IF EXISTS `history`;
CREATE TABLE `history` (
  `history_id` int(8) NOT NULL AUTO_INCREMENT,
  `num` tinyint(2) NOT NULL,
  `result_char` enum('+', '-', '=') NOT NULL,
  `user_id` int(8) NOT NULL,
  `user_rating` char(4) NOT NULL,
  `color_char` ENUM('W', 'B') NOT NULL,
  `opp_name` varchar(17) NOT NULL,
  `opp_rating` char(4) NOT NULL,
  `eco` char(5) NOT NULL,
  `flags` char(3) NOT NULL COMMENT 'string describing variant, speed, ratedness, etc.',
  `time` smallint(4) COMMENT 'initial time',
  `inc` smallint(4) COMMENT 'increment',
  `result_reason` ENUM('Adj', 'Agr', 'Dis', 'Fla', 'Mat', 'NM', 'Sta', 'Rep',
     'Res', 'TM', 'WLM', 'WNM', '50') NOT NULL,
  `when_ended` TIMESTAMP NOT NULL,
  `game_id` int(8) NOT NULL COMMENT 'corresponding game entry that has the moves',
  INDEX(`user_id`),
  UNIQUE INDEX(`user_id`, `num`),
  PRIMARY KEY (`history_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- game
DROP TABLE IF EXISTS `game`;
CREATE TABLE `game` (
  `game_id` int(8) NOT NULL AUTO_INCREMENT,
  `white_name` varchar(17) NOT NULL,
  `white_rating` char(4),
  `black_name` varchar(17) NOT NULL,
  `black_rating` char(4),
  `eco` char(5) NOT NULL,
  `speed_id` TINYINT NOT NULL,
  `variant_id` TINYINT NOT NULL,
  -- `private` BOOLEAN NOT NULL DEFAULT 0,
  `time` int(3) COMMENT 'initial time',
  `inc` int(3) COMMENT 'increment',
  `rated` BOOLEAN NOT NULL,
  `result` ENUM('1-0', '0-1', '1/2-1/2', '*') NOT NULL,
  `result_reason` ENUM('Adj', 'Agr', 'Dis', 'Fla', 'Mat', 'NM', 'Rep', 'Sta',
    'Res', 'TM', 'WLM', 'WNM', '50') NOT NULL,
  `ply_count` SMALLINT NOT NULL,
  `movetext` TEXT,
  `when_ended` TIMESTAMP NOT NULL,
  INDEX(`white_name`),
  INDEX(`black_name`),
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
  `fen` varchar(88) NOT NULL UNIQUE COLLATE utf8_bin,
  PRIMARY KEY (`eco_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `nic`;
CREATE TABLE `nic` (
  `nic_id` int(4) NOT NULL AUTO_INCREMENT,
  `nic` char(5) NOT NULL,
  `hash` bigint(12) UNSIGNED NOT NULL UNIQUE,
  `fen` varchar(88) NOT NULL UNIQUE COLLATE utf8_bin,
  PRIMARY KEY (`nic_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

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

-- speeds and variants
DROP TABLE IF EXISTS `speed`;
CREATE TABLE speed (
  `speed_id` int(8) NOT NULL AUTO_INCREMENT,
  `speed_name` varchar(16) NOT NULL,
  `speed_abbrev` char(2) NOT NULL,
  PRIMARY KEY(`speed_id`)
);
DROP TABLE IF EXISTS `variant`;
CREATE TABLE variant (
  `variant_id` int(8) NOT NULL AUTO_INCREMENT,
  `variant_name` varchar(16) NOT NULL,
  `variant_abbrev` char(2) NOT NULL,
  PRIMARY KEY(`variant_id`)
);
-- ratings
DROP TABLE IF EXISTS `rating`;
CREATE TABLE rating (
  `rating_id` int(8) NOT NULL AUTO_INCREMENT, -- is this necessary?
  `user_id` int(8) NOT NULL,
  `variant_id` int(8) NOT NULL,
  `speed_id` int(8) NOT NULL,
  `rating` int(4) NOT NULL,
  `rd` float NOT NULL,
  `volatility` float NOT NULL,
  `win` int(7) NOT NULL,
  `loss` int(7) NOT NULL,
  `draw` int(7) NOT NULL,
  `total` int(7) NOT NULL COMMENT 'equals win + loss + draw, but included for efficiency',
  `best` int(4) COMMENT 'best active rating',
  `when_best` date COMMENT 'when best rating was achieved',
  `ltime` timestamp NOT NULL DEFAULT 0,
  UNIQUE KEY (`user_id`, `variant_id`, `speed_id`),
  INDEX(`user_id`),
  PRIMARY KEY(`rating_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- news
DROP TABLE IF EXISTS `news_index`;
CREATE TABLE news_index (
  `news_id` int(4) NOT NULL AUTO_INCREMENT,
  `news_title` VARCHAR(45) NOT NULL,
  `news_date` date NOT NULL COMMENT 'when posted',
  `news_poster` VARCHAR(17) NOT NULL,
  `news_is_admin` BOOLEAN NOT NULL COMMENT 'normal or admin news item',
  PRIMARY KEY(`news_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `news_line`;
CREATE TABLE news_line (
  `news_id` int(8) NOT NULL,
  `num` tinyint UNSIGNED NOT NULL COMMENT 'line number',
  `txt` VARCHAR(1024) NOT NULL COMMENT 'news line text'
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

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

LOCK TABLES `speed` WRITE;
INSERT INTO `speed` VALUES (NULL,'untimed','?');
INSERT INTO `speed` VALUES (NULL,'lightning','l');
INSERT INTO `speed` VALUES (NULL,'blitz','b');
INSERT INTO `speed` VALUES (NULL,'standard','s');
INSERT INTO `speed` VALUES (NULL,'slow','o');
INSERT INTO `speed` VALUES (NULL,'corr','c');
UNLOCK TABLES;

LOCK TABLES `variant` WRITE;
INSERT INTO `variant` VALUES (NULL,'chess','n');
INSERT INTO `variant` VALUES (NULL,'crazyhouse','z');
UNLOCK TABLES;


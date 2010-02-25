--
-- Table structure for table `user`
--

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
  `examine` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'automatically examine after a game',
  `minmovetime` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'use minimum move time in games',
  -- `tolerance`
  `noescape` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'agree to forfeit on disconnect',
  `notakeback` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'automatically reject takeback requests',

  -- other flags
  `admin_light` BOOLEAN DEFAULT NULL COMMENT 'whether to show the (*) tag',
  `simopen` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'open for simul',
  `lang` VARCHAR(3) NOT NULL DEFAULT 'en' COMMENT 'user language',
  `prompt` varchar(16) NOT NULL DEFAULT 'fics% ' COMMENT 'command prompt',

  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_name` (`user_name`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `formula`;
CREATE TABLE formula (
  `formula_id` int(8) NOT NULL,
  `user_id` int(8) NOT NULL,
  `num` tinyint(1) NOT NULL COMMENT 'the variable number; formula=0, f1=1',
  `f` VARCHAR(1024) NOT NULL COMMENT 'formula text',
  UNIQUE KEY (`user_id`, `num`),
  PRIMARY KEY (`formula_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `note`;
CREATE TABLE note (
  `note_id` int(8) NOT NULL,
  `user_id` int(8) NOT NULL,
  `num` tinyint(1) NOT NULL COMMENT 'the note number',
  `txt` VARCHAR(1024) NOT NULL COMMENT 'note text',
  UNIQUE KEY (`user_id`, `num`),
  PRIMARY KEY (`note_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `channel`;
CREATE TABLE `channel` (
  `channel_id` int(8) NOT NULL,
  `name` varchar(32) DEFAULT NULL,
  `descr` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`channel_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `channel_user`;
CREATE TABLE `channel_user` (
  `channel_id` int(8) NOT NULL,
  `user_id` int(8) NOT NULL,
  UNIQUE KEY (`user_id`,`channel_id`)
) ENGINE=MyISAM;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
-- admin account with password 'admin'
INSERT INTO `user` SET user_id=1,user_name='admin',user_passwd='$2a$12$vUOlVpT6HhRBH3hCNrPW8.bqUwEZ/cRzLOOT142vmNYYxhq5bO4Sy',user_real_name='Admin Account',user_email='lics@openchess.dyndns.org',user_admin_level=1000;
UNLOCK TABLES;

LOCK TABLES `channel` WRITE;
INSERT INTO `channel` VALUES (1,'help','Help for new (and not-so-new) users. :-)');
UNLOCK TABLES;

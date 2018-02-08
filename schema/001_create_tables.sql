CREATE TABLE `tbl_acl` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(200) NOT NULL DEFAULT '' COMMENT '',
  `method` varchar(20) NOT NULL DEFAULT '' COMMENT '',
  `serviceName` varchar(50) NOT NULL DEFAULT '' COMMENT '',
  `aclRules` varchar(50) DEFAULT NULL COMMENT '',
  `remark` text COMMENT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniKey` (`url`,`method`,`serviceName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

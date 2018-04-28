/* insert into tbl_acl */;
INSERT INTO `tbl_acl` (`id`, `url`, `method`, `serviceName`, `aclRules`, `remark`)
VALUES
	(5,'/code','get','api','R1N',''),
	(6,'/token','get','api',NULL,NULL),
	(7,'/example','get','api','R1N',''),
	(8,'/example','post','api','R1N',''),
    (20,'/mobile/rules','get','api','R2N',NULL);
# -------- end
# migralite

migralite is a simple mysql migration tool.

Setup
```
pip install migralite
```

#### Example 1:
```bash
$ tree testsqls
testsqls
├── 001_create.sql
├── 002_insert.sql
└── 003_select.sql

$ migralite -i root@myhost.mysql.rds.aliyuncs.com:3306/dbtest -p PASSWORD ./testsqls

Start Version: 0
MySQLCursor: DROP TABLE IF EXISTS `tbl_python`
[]
MySQLCursor: CREATE TABLE `tbl_python` (
  `id` int(1..
[]
MySQLCursor: INSERT INTO tbl_python VALUES(1, 'abcde'..
[]
MySQLCursor: INSERT INTO tbl_python VALUES(2, 'xyz', ..
[]
MySQLCursor: INSERT INTO tbl_python VALUES(3, 'qqqq',..
[]
MySQLCursor: INSERT INTO tbl_python VALUES(4, 'pppp',..
[]
MySQLCursor: select * from tbl_python
[(1, 'abcde', datetime.datetime(2018, 1, 8, 14, 34, 8)), (2, 'xyz', datetime.datetime(2018, 1, 8, 14, 34, 8)), (3, 'qqqq', datetime.datetime(2018, 1, 8, 14, 34, 8)), (4, 'pppp', datetime.datetime(2018, 1, 8, 14, 34, 8))]
... (total: 4 rows) ...
MySQLCursor: UPDATE _migrate_ SET version=3
[]
---- Migrate Done. ----
```

#### Example 2:
```bash
$ tree .
├── 001_create.sql
├── 002_insert_except_local.sql
└── 003_select_only_local.sql

$ migralite -i myhost.mysql.rds.aliyuncs.com/dbtest -p PASSWORD -e local
Start Version: 0
MySQLCursor: DROP TABLE IF EXISTS `tbl_python`
[]
MySQLCursor: CREATE TABLE `tbl_python` (
  `id` int(1..
[]
MySQLCursor: select * from tbl_python
[]
MySQLCursor: UPDATE _migrate_ SET version=3
[]
---- Migrate Done. ----
```
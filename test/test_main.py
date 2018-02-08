from unittest import TestCase
import os
import mysql.connector
from contextlib import contextmanager


@contextmanager
def connect_db(dbpwd, port, database):
    conn = mysql.connector.connect(user='root', password=dbpwd, host='localhost', port=port, database=database)
    cur = conn.cursor()
    try:
        yield conn, cur
    finally:
        cur.close()
        conn.close()


class TestRun(TestCase):
    def setUp(self):
        os.system("python setup.py install")
        os.system("sh test-deps.sh")

    def test_run(self):
        dburl = 'localhost:31579/testdb'
        dbpwd = 'passwd'

        os.system('cd schema; migralite -i {0} -p {1} -d'.format(dburl, dbpwd))
        with connect_db(dbpwd, 31579, 'testdb') as (conn, cur):
            cur.execute("SELECT version FROM _migrate_ LIMIT 1")
            row = list(cur)
            self.assertTrue(row)
            start_version = row[0][0]
            self.assertEqual(start_version, 2)

            cur.execute("SELECT COUNT(*) FROM tbl_acl")
            row = list(cur)
            count = row[0][0]
            self.assertEqual(count, 5)

        print("********")

        os.system('cd schema; migralite -i {0} -p {1} -d -e test'.format(dburl, dbpwd))
        with connect_db(dbpwd, 31579, 'testdb') as (conn, cur):
            cur.execute("SELECT version FROM _migrate_ LIMIT 1")
            row = list(cur)
            self.assertTrue(row)
            start_version = row[0][0]
            self.assertEqual(start_version, 1)

            cur.execute("SELECT COUNT(*) FROM tbl_acl")
            row = list(cur)
            count = row[0][0]
            self.assertEqual(count, 0)

    def tearDown(self):
        os.system("docker-compose -f docker/testci/docker-compose.yml stop")

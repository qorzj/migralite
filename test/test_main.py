from unittest import TestCase
import os
import mysql.connector

from migralite.main import run


class TestRun(TestCase):
    def setUp(self):
        os.system("sh test-deps.sh")

    def test_run(self):
        dburl = 'localhost:31579/testdb'
        dbpwd = 'passwd'
        run('schema', i=dburl, p=dbpwd, d=True)
        print("********")
        run('schema', i=dburl, p=dbpwd, d=True, e='test')
        conn = mysql.connector.connect(user='root', password=dbpwd, host='localhost', port=31579, database='testdb')
        cur = conn.cursor()
        try:
            cur.execute("SELECT version FROM _migrate_ LIMIT 1")
            row = list(cur)
            self.assertTrue(bool(row))
            start_version = row[0][0]
            self.assertEqual(start_version, 1)

            cur.execute("SELECT COUNT(*) FROM tbl_acl")
            row = list(cur)
            count = row[0][0]
            self.assertEqual(count, 0)
        finally:
            cur.close()
            conn.close()

    def tearDown(self):
        os.system("docker-compose -f docker/testci/docker-compose.yml stop")
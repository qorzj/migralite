import os
import lesscli
import mysql.connector
from mysql.connector.cursor import MySQLCursor

from migralite.utils import fetch_version


def print_help():
    text = """

    migralite [args] sql_dir
        -i    : mysql user@host:port/database, default user is root
        -p    : mysql password

        -t    : version to be updated to, default is the max version
        -e    : current env, default is empty
        -s    : version to be updated from, default is the current version plus 1
        -d    : drop database when setup

        -h    : show help information
    """
    print(text)


def rewrite_by_java(arg_dict, confname):
    url = username = password = ''
    for line in open(confname).read().splitlines():
        if not line or line[0] == '#':
            continue
        if line.startswith('spring.datasource.url='):
            url = line.split(':mysql://', 1)[-1].split('?', 1)[0]
        if line.startswith('spring.datasource.hikari.username='):
            username = line.split('=', 1)[-1]
        if line.startswith('spring.datasource.hikari.password='):
            password = line.split('=', 1)[-1]

    arg_dict['i'] = '%s@%s' % (username, url)
    arg_dict['p'] = password


def run(*a, **b):
    if 'h' in b or 'help' in b or not b:
        return print_help()

    sql_dir = a[0] if a else '.'
    if 'j' in b:
        rewrite_by_java(b, b['j'])  # for java-springboot

    full_host = b['i']
    if '@' in full_host:
        username, full_host = full_host.split('@', 1)
    else:
        username = 'root'
    full_host, database = full_host.split('/', 1)
    if ':' in full_host:
        host, port = full_host.split(':', 1)
    else:
        host, port = full_host, '3306'

    password = b.get('p', '')
    to_version = b.get('t', None)
    cur_env = b.get('e', '_!_').lower()

    conn = mysql.connector.connect(user=username, password=password, host=host, port=int(port), database=database)
    cur = conn.cursor()

    if 'd' in b:
        cur.execute("DROP DATABASE IF EXISTS {}".format(database))
        cur.execute("CREATE DATABASE {}".format(database))
        cur.execute("USE {}".format(database))

    cur.execute("""CREATE TABLE IF NOT EXISTS `_migrate_` (
            `version` int(11) unsigned NOT NULL,
            PRIMARY KEY (`version`)
        ) """)
    cur.execute("SELECT version FROM _migrate_ LIMIT 1")
    row = list(cur)
    if row:
        start_version = row[0][0]
    else:
        start_version = 0
        cur.execute("INSERT INTO _migrate_ VALUES(0)")

    if b.get('s', None) is not None:
        start_version = int(b['s'])

    print('Start Version: %d' % start_version)

    sqls = [(fetch_version(x), x) for x in os.listdir(sql_dir) if fetch_version(x)]
    sqls.sort(key = lambda x: x[0][0])
    querys = []
    max_version = 0
    for k, fname in sqls:
        content = open(os.path.join(sql_dir, fname)).read()
        version, onlys, excepts = k
        assert version > 0, "version must larger than 0"
        if version <= start_version: continue
        if to_version and version > to_version: continue
        if (onlys is not None and cur_env not in onlys) or \
                (excepts is not None and cur_env in excepts):
            continue
        querys.append(content)
        max_version = version

    if querys:
        querys.append("UPDATE _migrate_ SET version=%d;" % max_version)
        query_text = '\n'.join(querys)
        for item in cur.execute(query_text, multi=True):
            if isinstance(item, MySQLCursor):
                _ = list(item)
                print(item)
                print(_[:10])
                if len(_) > 10: print('... (total: %d rows) ...' % len(_))

        conn.commit()

    cur.close()
    conn.close()
    print('---- Migrate Done. ----')


def entrypoint():
    lesscli.run(run, single='d')

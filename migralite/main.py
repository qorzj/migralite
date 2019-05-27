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
        -m    : dump remote database schema
        -o    : debug file name, output full sql content
        
        -j    : use java properties
        -J    : another java properties to compare with
    """
    print(text)


def connect_mysql(arg_dict, jconfname=None):
    if jconfname:
        url = username = password = ''
        for line in open(jconfname).read().splitlines():
            if not line or line[0] == '#':
                continue
            if line.startswith('spring.datasource.url='):
                url = line.split(':mysql://', 1)[-1].split('?', 1)[0]
            if line.startswith('spring.datasource.hikari.username='):
                username = line.split('=', 1)[-1]
            if line.startswith('spring.datasource.hikari.password='):
                password = line.split('=', 1)[-1]

        if not username or not url or not password:
            print('Java properties wrong format: {}'.format(jconfname))
            exit(1)

        arg_dict['i'] = '%s@%s' % (username, url)
        arg_dict['p'] = password

    full_host = arg_dict['i']
    if '@' in full_host:
        username, full_host = full_host.split('@', 1)
    else:
        username = 'root'
    full_host, database = full_host.split('/', 1)
    if ':' in full_host:
        host, port = full_host.split(':', 1)
    else:
        host, port = full_host, '3306'

    password = arg_dict.get('p', '')
    conn = mysql.connector.connect(user=username, password=password, host=host, port=int(port), database=database)
    cur = conn.cursor()
    return conn, cur, database


def split_sql_content(content):
    sb = []
    for line in content.splitlines():
        s = line.strip()
        if s.startswith('#') or (s.startswith('/*') and s.endswith(('*/', '*/;'))):
            yield '\n'.join(sb)
            sb = []
        elif s.startswith('/*'):
            yield '\n'.join(sb)
            sb = [line]
        else:
            sb.append(line)
    if sb:
        yield '\n'.join(sb)


def compare(arg_dict, cur, rows=None):
    dbname = arg_dict['i'].rsplit('/', 1)[-1]
    cur.execute("select TABLE_NAME, COLUMN_NAME, IS_NULLABLE, DATA_TYPE, COLUMN_TYPE, COLUMN_KEY "
                " from information_schema.COLUMNS where TABLE_SCHEMA='{}' AND TABLE_NAME!='_migrate_' "
                " order by TABLE_NAME, COLUMN_NAME".format(dbname))
    if rows:
        from unittest import TestCase
        rows2 = list(cur)
        TestCase().assertListEqual(rows, rows2)
        return rows
    else:
        return list(cur)


def run(*a, **b):
    if 'h' in b or 'help' in b or not b:
        return print_help()

    sql_dir = a[0] if a else '.'

    jconfname = b.get('j')  # for java-springboot
    conn, cur, database = connect_mysql(b, jconfname)

    to_version = b.get('t', None)
    cur_env = b.get('e', '_!_').lower()

    if 'J' in b:
        rows = compare(b, cur)
        conn2, cur2, _ = connect_mysql(b, b['J'])
        compare(b, cur2, rows)
        print('---- Compare Passed. ----')
        cur.close()
        conn.close()
        cur2.close()
        conn2.close()
        return

    if 'd' in b:
        cur.execute("DROP DATABASE IF EXISTS {}".format(database))
        cur.execute("CREATE DATABASE {}".format(database))
        cur.execute("USE {}".format(database))

    cur.execute("""CREATE TABLE IF NOT EXISTS `{}._migrate_` (
            `version` int(11) unsigned NOT NULL,
            PRIMARY KEY (`version`)
        ) """.format(database))
    cur.execute("SELECT version FROM `{}._migrate_` LIMIT 1".format(database))
    row = list(cur)
    if row:
        start_version = row[0][0]
    else:
        start_version = 0
        cur.execute("INSERT INTO `{}._migrate_` VALUES(0)".format(database))

    if b.get('s', None) is not None:
        start_version = int(b['s'])

    print('Start Version: %d' % start_version)

    sqls = [(fetch_version(x), x) for x in os.listdir(sql_dir) if fetch_version(x)]
    sqls.sort(key = lambda x: x[0][0])
    for k, fname in sqls:
        content = open(os.path.join(sql_dir, fname)).read()
        version, onlys, excepts = k
        assert version > 0, "version must larger than 0"
        if version <= start_version: continue
        if to_version and version > to_version: continue
        if (onlys is not None and cur_env not in onlys) or \
                (excepts is not None and cur_env in excepts):
            continue
        if 'o' in b:  # for debug
            with open(b['o'], 'w') as fdbg:
                fdbg.write(content)

        item = None
        try:
            for subcontent in split_sql_content(content):
                if not subcontent.strip(): continue
                for item in cur.execute(subcontent, multi=True):
                    if isinstance(item, MySQLCursor):
                        _ = list(item)
                        print(item)
                        print(_[:10])
                        if len(_) > 10: print('... (total: %d rows) ...' % len(_))
        except:
            if isinstance(item, MySQLCursor): print('Failed Statement:', item.statement)
            raise

        version_sql = "UPDATE `%s._migrate_` SET version=%d;" % (database, version)
        print(version_sql)
        cur.execute(version_sql)

    conn.commit()

    cur.close()
    conn.close()
    print('---- Migrate Done. ----')


def entrypoint():
    lesscli.run(run, single='d')

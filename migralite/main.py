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
    
        -h    : show help information
    """
    print(text)


def run(*a, **b):
    if 'h' in b or 'help' in b or not b:
        return print_help()
    sql_dir = a[0] if a else '.'
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
                print(_) if len(_) < 10 else (print(_), print('... (total: %d rows) ...' % len(_)))

        conn.commit()

    cur.close()
    conn.close()
    print('---- Migrate Done. ----')


def entrypoint():
    lesscli.run(run)

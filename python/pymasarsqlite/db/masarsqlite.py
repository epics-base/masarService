'''
Created on Dec 19, 2011

@author: shengb
'''

import os, sqlite3

def getSqlite():
    from os.path import dirname, join
    sqlfile = join(dirname(__file__), 'masar-sqlite.sql')

    with open(sqlfile, 'r') as F:
        sql = F.read()
    return sql

def connect(*args, **kws):
    '''Helper to connect to sqlite3 with lazy loading of schema.
    Accepts the same args as sqlite3.connect()
    Returns sqlite3.Connection with MASAR schema loaded
    '''
    conn = sqlite3.connect(*args, **kws)
    try:
        # test to see if the schema is loaded
        loadschema = False
        try:
            conn.execute("SELECT * FROM pv_group LIMIT 1")
        except sqlite3.OperationalError:
            loadschema = True
        if loadschema:
            print 'Loading SQLITE DB schema'
            conn.executescript(SQL)
    except:
        conn.close()
        raise
    return conn

SQL = getSqlite()

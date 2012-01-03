'''
Created on Dec 19, 2011

@author: shengb
'''

import os

def getSqlite():
    __sql = '/'.join((os.path.abspath(os.path.dirname(__file__)), 'masar-sqlite.sql'))
    sqlfile = None
    __SQL = None

    try:
        if os.path.exists(__sql): 
            if os.path.isfile(__sql):
                sqlfile = open(__sql, 'r')
                __SQL = sqlfile.read()
    except:
        raise
    finally:
        if sqlfile:
            sqlfile.close()
    return __SQL

SQL = getSqlite()

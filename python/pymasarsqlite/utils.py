'''
Created on Dec 8, 2011

@author: shengb
'''

import os
import sqlite3

from .db import masarsqlite

try:
    __db=os.environ['MASAR_SQLITE_DB']
except KeyError:
    raise KeyError("Environment variable MASAR_SQLITE_DB not set")

def connect():
    try:
        return masarsqlite.connect(__db)
    except sqlite3.OperationalError as e:
        raise RuntimeError("Failed to open DB '%s': %s"%(__db, e))

def checkConnection(conn):
    """
    Check whether conn is empty.
    
    >>> import sqlite3
    >>> conn = sqlite3.connect(':memory:')
    >>> checkConnection(conn)
    """
    if conn == None:
        raise Exception('SQLite connection is empty.')

def save(conn):
    checkConnection(conn)
    conn.commit()
    
def close(conn):
    checkConnection(conn)
    conn.close()

__all__ = ['checkConnection', 'save', 'connect', 'close']

if __name__ == '__main__':
    import doctest
    doctest.testmod()

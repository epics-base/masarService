'''
Created on Dec 8, 2011

@author: shengb
'''

import os
import sqlite3

try:
    __db=os.environ['MASAR_SQLITE_DB']
except KeyError:
    raise

def connect():
    return sqlite3.connect(__db)

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

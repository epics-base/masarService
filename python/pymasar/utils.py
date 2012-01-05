'''
Created on Dec 8, 2011

@author: shengb
'''

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

__all__ = ['checkConnection', 'save']

if __name__ == '__main__':
    import doctest
    doctest.testmod()
'''
Created on Dec 9, 2011

@author: shengb
'''
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import sys
import sqlite3

from pymasar.utils import checkConnection

def retrieveServices(conn, servicename=None):
    """
    Retrieve all services stored in service table.
    for example:
    
    >>> import sqlite3
    >>> from pymasar.service.service import (saveService, retrieveServices)
    >>> from pymasar.db.masarsqlite import (SQL)
    >>> conn = sqlite3.connect(':memory:')
    >>> cur = conn.cursor()
    >>> result = cur.executescript(SQL)
    >>> saveService(conn, 'masar1', desc='non-empty description')
    1
    >>> saveService(conn, 'masar2')
    2
    >>> retrieveServices(conn)
    [(1, u'masar1', u'non-empty description'), (2, u'masar2', u'')]
    >>> retrieveServices(conn, 'masar1')
    [(1, u'masar1', u'non-empty description')]
    >>> retrieveServices(conn, 'masar3')
    []
    >>> conn.close()
    """
    checkConnection(conn)
    
    result = None
    try:
        cursor = conn.cursor()
        if servicename is None:
            cursor.execute('select service_id, service_name, service_desc from service')
        else:
            cursor.execute('select service_id, service_name, service_desc from service where service_name = ?', (servicename,))
        result = cursor.fetchall()
#        queryResponse = cursor.fetchall()
#        for row in queryResponse:
#            result.append(''.join(row[0]))  #force result into a string
#            desc.append(''.join(row[1]))
    except sqlite3.Error, e:
        raise Exception("Error %s:" % e.args[0])
        sys.exit(1)

    return result

def saveService(conn, name, desc=''):
    """
    Save list services into service table.
    The key word looks like:
    name='my service name', desc='description for this service'
    for example:
    
    >>> import sqlite3
    >>> from pymasar.service.service import (saveService, retrieveServices)
    >>> from pymasar.db.masarsqlite import (SQL)
    >>> conn = sqlite3.connect(':memory:')
    >>> cur = conn.cursor()
    >>> result = cur.executescript(SQL)
    >>> saveService(conn, 'masar', desc='an example')
    1
    >>> retrieveServices(conn, 'masar')
    [(1, u'masar', u'an example')]
    >>> conn.close()
    """
    checkConnection(conn)
    
    serviceId = None
    try:
        cursor = conn.cursor()
        cursor.execute('insert into service(service_id, service_name, service_desc) values (?,?,?)', (None, name, desc))
        serviceId = cursor.lastrowid
    except sqlite3.Error, e:
        print ("Error %s:" % e.args[0])
        raise
        sys.exit(1)
    
    return serviceId

if __name__ == "__main__":
    import doctest
    doctest.testmod()

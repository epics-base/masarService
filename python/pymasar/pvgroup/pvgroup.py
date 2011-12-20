'''
Created on Dec 7, 2011

@author: shengb
'''
from utils import checkConnection

def savePvGroup(conn, name, **kws):
    """
    Save pv groups with given name and description into pv_group table.
    With current version, the pv group name has to be global unique.
    If one pv group already exists and update is true, update its description.
     
    The key word is optional, and looks like:
    [func='function description for this pv group'] [, update=False] [, version = '0.0.1']
    
    >>> import sqlite3
    >>> from pvgroup import (savePvGroup, retrievePvGroups)
    >>> conn = sqlite3.connect(':memory:')
    >>> cur = conn.cursor()
    >>> SQL = '''CREATE TABLE "pv_group" (
    ...        "pv_group_id" INTEGER ,
    ...        "pv_group_name" varchar(50) DEFAULT NULL,
    ...        "pv_group_func" varchar(50) DEFAULT NULL,
    ...        "pvg_creation_date" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ...         "version" varchar(50) DEFAULT NULL,
    ...        PRIMARY KEY ("pv_group_id")
    ...        );'''
    >>> result = cur.executescript(SQL)
    >>> name = 'masar'
    >>> desc = 'this is my first pv group for masar service'
    >>> savePvGroup(conn, name, func=desc)
    [1]
    >>> desc = 'this is my new pv group for masar service with same group name'
    >>> savePvGroup(conn, name, func=desc)
    [1]
    >>> name = 'masar2'
    >>> desc = 'this is my new pv group for masar service with same group name'
    >>> savePvGroup(conn, name, func=desc)
    [2]
    >>> conn.close()
    """
    checkConnection(conn)
    func = None
    version = None
    try:
        func = kws['func']
    except:
        pass
    try:
        version = kws['version']
    except:
        pass
    update = False
    try:
        update = kws['update']
    except:
        pass
    
    cur = conn.cursor()
    basic_sql = 'select pv_group_id from pv_group where pv_group_name = ?'
    cur.execute(basic_sql, (name,))
#    basic_sql = 'select pv_group_id, pv_group_name, pv_group_func, pvg_creation_date, version from pv_group where pv_group_name = ?'
#    if func is None and version is None:
#        cur.execute(basic_sql, (name,))
#    elif version is None:
#        cur.execute(basic_sql + ' and pv_group_func = ?', (name, func))
#    elif version is None:
#        cur.execute(basic_sql + ' and version = ?', (name, version))
#    else:
#        cur.execute(basic_sql + ' and pv_group_func = ? and version = ?', (name, func, version))
    pvgroups = cur.fetchall()
    pvgroup_id = []
    
    if len(pvgroups) == 0:
        cur.execute('insert into pv_group(pv_group_id, pv_group_name, pv_group_func, pvg_creation_date, version) values (?,?,?,datetime("now"),?)', (None, name, func, version))
        pvgroup_id.append(cur.lastrowid)
    else:
        for pvgroup in pvgroups:
            pvgroup_id.append(pvgroup[0])
        if update:
            cur.execute('UPDATE pv_group SET pv_group_func = ? WHERE pv_group_id = ?', (pvgroup[0],))
#        pvgroup_id = pvgroups['id']
        
    return pvgroup_id

def retrievePvGroups(conn, pvgroupname=None):
    """
    Retrieve pv groups with given name from pv_group table.
    It returns a tuple with format (pv_group_id, pv_group_name, pv_group_func, pvg_creation_date, version)
     
    >>> import sqlite3
    >>> from pvgroup import (savePvGroup, retrievePvGroups)
    >>> conn = sqlite3.connect(':memory:')
    >>> cur = conn.cursor()
    >>> SQL = '''CREATE TABLE "pv_group" (
    ...        "pv_group_id" INTEGER ,
    ...        "pv_group_name" varchar(50) DEFAULT NULL,
    ...        "pv_group_func" varchar(50) DEFAULT NULL,
    ...        "pvg_creation_date" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ...         "version" varchar(50) DEFAULT NULL,
    ...        PRIMARY KEY ("pv_group_id")
    ...        );'''
    >>> result = cur.executescript(SQL)
    >>> name = 'masar'
    >>> desc = 'this is my first pv group for masar service'
    >>> savePvGroup(conn, name, func=desc)
    [1]
    >>> name = 'masar2'
    >>> desc = 'this is my new pv group for masar service with same group name'
    >>> savePvGroup(conn, name, func=desc)
    [2]
    >>> pvgroups = retrievePvGroups(conn)
    >>> for pvgroup in pvgroups:
    ...    print (pvgroup[0], pvgroup[1])
    (1, u'masar')
    (2, u'masar2')
    >>> pvgroups = retrievePvGroups(conn, 'masar')
    >>> for pvgroup in pvgroups:
    ...    print (pvgroup[0], pvgroup[1])
    (1, u'masar')
    >>> pvgroups = retrievePvGroups(conn, 'masar2')
    >>> for pvgroup in pvgroups:
    ...    print (pvgroup[0], pvgroup[1])
    (2, u'masar2')
    >>> retrievePvGroups(conn, 'masar3')
    []
    >>> conn.close()
    """
    checkConnection(conn)
    cur = conn.cursor()
    if pvgroupname is None:
        cur.execute('select pv_group_id, pv_group_name, pv_group_func, pvg_creation_date, version from pv_group')
    else:
        cur.execute('select pv_group_id, pv_group_name, pv_group_func, pvg_creation_date, version from pv_group where pv_group_name = ?',
               (pvgroupname,))

    dataset = cur.fetchall()
    
    return dataset
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()

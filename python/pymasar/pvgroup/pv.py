'''
Created on Dec 7, 2011

@author: shengb
'''
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import sys

from pymasar.utils import checkConnection

def savePvs(conn, pvlist, pvdesc=None, update = False):
    """
    This method saves all pvs in pvlist, and returns the pv_id (the primary key) list. 
    If one pv already exists, it retrieves its primary key, and update its description if update is true. 
    
    >>> import sqlite3
    >>> from pymasar.pvgroup.pv import (savePvs, retrieveGroupPvs)
    >>> from pymasar.db.masarsqlite import (SQL)
    >>> conn = sqlite3.connect(":memory:")
    >>> cur = conn.cursor()
    >>> result = cur.executescript(SQL)
    >>> pvs = ['SR:C01-BI:G02A<BPM:L1>Pos-X', 'SR:C01-BI:G02A<BPM:L2>Pos-X',
    ...        'SR:C01-BI:G04A<BPM:M1>Pos-X', 'SR:C01-BI:G04B<BPM:M1>Pos-X',
    ...        'SR:C01-BI:G06B<BPM:H1>Pos-X', 'SR:C01-BI:G06B<BPM:H2>Pos-X',
    ...        'SR:C02-BI:G02A<BPM:H1>Pos-X', 'SR:C02-BI:G02A<BPM:H2>Pos-X',
    ...        'SR:C02-BI:G04A<BPM:M1>Pos-X', 'SR:C02-BI:G04B<BPM:M1>Pos-X',
    ...        'SR:C02-BI:G06B<BPM:L1>Pos-X', 'SR:C02-BI:G06B<BPM:L2>Pos-X',
    ...        'SR:C03-BI:G02A<BPM:L1>Pos-X', 'SR:C03-BI:G02A<BPM:L2>Pos-X',
    ...        'SR:C03-BI:G04A<BPM:M1>Pos-X', 'SR:C03-BI:G04B<BPM:M1>Pos-X']
    >>> savePvs(conn, pvs)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    >>> desc = ['Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G04 M1', 'Horizontal orbit from BPM at C01 G04 M1',
    ...          'Horizontal orbit from BPM at C01 G06 H1', 'Horizontal orbit from BPM at C01 G06 H2',
    ...          'Horizontal orbit from BPM at C02 G02 H1', 'Horizontal orbit from BPM at C02 G02 H2',
    ...          'Horizontal orbit from BPM at C02 G04 M1', 'Horizontal orbit from BPM at C02 G04 M1',
    ...          'Horizontal orbit from BPM at C02 G06 L1', 'Horizontal orbit from BPM at C01 G06 L2',
    ...          'Horizontal orbit from BPM at C03 G02 L1', 'Horizontal orbit from BPM at C03 G02 L2',
    ...          'Horizontal orbit from BPM at C03 G04 M1', 'Horizontal orbit from BPM at C03 G04 M1']
    >>> savePvs(conn, pvs, desc)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    >>> tmp = cur.execute('select pv_id, pv_name, description from pv')
    >>> dataset = cur.fetchall()
    >>> for data in dataset:
    ...    print (data)
    (1, u'SR:C01-BI:G02A<BPM:L1>Pos-X', None)
    (2, u'SR:C01-BI:G02A<BPM:L2>Pos-X', None)
    (3, u'SR:C01-BI:G04A<BPM:M1>Pos-X', None)
    (4, u'SR:C01-BI:G04B<BPM:M1>Pos-X', None)
    (5, u'SR:C01-BI:G06B<BPM:H1>Pos-X', None)
    (6, u'SR:C01-BI:G06B<BPM:H2>Pos-X', None)
    (7, u'SR:C02-BI:G02A<BPM:H1>Pos-X', None)
    (8, u'SR:C02-BI:G02A<BPM:H2>Pos-X', None)
    (9, u'SR:C02-BI:G04A<BPM:M1>Pos-X', None)
    (10, u'SR:C02-BI:G04B<BPM:M1>Pos-X', None)
    (11, u'SR:C02-BI:G06B<BPM:L1>Pos-X', None)
    (12, u'SR:C02-BI:G06B<BPM:L2>Pos-X', None)
    (13, u'SR:C03-BI:G02A<BPM:L1>Pos-X', None)
    (14, u'SR:C03-BI:G02A<BPM:L2>Pos-X', None)
    (15, u'SR:C03-BI:G04A<BPM:M1>Pos-X', None)
    (16, u'SR:C03-BI:G04B<BPM:M1>Pos-X', None)
    >>> savePvs(conn, pvs, desc, update=True)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    >>> tmp = cur.execute('select pv_id, pv_name, description from pv')
    >>> dataset = cur.fetchall()
    >>> for data in dataset:
    ...    print (data)
    (1, u'SR:C01-BI:G02A<BPM:L1>Pos-X', u'Horizontal orbit from BPM at C01 G02 L1')
    (2, u'SR:C01-BI:G02A<BPM:L2>Pos-X', u'Horizontal orbit from BPM at C01 G02 L2')
    (3, u'SR:C01-BI:G04A<BPM:M1>Pos-X', u'Horizontal orbit from BPM at C01 G04 M1')
    (4, u'SR:C01-BI:G04B<BPM:M1>Pos-X', u'Horizontal orbit from BPM at C01 G04 M1')
    (5, u'SR:C01-BI:G06B<BPM:H1>Pos-X', u'Horizontal orbit from BPM at C01 G06 H1')
    (6, u'SR:C01-BI:G06B<BPM:H2>Pos-X', u'Horizontal orbit from BPM at C01 G06 H2')
    (7, u'SR:C02-BI:G02A<BPM:H1>Pos-X', u'Horizontal orbit from BPM at C02 G02 H1')
    (8, u'SR:C02-BI:G02A<BPM:H2>Pos-X', u'Horizontal orbit from BPM at C02 G02 H2')
    (9, u'SR:C02-BI:G04A<BPM:M1>Pos-X', u'Horizontal orbit from BPM at C02 G04 M1')
    (10, u'SR:C02-BI:G04B<BPM:M1>Pos-X', u'Horizontal orbit from BPM at C02 G04 M1')
    (11, u'SR:C02-BI:G06B<BPM:L1>Pos-X', u'Horizontal orbit from BPM at C02 G06 L1')
    (12, u'SR:C02-BI:G06B<BPM:L2>Pos-X', u'Horizontal orbit from BPM at C01 G06 L2')
    (13, u'SR:C03-BI:G02A<BPM:L1>Pos-X', u'Horizontal orbit from BPM at C03 G02 L1')
    (14, u'SR:C03-BI:G02A<BPM:L2>Pos-X', u'Horizontal orbit from BPM at C03 G02 L2')
    (15, u'SR:C03-BI:G04A<BPM:M1>Pos-X', u'Horizontal orbit from BPM at C03 G04 M1')
    (16, u'SR:C03-BI:G04B<BPM:M1>Pos-X', u'Horizontal orbit from BPM at C03 G04 M1')
    >>> conn.close()
    """
    checkConnection(conn)
    
    if len(pvlist) == 0 or (pvdesc != None and len(pvlist) != len(pvdesc)):
        raise Exception('empty pv list or length of pv list and description does not match.')
        sys.exit()

    cur = conn.cursor()
    pv_ids = []
    for i in range(len(pvlist)):
        pv_name = pvlist[i]
        cur.execute('select pv_id from pv where pv_name = ?', (pv_name,))
        pv_id = cur.fetchone()
        
        desc = None
        if pvdesc!=None:
            desc = pvdesc[i]

        if pv_id is None:
            cur.execute('insert into pv(pv_id, pv_name, description) values (?,?,?)', (None, pv_name, desc))
            pv_id = cur.lastrowid
#            cur.execute('select pv_id from pv where pv_name = ?', (pvlist[i],))
#            pv_id = cur.fetchone()
        else:
            pv_id = pv_id[0]
            if update:
                "update pv description"
                cur.execute('UPDATE pv SET description=? WHERE pv_name = ? and pv_id=?', (desc, pv_name, pv_id))

        pv_ids.append(pv_id)
    
    return pv_ids

def saveGroupPvs(conn, pvgroupname, pvlist, pvdesc = None, update = False):
    """
    This method saves all pvs in pvlist, and assigns those pvs to given pv group name. If update is true, 
    update the pvs in the pv group. By default, it uses existing pvs belonging to that group. Currently,
    the update flag is a place holder to future usage. It is not allowed to append any pv to existing pv
    group. 
    
    In general, once a pv group exists, it is not encourage to modify it. Create a new pv group 
    instead of appending any pv into existing one.
    
    >>> import sqlite3
    >>> from __future__ import print_function
    >>> from pymasar.pvgroup.pv import (savePvs, retrieveGroupPvs)
    >>> from pymasar.pvgroup.pvgroup import(savePvGroup, retrievePvGroups)
    >>> from pymasar.db.masarsqlite import (SQL)
    >>> conn = sqlite3.connect(":memory:")
    >>> cur = conn.cursor()
    >>> result = cur.executescript(SQL)
    >>> pvs = ['SR:C01-BI:G02A<BPM:L1>Pos-X', 'SR:C01-BI:G02A<BPM:L2>Pos-X',
    ...        'SR:C01-BI:G04A<BPM:M1>Pos-X', 'SR:C01-BI:G04B<BPM:M1>Pos-X',
    ...        'SR:C01-BI:G06B<BPM:H1>Pos-X', 'SR:C01-BI:G06B<BPM:H2>Pos-X',
    ...        'SR:C02-BI:G02A<BPM:H1>Pos-X', 'SR:C02-BI:G02A<BPM:H2>Pos-X',
    ...        'SR:C02-BI:G04A<BPM:M1>Pos-X', 'SR:C02-BI:G04B<BPM:M1>Pos-X',
    ...        'SR:C02-BI:G06B<BPM:L1>Pos-X', 'SR:C02-BI:G06B<BPM:L2>Pos-X',
    ...        'SR:C03-BI:G02A<BPM:L1>Pos-X', 'SR:C03-BI:G02A<BPM:L2>Pos-X',
    ...        'SR:C03-BI:G04A<BPM:M1>Pos-X', 'SR:C03-BI:G04B<BPM:M1>Pos-X']
    >>> pvdesc = ['Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2']
    >>> name = 'masar'
    >>> desc = 'this is my first pv group for masar service'
    >>> savePvGroup(conn, name, func=desc)
    [1]
    >>> pvgroups = retrievePvGroups(conn, name)
    >>> for pvgroup in pvgroups:
    ...    print (pvgroup[0], pvgroup[1])
    1 masar
    >>> saveGroupPvs(conn, name, pvs, pvdesc=pvdesc)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    >>> saveGroupPvs(conn, name, pvs, pvdesc=pvdesc)
    []
    >>> conn.close()
    """
    
    checkConnection(conn)
    cur=conn.cursor()
    cur.execute('select pv_group_id from pv_group where pv_group_name = ?', (pvgroupname,))
    pvgroupid = cur.fetchall()
    if len(pvgroupid) != 1:
        raise Exception('''pv group name ({0}) is not unique, or not exist.'''.format(pvgroupname))
        sys.exit()
    else:
        pvgroupid = pvgroupid[0][0]
    cur.execute('select pv__pvgroup_id from pv__pvgroup where pv_group_id = ?', (pvgroupid,))
    pv_pvg_id = cur.fetchone()
    pv_pvg_ids = []
    if pv_pvg_id is None:
        "the pv group with pvgroupid does not exist."
        pv_ids = savePvs(conn, pvlist, pvdesc=pvdesc)
        for pv_id in pv_ids:
            cur.execute('select pv__pvgroup_id from pv__pvgroup where pv_id = ? and pv_group_id = ?', (pv_id, pvgroupid))
            pv_pvg_id = cur.fetchone()
            if pv_pvg_id is None:
                cur.execute('insert into pv__pvgroup (pv__pvgroup_id, pv_id, pv_group_id) values (?,?,?)', (None, pv_id, pvgroupid))
                pv_pvg_id = cur.lastrowid
            else:
                pv_pvg_id = pv_pvg_id[0]
            pv_pvg_ids.append(pv_pvg_id)
        
    elif update:
        "the pv group with pvgroupid exists, and need to be updated."
    else:
        "the pv group with pvgroupid exists, and not need to be updated."
    
    return pv_pvg_ids
        
def retrieveGroupPvs(conn, pvgroupid):
    """
    This methods retrieves all pvs associated with a pv_group.
    Return return a tuple array with like [(pv_name1, description1),(pv_name2, description2)].
    for example:
    
    >>> import sqlite3
    >>> from __future__ import print_function
    >>> from pymasar.pvgroup.pv import (savePvs, retrieveGroupPvs)
    >>> from pymasar.pvgroup.pvgroup import(savePvGroup, retrievePvGroups)
    >>> from pymasar.db.masarsqlite import (SQL)
    >>> conn = sqlite3.connect(":memory:")
    >>> cur = conn.cursor()
    >>> result = cur.executescript(SQL)
    >>> pvs = ['SR:C01-BI:G02A<BPM:L1>Pos-X', 'SR:C01-BI:G02A<BPM:L2>Pos-X',
    ...        'SR:C01-BI:G04A<BPM:M1>Pos-X', 'SR:C01-BI:G04B<BPM:M1>Pos-X',
    ...        'SR:C01-BI:G06B<BPM:H1>Pos-X', 'SR:C01-BI:G06B<BPM:H2>Pos-X',
    ...        'SR:C02-BI:G02A<BPM:H1>Pos-X', 'SR:C02-BI:G02A<BPM:H2>Pos-X',
    ...        'SR:C02-BI:G04A<BPM:M1>Pos-X', 'SR:C02-BI:G04B<BPM:M1>Pos-X',
    ...        'SR:C02-BI:G06B<BPM:L1>Pos-X', 'SR:C02-BI:G06B<BPM:L2>Pos-X',
    ...        'SR:C03-BI:G02A<BPM:L1>Pos-X', 'SR:C03-BI:G02A<BPM:L2>Pos-X',
    ...        'SR:C03-BI:G04A<BPM:M1>Pos-X', 'SR:C03-BI:G04B<BPM:M1>Pos-X']
    >>> pvdesc = ['Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2',
    ...          'Horizontal orbit from BPM at C01 G02 L1', 'Horizontal orbit from BPM at C01 G02 L2']
    >>> name = 'masar'
    >>> desc = 'this is my first pv group for masar service'
    >>> savePvGroup(conn, name, func=desc)
    [1]
    >>> pvgroups = retrievePvGroups(conn, name)
    >>> for pvgroup in pvgroups:
    ...    print (pvgroup[0], pvgroup[1])
    1 masar
    >>> saveGroupPvs(conn, name, pvs, pvdesc=pvdesc)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    >>> results = retrieveGroupPvs(conn, 1)
    >>> for result in results:
    ...     print (result)
    (u'SR:C01-BI:G02A<BPM:L1>Pos-X', u'Horizontal orbit from BPM at C01 G02 L1')
    (u'SR:C01-BI:G02A<BPM:L2>Pos-X', u'Horizontal orbit from BPM at C01 G02 L2')
    (u'SR:C01-BI:G04A<BPM:M1>Pos-X', u'Horizontal orbit from BPM at C01 G02 L1')
    (u'SR:C01-BI:G04B<BPM:M1>Pos-X', u'Horizontal orbit from BPM at C01 G02 L2')
    (u'SR:C01-BI:G06B<BPM:H1>Pos-X', u'Horizontal orbit from BPM at C01 G02 L1')
    (u'SR:C01-BI:G06B<BPM:H2>Pos-X', u'Horizontal orbit from BPM at C01 G02 L2')
    (u'SR:C02-BI:G02A<BPM:H1>Pos-X', u'Horizontal orbit from BPM at C01 G02 L1')
    (u'SR:C02-BI:G02A<BPM:H2>Pos-X', u'Horizontal orbit from BPM at C01 G02 L2')
    (u'SR:C02-BI:G04A<BPM:M1>Pos-X', u'Horizontal orbit from BPM at C01 G02 L1')
    (u'SR:C02-BI:G04B<BPM:M1>Pos-X', u'Horizontal orbit from BPM at C01 G02 L2')
    (u'SR:C02-BI:G06B<BPM:L1>Pos-X', u'Horizontal orbit from BPM at C01 G02 L1')
    (u'SR:C02-BI:G06B<BPM:L2>Pos-X', u'Horizontal orbit from BPM at C01 G02 L2')
    (u'SR:C03-BI:G02A<BPM:L1>Pos-X', u'Horizontal orbit from BPM at C01 G02 L1')
    (u'SR:C03-BI:G02A<BPM:L2>Pos-X', u'Horizontal orbit from BPM at C01 G02 L2')
    (u'SR:C03-BI:G04A<BPM:M1>Pos-X', u'Horizontal orbit from BPM at C01 G02 L1')
    (u'SR:C03-BI:G04B<BPM:M1>Pos-X', u'Horizontal orbit from BPM at C01 G02 L2')
    >>> results = retrieveGroupPvs(conn, 2)
    >>> print (results)
    []
    >>> conn.close()
    """
    checkConnection(conn)
    cur = conn.cursor()

    # if there is any query performance issue, the SQL command should use left join, 
    # fine tuning join order to get best performance.
    # Here is an example using join
    SQL = ''' select pv.pv_name, pv.description from pv
    left join pv__pvgroup using (pv_id)
    left join pv_group using (pv_group_id)
    where pv_group.pv_group_id = ?
    '''
    
#    SQL = '''select pv.pv_name, pv.description from pv, pv__pvgroup, pv_group where pv.pv_id = pv__pvgroup.pv_id
#    and pv__pvgroup.pv_group_id = pv_group.pv_group_id
#    and pv_group.pv_group_id = ?
#    '''

    cur.execute(SQL, (pvgroupid,))
    dataset = cur.fetchall()
    return dataset

if __name__ == '__main__':
    import doctest
    doctest.testmod()
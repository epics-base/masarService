'''
Created on Dec 16, 2011

@author: shengb
'''
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sqlite3
import datetime as dt

from pymasar.utils import checkConnection
from pymasar.service.serviceconfig import (retrieveServiceConfigs)

def saveServiceEvent(conn, servicename, configname, comment=None, approval=False, username=None):
    """
    save an event config, and associate this event with given service and service config.
    
    >>> import sqlite3
    >>> from pymasar.service.service import (saveService, retrieveServices)
    >>> from pymasar.service.serviceconfig import (saveServiceConfig)
    >>> from pymasar.db.masarsqlite import (SQL)
    >>> conn = sqlite3.connect(":memory:")
    >>> cur = conn.cursor()
    >>> result = cur.executescript(SQL)
    >>> saveService(conn, 'masar1', desc='non-empty description')
    1
    >>> saveService(conn, 'masar2', desc='non-empty description')
    2
    >>> saveServiceConfig(conn, 'masar1', 'orbit C01', 'BPM horizontal readout for storage ring')
    1
    >>> saveServiceConfig(conn, 'masar1', 'orbit C02', 'BPM horizontal readout for storage ring')
    2
    >>> saveServiceConfig(conn, 'masar2', 'orbit C01', 'BPM horizontal readout for storage ring')
    3
    >>> saveServiceConfig(conn, 'masar2', 'orbit C02', 'BPM horizontal readout for storage ring')
    4
    >>> result = retrieveServiceConfigs(conn, servicename='masar1', configname='orbit C01')
    >>> saveServiceEvent(conn, servicename='masar1', configname='orbit C01', comment='a service event')
    1
    >>> conn.close()
    """
    if servicename is None or configname is None:
        raise Exception('service or service config is empty. Can not associate the event with service and its config.')
    checkConnection(conn)
    if configname is None:
        raise Exception("service config name is not specified for this event.")
    
    serviceconfigid = retrieveServiceConfigs(conn, servicename=servicename, configname=configname)[1:]
    if len(serviceconfigid) > 0:
        serviceconfigid = serviceconfigid[0][0]
    else:
        raise Exception('Can not find service config (%s) with service (%s)' %(configname, servicename))

    sql = '''
    insert into service_event(service_event_id, service_config_id, service_event_user_tag, service_event_UTC_time, service_event_approval, service_event_user_name)
    values (?, ?, ?, datetime('now'), ?, ?)
    '''
    try:
        cur = conn.cursor()
        
        # each service event is a individual entity. Do not check the existence. 
        cur.execute(sql, (None, serviceconfigid, comment, approval, username))
    except sqlite3.Error, e:
        print ('Error %s' %e.args[0])
        raise
    return cur.lastrowid

def updateServiceEvent(conn, eventid, comment=None, approval=False, username=None):
    """
    update the comment, approval status, and add user name for an existing event.
    
    >>> import sqlite3
    >>> from pymasar.service.service import (saveService, retrieveServices)
    >>> from pymasar.service.serviceconfig import (saveServiceConfig)
    >>> from pymasar.db.masarsqlite import (SQL)
    >>> conn = sqlite3.connect(":memory:")
    >>> cur = conn.cursor()
    >>> result = cur.executescript(SQL)
    >>> saveService(conn, 'masar1', desc='non-empty description')
    1
    >>> saveService(conn, 'masar2', desc='non-empty description')
    2
    >>> saveServiceConfig(conn, 'masar1', 'orbit C01', 'BPM horizontal readout for storage ring')
    1
    >>> saveServiceConfig(conn, 'masar1', 'orbit C02', 'BPM horizontal readout for storage ring')
    2
    >>> saveServiceConfig(conn, 'masar2', 'orbit C01', 'BPM horizontal readout for storage ring')
    3
    >>> saveServiceConfig(conn, 'masar2', 'orbit C02', 'BPM horizontal readout for storage ring')
    4
    >>> result = retrieveServiceConfigs(conn, servicename='masar1', configname='orbit C01')
    >>> saveServiceEvent(conn, servicename='masar1', configname='orbit C01', comment='a service event',approval=True)
    1
    >>> saveServiceEvent(conn, servicename='masar1', configname='orbit C01', comment='end service event',approval=True)
    2
    >>> updateServiceEvent(conn, 1, comment='an updated service event', approval=True, username='test user')
    True
    >>> results = retrieveServiceEvents(conn)
    >>> for res in results[1:]:
    ...    print (res[0], res[0], res[2], res[4])
    1 1 an updated service event test user
    2 2 end service event None
    >>> conn.close()
    """
    checkConnection(conn)
   
    sqlsel = '''
    SELECT service_event_user_tag, service_event_approval, service_event_user_name
    FROM service_event
    WHERE service_event_id = ?
    '''
 
    sql = '''
    UPDATE service_event
    SET service_event_user_tag = ?, service_event_approval=?, service_event_user_name = ?
    WHERE service_event_id = ?
    '''
    try:
        cur = conn.cursor()
        
        cur.execute(sqlsel, (eventid,))
        comment0, approval0, username0 = cur.fetchone()
        if comment==None:
            comment = comment0
        if not approval:
            approval = approval0
        if username==None:
            username = username0
        # each service event is a individual entity. Do not check the existence.
        cur.execute(sql, (comment, approval, username, eventid)) 
    except sqlite3.Error, e:
        print ('Error %s' %e.args[0])
        raise
    return True

def retrieveServiceEvents(conn, configid=None,start=None, end=None, comment=None, user=None, approval=True):
    """
    retrieve an service event with given user tag within given time frame.
    Both start and end time should be in UTC time format.
    If end time is not specified, use current time. If start is not specified, use one week before end time.
    It return a tuple array with format like:
    [(service_event_id, service_config_id, service_event_user_tag, service_event_UTC_time, service_event_serial_tag)]
    
    >>> import sqlite3
    >>> from pymasar.service.service import (saveService, retrieveServices)
    >>> from pymasar.service.serviceconfig import (saveServiceConfig)
    >>> from pymasar.db.masarsqlite import (SQL)
    >>> conn = sqlite3.connect(":memory:")
    >>> cur = conn.cursor()
    >>> result = cur.executescript(SQL)
    >>> saveService(conn, 'masar1', desc='non-empty description')
    1
    >>> saveService(conn, 'masar2', desc='non-empty description')
    2
    >>> saveServiceConfig(conn, 'masar1', 'orbit C01', 'BPM horizontal readout for storage ring')
    1
    >>> saveServiceConfig(conn, 'masar1', 'orbit C02', 'BPM horizontal readout for storage ring')
    2
    >>> saveServiceConfig(conn, 'masar2', 'orbit C01', 'BPM horizontal readout for storage ring')
    3
    >>> saveServiceConfig(conn, 'masar2', 'orbit C02', 'BPM horizontal readout for storage ring')
    4
    >>> result = retrieveServiceConfigs(conn, servicename='masar1', configname='orbit C01')
    >>> import datetime as dt
    >>> saveServiceEvent(conn, servicename='masar1', configname='orbit C01', comment='a service event1',approval=True)
    1
    >>> start = dt.datetime.utcnow()
    >>> import time
    >>> time.sleep(1)
    >>> saveServiceEvent(conn, servicename='masar1', configname='orbit C01', comment='a service event2',approval=True)
    2
    >>> end = dt.datetime.utcnow()
    >>> time.sleep(1)
    >>> saveServiceEvent(conn, servicename='masar1', configname='orbit C01', comment='a service event3',approval=True)
    3
    >>> results = retrieveServiceEvents(conn, comment='a service event1')
    >>> for result in results[1:]:
    ...    print (result[0], result[1], result[2])
    1 1 a service event1
    >>> results = retrieveServiceEvents(conn)
    >>> for result in results[1:]:
    ...    print (result[0], result[1], result[2])
    1 1 a service event1
    2 1 a service event2
    3 1 a service event3
    >>> results = retrieveServiceEvents(conn, start=start, end=end)
    >>> for result in results[1:]:
    ...    print (result[0], result[1], result[2])
    2 1 a service event2
    >>> conn.close()
    """
    checkConnection(conn)
    results = None
    
    if comment == None:
        comment = '%'
    else:
        comment = comment.replace("*","%").replace("?","_")
        
    if user == None:
        user = "%"
    else:
        user = user.replace("*","%").replace("?","_")
    
    try:
        cur = conn.cursor()
        sql = '''
        select service_event_id, service_config_id, service_event_user_tag, service_event_UTC_time, service_event_user_name
        from service_event where service_event_approval = 1 and service_event_user_tag like ? and service_event_user_name like ?
        '''
        
        if (start is None) and (end is None):
            if configid is None:
                cur.execute(sql, (comment, user, ))
            else:
                sql += ' and service_config_id = ?'
                cur.execute(sql, (comment, user, configid, ))
        else:
            sql += ' and service_event_UTC_time > ? and service_event_UTC_time < ? '
            if end is None:
                end = dt.datetime.utcnow()
            if start is None:
                start = end - dt.timedelta(weeks=1)
            
            if start > end:
                raise Exception('Time range error')
            
            if configid is None:
                cur.execute(sql, (comment, user, start, end, ))
            else:
                sql += ' and service_config_id = ? '
                cur.execute(sql, (comment, user, start, end, configid, ))
        results = cur.fetchall()
    except sqlite3.Error, e:
        print ("Error %s" %e.args[0])
        raise
    
    results = [('service_event_id', 'service_config_id', 'service_event_user_tag', 'service_event_UTC_time', 'service_event_user_name'),] + results[:]
    return results

if __name__ == '__main__':
    import doctest
    doctest.testmod()
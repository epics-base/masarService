'''
Created on Dec 19, 2011

@author: shengb
'''
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sqlite3

from pymasar.utils import checkConnection
from pymasar.service.serviceevent import (saveServiceEvent, retrieveServiceEvents)

#define    DBF_STRING  0
#define    DBF_INT     1
#define    DBF_SHORT   1
#define    DBF_FLOAT   2
#define    DBF_ENUM    3
#define    DBF_CHAR    4
#define    DBF_LONG    5
#define    DBF_DOUBLE  6
epicsint    = [1, 4, 5]
epicsString = [0]
epicsDouble = [2, 6]

def saveMasar(conn, data, servicename=None, configname=None, comment=None):
    """
    save a snapshot (masar event) with data.
    The data format is a tuple array like [(pv_name, dbr_type, s_value, i_value, d_value, status, severity, ioc_timestamp, ioc_timestamp_nano)]
    Return service_event_id, masar_data_id[].
    
    >>> import sqlite3
    >>> from pymasar.service.service import (saveService, retrieveServices)
    >>> from pymasar.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs)
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
    >>> data = [('SR:C01-BI:G02A<BPM:L1>Pos-X',6, '', 0, 1.0e-4, 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G02A<BPM:L2>Pos-X', 6, '', 0, 1.2e-4, 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G04A<BPM:M1>Pos-X', 6, '', 0, 0.5e-4, 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G04B<BPM:M1>Pos-X', 6, '', 0, -1.0e-4,0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H1>Pos-X', 6, '', 0, -0.5e-4,0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H2>Pos-X', 6, '', 0, -0.8e-4,0, 0, 435686768234, 3452345098734)]
    >>> saveMasar(conn, data, servicename='masar1', configname='orbit C01', comment='a service event')
    (1, [1, 2, 3, 4, 5, 6])
    >>> data = [('SR:C01-BI:G02A<BPM:L1>Pos-X',6, '', 0, 1.0e-4, 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G02A<BPM:L2>Pos-X', 6, '', 0, 1.2e-4, 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G04A<BPM:M1>Pos-X', 6, '', 0, 0.5e-4, 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G04B<BPM:M1>Pos-X', 6, '', 0, -1.0e-4,0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H1>Pos-X', 6, '', 0, -0.5e-4,0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H2>Pos-X', 6, '', 0, -0.8e-4,0, 0, 564562342566, 3452345098734)]
    >>> saveMasar(conn, data, servicename='masar1', configname='orbit C01', comment='a service event')
    (2, [7, 8, 9, 10, 11, 12])
    >>> conn.close()
    """
    checkConnection(conn)
    eventid = saveServiceEvent(conn, servicename, configname, comment)
    masarid = None
    try:
        masarid = __saveMasarData(conn, eventid, data)
    except sqlite3.Error, e:
        print ('Error %s' %e.args[0])
        raise
    return eventid, masarid

def __saveMasarData(conn, eventid, datas):
    """
    save data of masar service, and associated those data with a given event id.
    The data format is a tuple array like [(pv_name, dbr_type, s_value, i_value, d_value, status, severity, ioc_timestamp, ioc_timestamp_nano)]
    Return masar_data_id[].
    
    """
    checkConnection(conn)
    
    sql = '''insert into masar_data 
    (masar_data_id, service_event_id, pv_name, dbr_type, s_value, i_value, d_value, status, severity, ioc_timestamp, ioc_timestamp_nano)
    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
    masarid = []
    try:
        cur = conn.cursor()
        for data in datas:
            cur.execute(sql, (None, eventid, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]))
            masarid.append(cur.lastrowid)
    except:
        raise 
    return masarid
    
def retrieveMasar(conn, eventid=None,start=None, end=None, comment=None):
    """
    retrieve masar service data with given time frame and comment.
    If end time is not given, use current time. If start time is not given, 
    get all data during past one week before end time.
    Both start time and end time should be in UTC time format.
    It returns data as a tuple array like below:
    service_event_user_tag, service_event_UTC_time, service_config_name, service_name
    [[('user tag', 'event UTC time', 'service config name', 'service name'),
    ('pv name label', 'dbr_type label', 'string value', 'int value', 'double value', 'status label', 'severity label', 'ioc time stamp label', 'ioc time stamp nano label')]
    [(pv_name data, dbr_type, s_value, i_value, d_value, status data, severity data, ioc_timestamp data, ioc_timestamp_nano data)
    (pv_name data, dbr_type, s_value, i_value, d_value, status data, severity data, ioc_timestamp data, ioc_timestamp_nano data)
    (pv_name data, dbr_type, s_value, i_value, d_value, status data, severity data, ioc_timestamp data, ioc_timestamp_nano data)
    (pv_name data, dbr_type, s_value, i_value, d_value, status data, severity data, ioc_timestamp data, ioc_timestamp_nano data)
    ...]
    ...
    ]
    
    >>> import sqlite3
    >>> from pymasar.service.service import (saveService, retrieveServices)
    >>> from pymasar.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs)
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
    >>> data = [('SR:C01-BI:G02A<BPM:L1>Pos-X',6, '', 0, 1.0e-4, 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G02A<BPM:L2>Pos-X', 6, '', 0, 1.2e-4, 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G04A<BPM:M1>Pos-X', 6, '', 0, 0.5e-4, 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G04B<BPM:M1>Pos-X', 6, '', 0, -1.0e-4,0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H1>Pos-X', 6, '', 0, -0.5e-4,0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H2>Pos-X', 6, '', 0, -0.8e-4,0, 0, 435686768234, 3452345098734)]
    >>> import datetime as dt
    >>> import time
    >>> start = dt.datetime.utcnow()
    >>> time.sleep(1.0) 
    >>> saveMasar(conn, data, servicename='masar1', configname='orbit C01', comment='a service event')
    (1, [1, 2, 3, 4, 5, 6])
    >>> data = [('SR:C01-BI:G02A<BPM:L1>Pos-X',6, '', 0, 1.0e-4, 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G02A<BPM:L2>Pos-X', 6, '', 0, 1.2e-4, 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G04A<BPM:M1>Pos-X', 6, '', 0, 0.5e-4, 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G04B<BPM:M1>Pos-X', 6, '', 0, -1.0e-4,0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H1>Pos-X', 6, '', 0, -0.5e-4,0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H2>Pos-X', 6, '', 0, -0.8e-4,0, 0, 564562342566, 3452345098734)]
    >>> time.sleep(1.0)
    >>> end1 = dt.datetime.utcnow()
    >>> time.sleep(1.0)
    >>> saveMasar(conn, data, servicename='masar1', configname='orbit C01', comment='a service event')
    (2, [7, 8, 9, 10, 11, 12])
    >>> time.sleep(1.0)
    >>> end2 = dt.datetime.utcnow()
    >>> datas = retrieveMasar(conn, start=start, end=end1)
    >>> print (datas[1][0][0], ',', datas[1][0][2], ',', datas[1][0][3])
    a service event , orbit C01 , masar1
    >>> for data in datas[1][1:]:
    ...    print (data)
    (u'SR:C01-BI:G02A<BPM:L1>Pos-X', 6, u'', 0, 0.0001, 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G02A<BPM:L2>Pos-X', 6, u'', 0, 0.00012, 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G04A<BPM:M1>Pos-X', 6, u'', 0, 5e-05, 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G04B<BPM:M1>Pos-X', 6, u'', 0, -0.0001, 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G06B<BPM:H1>Pos-X', 6, u'', 0, -5e-05, 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G06B<BPM:H2>Pos-X', 6, u'', 0, -8e-05, 0, 0, 435686768234L, 3452345098734L)
    >>> datasets = retrieveMasar(conn, start=start, end=end2)
    >>> for dataset in datasets[1:]:
    ...    print (dataset[0][0], ',', dataset[0][2], ',', dataset[0][3])
    ...    for data in dataset[1:]:
    ...        print (data)
    a service event , orbit C01 , masar1
    (u'SR:C01-BI:G02A<BPM:L1>Pos-X', 6, u'', 0, 0.0001, 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G02A<BPM:L2>Pos-X', 6, u'', 0, 0.00012, 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G04A<BPM:M1>Pos-X', 6, u'', 0, 5e-05, 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G04B<BPM:M1>Pos-X', 6, u'', 0, -0.0001, 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G06B<BPM:H1>Pos-X', 6, u'', 0, -5e-05, 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G06B<BPM:H2>Pos-X', 6, u'', 0, -8e-05, 0, 0, 435686768234L, 3452345098734L)
    a service event , orbit C01 , masar1
    (u'SR:C01-BI:G02A<BPM:L1>Pos-X', 6, u'', 0, 0.0001, 0, 0, 564562342566L, 3452345098734L)
    (u'SR:C01-BI:G02A<BPM:L2>Pos-X', 6, u'', 0, 0.00012, 0, 0, 564562342566L, 3452345098734L)
    (u'SR:C01-BI:G04A<BPM:M1>Pos-X', 6, u'', 0, 5e-05, 0, 0, 564562342566L, 3452345098734L)
    (u'SR:C01-BI:G04B<BPM:M1>Pos-X', 6, u'', 0, -0.0001, 0, 0, 564562342566L, 3452345098734L)
    (u'SR:C01-BI:G06B<BPM:H1>Pos-X', 6, u'', 0, -5e-05, 0, 0, 564562342566L, 3452345098734L)
    (u'SR:C01-BI:G06B<BPM:H2>Pos-X', 6, u'', 0, -8e-05, 0, 0, 564562342566L, 3452345098734L)
    >>> datasets = retrieveMasar(conn, start=end2)
    >>> print (datasets)
    [[(u'user tag', u'event UTC time', u'service config name', u'service name'), (u'pv_name', u'dbr_type', u's_value', u'i_value', u'd_value', u'status', u'severity', u'ioc_timestamp', u'ioc_timestamp_nano')]]
    >>> conn.close()
    """
    checkConnection(conn)
    dataset = []

    datahead = [[('user tag', 'event UTC time', 'service config name', 'service name'), 
                ('pv_name', 'dbr_type', 's_value', 'i_value', 'd_value', 'status', 'severity', 'ioc_timestamp', 'ioc_timestamp_nano')]]
    sql = '''
    select service_event_user_tag, service_event_UTC_time, service_config_name, service_name
    from service_event
    left join service_config using (service_config_id)
    left join service using (service_id)
    where service_event_id = ?
    '''

    if eventid:
        data= __retrieveMasarData(conn, eventid)
#        data = datahead + data[:]
        
        cur = conn.cursor()
        cur.execute(sql, (eventid,))
        result =cur.fetchall()
        data = result[:] + data[:]
        dataset.append(data)
    else:
        results = retrieveServiceEvents(conn, start=start, end=end, comment=comment)
#        print ("event retults = ", results)
        sql += ' and service_config_id = ?'
        for result in results[1:]:
            data= __retrieveMasarData(conn, result[0])
#            data = datahead + data[:]
    
            cur = conn.cursor()
            cur.execute(sql, (result[0], result[1],))
            result =cur.fetchall()
            data = result[:] + data[:]
            dataset.append(data)
    dataset = datahead[:] + dataset[:]
    return dataset

def __retrieveMasarData(conn, eventid):
    checkConnection(conn)
    sql = '''
    select pv_name, dbr_type, s_value, i_value, d_value, status, severity, ioc_timestamp, ioc_timestamp_nano from masar_data
    where service_event_id = ?
    '''
    data = None
    try:
        cur=conn.cursor()
        cur.execute(sql, (eventid,))
        data = cur.fetchall()
    except:
        raise
    return data

if __name__ == '__main__':
    import doctest
    doctest.testmod()
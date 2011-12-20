'''
Created on Dec 19, 2011

@author: shengb
'''
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sqlite3

from utils import checkConnection
from service.serviceevent import (saveServiceEvent, retrieveServiceEvents)

def saveMasar(conn, data, servicename=None, serviceconfigname=None, comment=None):
    """
    save a snapshot (masar event) with data.
    The data format is a tuple array like [(pv_name, value, status, severity, ioc_timestamp, ioc_timestamp_nano)]
    Return service_event_id, masar_data_id[].
    
    >>> import sqlite3
    >>> from service.service import (saveService, retrieveServices)
    >>> from service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs)
    >>> conn = sqlite3.connect(":memory:")
    >>> cur = conn.cursor()
    >>> SQL = '''CREATE TABLE "service" (
    ...        "service_id" INTEGER, 
    ...        "service_name" varchar(50) DEFAULT NULL, 
    ...        "service_desc" varchar(255) DEFAULT NULL, 
    ...        PRIMARY KEY ("service_id"));
    ...        CREATE TABLE "service_config" (
    ...        "service_config_id" INTEGER ,
    ...        "service_id" int(11) NOT NULL DEFAULT '0',
    ...        "service_config_name" varchar(50) DEFAULT NULL,
    ...        "service_config_desc" varchar(255) DEFAULT NULL,
    ...        "service_config_version" int(11) DEFAULT NULL,
    ...        "service_config_create_date" timestamp NOT NULL ,
    ...        PRIMARY KEY ("service_config_id")
    ...        CONSTRAINT "Ref_197" FOREIGN KEY ("service_id") REFERENCES "service" ("service_id") ON DELETE NO ACTION ON UPDATE NO ACTION
    ...        );
    ...        CREATE TABLE "service_event" (
    ...        "service_event_id" INTEGER ,
    ...        "service_config_id" int(11) NOT NULL DEFAULT '0',
    ...        "service_event_user_tag" varchar(255) DEFAULT NULL,
    ...        "service_event_UTC_time" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ...        "service_event_serial_tag" varchar(50) DEFAULT NULL,
    ...        PRIMARY KEY ("service_event_id")
    ...        CONSTRAINT "Ref_08" FOREIGN KEY ("service_config_id") REFERENCES "service_config" ("service_config_id") ON DELETE NO ACTION ON UPDATE NO ACTION
    ...        );
    ...        CREATE TABLE "masar_data" (
    ...        "masar_data_id" INTEGER ,
    ...        "service_event_id" int(11) NOT NULL DEFAULT '0',
    ...        "pv_name" varchar(50) DEFAULT NULL,
    ...        "value" varchar(50) DEFAULT NULL,
    ...        "status" int(11) DEFAULT NULL,
    ...        "severity" int(11) DEFAULT NULL,
    ...        "ioc_timestamp" int(11)  NOT NULL,
    ...        "ioc_timestamp_nano" int(11)  NOT NULL,
    ...        PRIMARY KEY ("masar_data_id")
    ...        CONSTRAINT "Ref_10" FOREIGN KEY ("service_event_id") REFERENCES "service_event" ("service_event_id") ON DELETE NO ACTION ON UPDATE NO ACTION
    ...        );'''
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
    >>> result = retrieveServiceConfigs(conn, servicename='masar1', serviceconfigname='orbit C01')
    >>> data = [('SR:C01-BI:G02A<BPM:L1>Pos-X', '1.0e-4', 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G02A<BPM:L2>Pos-X', '1.2e-4',  0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G04A<BPM:M1>Pos-X', '0.5e-4',  0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G04B<BPM:M1>Pos-X', '-1.0e-4', 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H1>Pos-X', '-0.5e-4', 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H2>Pos-X', '-0.8e-4', 0, 0, 435686768234, 3452345098734)]
    >>> saveMasar(conn, data, servicename='masar1', serviceconfigname='orbit C01', comment='a service event')
    (1, [1, 2, 3, 4, 5, 6])
    >>> data = [('SR:C01-BI:G02A<BPM:L1>Pos-X', '1.0e-4', 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G02A<BPM:L2>Pos-X', '1.2e-4',  0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G04A<BPM:M1>Pos-X', '0.5e-4',  0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G04B<BPM:M1>Pos-X', '-1.0e-4', 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H1>Pos-X', '-0.5e-4', 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H2>Pos-X', '-0.8e-4', 0, 0, 564562342566, 3452345098734)]
    >>> saveMasar(conn, data, servicename='masar1', serviceconfigname='orbit C01', comment='a service event')
    (2, [7, 8, 9, 10, 11, 12])
    >>> conn.close()
    """
    checkConnection(conn)
    eventid = saveServiceEvent(conn, servicename, serviceconfigname, comment)
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
    The data format is a tuple array like [(pv_name, value, status, severity, ioc_timestamp, ioc_timestamp_nano)]
    Return masar_data_id[].
    
    >>> import sqlite3
    >>> from service.service import (saveService, retrieveServices)
    >>> from service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs)
    >>> conn = sqlite3.connect(":memory:")
    >>> cur = conn.cursor()
    >>> SQL = '''CREATE TABLE "service" (
    ...        "service_id" INTEGER, 
    ...        "service_name" varchar(50) DEFAULT NULL, 
    ...        "service_desc" varchar(255) DEFAULT NULL, 
    ...        PRIMARY KEY ("service_id"));
    ...        CREATE TABLE "service_config" (
    ...        "service_config_id" INTEGER ,
    ...        "service_id" int(11) NOT NULL DEFAULT '0',
    ...        "service_config_name" varchar(50) DEFAULT NULL,
    ...        "service_config_desc" varchar(255) DEFAULT NULL,
    ...        "service_config_version" int(11) DEFAULT NULL,
    ...        "service_config_create_date" timestamp NOT NULL ,
    ...        PRIMARY KEY ("service_config_id")
    ...        CONSTRAINT "Ref_197" FOREIGN KEY ("service_id") REFERENCES "service" ("service_id") ON DELETE NO ACTION ON UPDATE NO ACTION
    ...        );
    ...        CREATE TABLE "service_event" (
    ...        "service_event_id" INTEGER ,
    ...        "service_config_id" int(11) NOT NULL DEFAULT '0',
    ...        "service_event_user_tag" varchar(255) DEFAULT NULL,
    ...        "service_event_UTC_time" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ...        "service_event_serial_tag" varchar(50) DEFAULT NULL,
    ...        PRIMARY KEY ("service_event_id")
    ...        CONSTRAINT "Ref_08" FOREIGN KEY ("service_config_id") REFERENCES "service_config" ("service_config_id") ON DELETE NO ACTION ON UPDATE NO ACTION
    ...        );
    ...        CREATE TABLE "masar_data" (
    ...        "masar_data_id" INTEGER ,
    ...        "service_event_id" int(11) NOT NULL DEFAULT '0',
    ...        "pv_name" varchar(50) DEFAULT NULL,
    ...        "value" varchar(50) DEFAULT NULL,
    ...        "status" int(11) DEFAULT NULL,
    ...        "severity" int(11) DEFAULT NULL,
    ...        "ioc_timestamp" int(11)  NOT NULL,
    ...        "ioc_timestamp_nano" int(11)  NOT NULL,
    ...        PRIMARY KEY ("masar_data_id")
    ...        CONSTRAINT "Ref_10" FOREIGN KEY ("service_event_id") REFERENCES "service_event" ("service_event_id") ON DELETE NO ACTION ON UPDATE NO ACTION
    ...        );'''
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
    >>> result = retrieveServiceConfigs(conn, servicename='masar1', serviceconfigname='orbit C01')
    >>> data = [('SR:C01-BI:G02A<BPM:L1>Pos-X', '1.0e-4', 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G02A<BPM:L2>Pos-X', '1.2e-4',  0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G04A<BPM:M1>Pos-X', '0.5e-4',  0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G04B<BPM:M1>Pos-X', '-1.0e-4', 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H1>Pos-X', '-0.5e-4', 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H2>Pos-X', '-0.8e-4', 0, 0, 435686768234, 3452345098734)]
    >>> saveMasar(conn, data, servicename='masar1', serviceconfigname='orbit C01', comment='a service event')
    (1, [1, 2, 3, 4, 5, 6])
    >>> data = [('SR:C01-BI:G02A<BPM:L1>Pos-X', '1.0e-4', 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G02A<BPM:L2>Pos-X', '1.2e-4',  0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G04A<BPM:M1>Pos-X', '0.5e-4',  0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G04B<BPM:M1>Pos-X', '-1.0e-4', 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H1>Pos-X', '-0.5e-4', 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H2>Pos-X', '-0.8e-4', 0, 0, 564562342566, 3452345098734)]
    >>> saveMasar(conn, data, servicename='masar1', serviceconfigname='orbit C01', comment='a service event')
    (2, [7, 8, 9, 10, 11, 12])
    >>> conn.close()
    """
    checkConnection(conn)
    
    sql = '''insert into masar_data 
    (masar_data_id, service_event_id, pv_name, value, status, severity, ioc_timestamp, ioc_timestamp_nano)
    values (?, ?, ?, ?, ?, ?, ?, ?) '''
    masarid = []
    try:
        cur = conn.cursor()
        for data in datas:
            cur.execute(sql, (None, eventid, data[0], data[1], data[2], data[3], data[4], data[5]))
            masarid.append(cur.lastrowid)
    except:
        raise 
    return masarid
    
def retrieveMasar(conn, start=None, end=None, comment=None):
    """
    retrieve masar service data with given time frame and comment.
    If end time is not given, use current time. If start time is not given, 
    get all data during past one week before end time.
    Both start time and end time should be in UTC time format.
    It returns data as a tuple array like below:
    service_event_user_tag, service_event_UTC_time, service_config_name, service_name
    [('user tag', 'event UTC time', 'service config name', 'service name'),
    ('pv name label', 'value label', 'status label', 'severity label', 'ioc time stamp label', 'ioc time stamp nano label'),
    (pv_name data, value data, status data, severity data, ioc_timestamp data, ioc_timestamp_nano data)
    (pv_name data, value data, status data, severity data, ioc_timestamp data, ioc_timestamp_nano data)
    (pv_name data, value data, status data, severity data, ioc_timestamp data, ioc_timestamp_nano data)
    (pv_name data, value data, status data, severity data, ioc_timestamp data, ioc_timestamp_nano data)
    ...
    ]
    
    >>> import sqlite3
    >>> from service.service import (saveService, retrieveServices)
    >>> from service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs)
    >>> conn = sqlite3.connect(":memory:")
    >>> cur = conn.cursor()
    >>> SQL = '''CREATE TABLE "service" (
    ...        "service_id" INTEGER, 
    ...        "service_name" varchar(50) DEFAULT NULL, 
    ...        "service_desc" varchar(255) DEFAULT NULL, 
    ...        PRIMARY KEY ("service_id"));
    ...        CREATE TABLE "service_config" (
    ...        "service_config_id" INTEGER ,
    ...        "service_id" int(11) NOT NULL DEFAULT '0',
    ...        "service_config_name" varchar(50) DEFAULT NULL,
    ...        "service_config_desc" varchar(255) DEFAULT NULL,
    ...        "service_config_version" int(11) DEFAULT NULL,
    ...        "service_config_create_date" timestamp NOT NULL ,
    ...        PRIMARY KEY ("service_config_id")
    ...        CONSTRAINT "Ref_197" FOREIGN KEY ("service_id") REFERENCES "service" ("service_id") ON DELETE NO ACTION ON UPDATE NO ACTION
    ...        );
    ...        CREATE TABLE "service_event" (
    ...        "service_event_id" INTEGER ,
    ...        "service_config_id" int(11) NOT NULL DEFAULT '0',
    ...        "service_event_user_tag" varchar(255) DEFAULT NULL,
    ...        "service_event_UTC_time" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ...        "service_event_serial_tag" varchar(50) DEFAULT NULL,
    ...        PRIMARY KEY ("service_event_id")
    ...        CONSTRAINT "Ref_08" FOREIGN KEY ("service_config_id") REFERENCES "service_config" ("service_config_id") ON DELETE NO ACTION ON UPDATE NO ACTION
    ...        );
    ...        CREATE TABLE "masar_data" (
    ...        "masar_data_id" INTEGER ,
    ...        "service_event_id" int(11) NOT NULL DEFAULT '0',
    ...        "pv_name" varchar(50) DEFAULT NULL,
    ...        "value" varchar(50) DEFAULT NULL,
    ...        "status" int(11) DEFAULT NULL,
    ...        "severity" int(11) DEFAULT NULL,
    ...        "ioc_timestamp" int(11)  NOT NULL,
    ...        "ioc_timestamp_nano" int(11)  NOT NULL,
    ...        PRIMARY KEY ("masar_data_id")
    ...        CONSTRAINT "Ref_10" FOREIGN KEY ("service_event_id") REFERENCES "service_event" ("service_event_id") ON DELETE NO ACTION ON UPDATE NO ACTION
    ...        );'''
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
    >>> result = retrieveServiceConfigs(conn, servicename='masar1', serviceconfigname='orbit C01')
    >>> data = [('SR:C01-BI:G02A<BPM:L1>Pos-X', '1.0e-4', 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G02A<BPM:L2>Pos-X', '1.2e-4',  0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G04A<BPM:M1>Pos-X', '0.5e-4',  0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G04B<BPM:M1>Pos-X', '-1.0e-4', 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H1>Pos-X', '-0.5e-4', 0, 0, 435686768234, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H2>Pos-X', '-0.8e-4', 0, 0, 435686768234, 3452345098734)]
    >>> import datetime as dt
    >>> import time
    >>> start = dt.datetime.utcnow()
    >>> time.sleep(1.0) 
    >>> saveMasar(conn, data, servicename='masar1', serviceconfigname='orbit C01', comment='a service event')
    (1, [1, 2, 3, 4, 5, 6])
    >>> data = [('SR:C01-BI:G02A<BPM:L1>Pos-X', '1.0e-4', 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G02A<BPM:L2>Pos-X', '1.2e-4',  0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G04A<BPM:M1>Pos-X', '0.5e-4',  0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G04B<BPM:M1>Pos-X', '-1.0e-4', 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H1>Pos-X', '-0.5e-4', 0, 0, 564562342566, 3452345098734),
    ...        ('SR:C01-BI:G06B<BPM:H2>Pos-X', '-0.8e-4', 0, 0, 564562342566, 3452345098734)]
    >>> time.sleep(1.0)
    >>> end1 = dt.datetime.utcnow()
    >>> time.sleep(1.0)
    >>> saveMasar(conn, data, servicename='masar1', serviceconfigname='orbit C01', comment='a service event')
    (2, [7, 8, 9, 10, 11, 12])
    >>> time.sleep(1.0)
    >>> end2 = dt.datetime.utcnow()
    >>> datas = retrieveMasar(conn, start=start, end=end1)
    >>> print (datas[0][0][0], ',', datas[0][0][2], ',', datas[0][0][3])
    a service event , orbit C01 , masar1
    >>> for data in datas[0][1:]:
    ...    print (data)
    (u'pv_name', u'value', u'status', u'severity', u'ioc_timestamp', u'ioc_timestamp_nano')
    (u'SR:C01-BI:G02A<BPM:L1>Pos-X', u'1.0e-4', 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G02A<BPM:L2>Pos-X', u'1.2e-4', 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G04A<BPM:M1>Pos-X', u'0.5e-4', 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G04B<BPM:M1>Pos-X', u'-1.0e-4', 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G06B<BPM:H1>Pos-X', u'-0.5e-4', 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G06B<BPM:H2>Pos-X', u'-0.8e-4', 0, 0, 435686768234L, 3452345098734L)
    >>> datasets = retrieveMasar(conn, start=start, end=end2)
    >>> for dataset in datasets:
    ...    print (dataset[0][0], ',', dataset[0][2], ',', dataset[0][3])
    ...    for data in dataset[1:]:
    ...        print (data)
    a service event , orbit C01 , masar1
    (u'pv_name', u'value', u'status', u'severity', u'ioc_timestamp', u'ioc_timestamp_nano')
    (u'SR:C01-BI:G02A<BPM:L1>Pos-X', u'1.0e-4', 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G02A<BPM:L2>Pos-X', u'1.2e-4', 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G04A<BPM:M1>Pos-X', u'0.5e-4', 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G04B<BPM:M1>Pos-X', u'-1.0e-4', 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G06B<BPM:H1>Pos-X', u'-0.5e-4', 0, 0, 435686768234L, 3452345098734L)
    (u'SR:C01-BI:G06B<BPM:H2>Pos-X', u'-0.8e-4', 0, 0, 435686768234L, 3452345098734L)
    a service event , orbit C01 , masar1
    (u'pv_name', u'value', u'status', u'severity', u'ioc_timestamp', u'ioc_timestamp_nano')
    (u'SR:C01-BI:G02A<BPM:L1>Pos-X', u'1.0e-4', 0, 0, 564562342566L, 3452345098734L)
    (u'SR:C01-BI:G02A<BPM:L2>Pos-X', u'1.2e-4', 0, 0, 564562342566L, 3452345098734L)
    (u'SR:C01-BI:G04A<BPM:M1>Pos-X', u'0.5e-4', 0, 0, 564562342566L, 3452345098734L)
    (u'SR:C01-BI:G04B<BPM:M1>Pos-X', u'-1.0e-4', 0, 0, 564562342566L, 3452345098734L)
    (u'SR:C01-BI:G06B<BPM:H1>Pos-X', u'-0.5e-4', 0, 0, 564562342566L, 3452345098734L)
    (u'SR:C01-BI:G06B<BPM:H2>Pos-X', u'-0.8e-4', 0, 0, 564562342566L, 3452345098734L)
    >>> datasets = retrieveMasar(conn, start=end2)
    >>> print (datasets)
    []
    >>> conn.close()
    """
    checkConnection(conn)
    results = retrieveServiceEvents(conn, start=start, end=end, comment=comment)
    dataset = []
    for result in results:
        data= __retrieveMasarData(conn, result[0])
        sql = '''
        select service_event_user_tag, service_event_UTC_time, service_config_name, service_name
        from service_event
        left join service_config using (service_config_id)
        left join service using (service_id)
        where service_event_id = ? and service_config_id = ?
        '''
        data = [('pv_name', 'value', 'status', 'severity', 'ioc_timestamp', 'ioc_timestamp_nano')] + data[:]

        cur = conn.cursor()
        cur.execute(sql, (result[0], result[1],))
        result =cur.fetchall()
        data = result[:] + data[:]
        dataset.append(data)
    return dataset

def __retrieveMasarData(conn, eventid):
    checkConnection(conn)
    sql = '''
    select pv_name, value, status, severity, ioc_timestamp, ioc_timestamp_nano from masar_data
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
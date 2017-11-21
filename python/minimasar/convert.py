# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 11:19:06 2017

@author: Michael Dalesio
"""

import logging
_log = logging.getLogger(__name__)

import sqlite3 as sqlite
from db import connect, encodeValue, ConcatUnique
from ops import normtime
import pickle, json

def getargs():
    from argparse import ArgumentParser
    P = ArgumentParser()
    P.add_argument('source', help='File name of source sqlite .db file')
    P.add_argument('target', help='File name of target sqlite .db file')
    P.add_argument('-L', '--log-level', default='INFO', help='Level name (eg. ERROR, WARN, INFO, DEBUG)')
    return P.parse_args()

def configEntry (config):
    _log.debug("configEntry() config name: %s", config['service_config_name'])
    
    """SELECT service_config_name, service_config_create_date, 
            service_config_desc, service_config_status, service_config_id
       FROM service_config"""
    
    if config['service_config_status'] == 'active': 
        active = 1
    else:     
        active = 0

    ret = {
        'name': config['service_config_name'],
        'created': normtime(config['service_config_create_date']),
        'active': active,
        'desc': config['service_config_desc'],
        'system': None,
        'oldid': config['service_config_id']
            }

    return ret

def configAdd (config, cTarget):
    _log.debug("configAdd() service_config_id: %s", config['oldid'])
    
    """
    id	*auto*	INTEGER
    name	service_config\service_config_name	TEXT
    next	TEXT	REFERENCE config(id)
    created	service_config\service_config_create_date	TEXT
    active		INTEGER
    desc	service_config\service_config_desc	TEXT
    system	TEXT	TEXT
    """
    
    cTarget.execute("""
            INSERT INTO config(name, created, active, desc, system)
            VALUES (:name, :created, :active, :desc, :system)
            """, config)
    return cTarget.lastrowid
    
def pvEntry (pv, config):
    _log.debug("pvEntry() pv_id: %s", pv['pv_id'])
    
    """
    SELECT pv.pv_id, pv.pv_name, 
        pvgroup__serviceconfig.service_config_id,
        group_concat(pv_group.pv_group_name) AS pv_group_name
    FROM pv
        JOIN pv__pvgroup
            ON pv.pv_id = pv__pvgroup.pv_id
        JOIN pv_group
            ON pv__pvgroup.pv_group_id = pv_group.pv_group_id
        JOIN pvgroup__serviceconfig
            ON pv_group.pv_group_id = pvgroup__serviceconfig.pv_group_id
    WHERE pvgroup__serviceconfig.service_config_id=?
    GROUP BY pv.pv_id  
    """    
    
    ret = {
        'config': config, 
        'name': pv['pv_name'],
        'groupName': pv['pv_group_name'],
        'oldid': pv['pv_id']
    }
    
    return ret

def pvAdd (pv, cTarget):
    _log.debug("pvAdd() pv_id: %s", pv['oldid'])
  
    """  
    id	*auto*	INTEGER
    config	_config\id_	REFERENCES config(id)
    name	pv\pv_name	TEXT
    tags		TEXT
    groupName	pv_group\pv_group_name	TEXT
    readonly	INT	INT
    """
    
    cTarget.execute("""
        INSERT INTO config_pv(config, name, groupName)
        VALUES (:config, :name, :groupName)
        """, pv)
            
    return cTarget.lastrowid

def eventEntry (event, config):
    _log.debug("eventEntry() service_event_id: %s", event['service_event_id'])    
    
    """
    SELECT service_event_UTC_time,
        service_event_user_name,
        service_event_user_tag,
        service_event_approval,
        service_event_id
    FROM service_event
    WHERE service_config_id=?    
    """
    
    ret = {
        'config': config,
        'created': normtime(event['service_event_UTC_time']),
        'user': event['service_event_user_name'],
        'comment': event['service_event_user_tag'],
        'approve': event['service_event_approval'],
        'oldid': event['service_event_id']
    }
    
    return ret

def eventAdd (event, cTarget):
    _log.debug("eventAdd() service_event_id: %s", event['oldid'])
    
    """
    id	*auto*	INTEGER
    config	_config\id_	REFERENCES config(id)
    created	service_event\service_event_UTC_time	TEXT
    user	service_event\service_event_user_name	TEXT
    comment		TEXT
    approve	service_event\service_event_approval	INTEGER
    """
    
    cTarget.execute("""
        INSERT INTO event(config, created, user, approve, comment)
        VALUES (:config, :created, :user, :approve, :comment)
        """, event)
    
    return cTarget.lastrowid

def eventpvEntry (masar, pvid, eventid):
    _log.debug("eventpvEntry() masar_data_id: %s", masar['masar_data_id'])
    
    """
    SELECT dbr_type, severity, status, ioc_timestamp,
        ioc_timestamp_nano, dbr_type, d_value, s_value, l_value,
        is_array, array_value, pv_name, masar_data_id
    FROM masar_data
    WHERE service_event_id=?    
    """    
    
    if masar['is_array'] == 1:
        value = pickle.loads(masar['array_value'])
    else:
        if masar['dbr_type'] in [0,3]: value = masar['s_value']
        elif masar['dbr_type'] in [2,6]: value = masar['d_value']
        else: value = masar['l_value']

    value = encodeValue(value)
 
    ret = {
        'event': eventid,
        'pv': pvid,
        'dtype':masar['dbr_type'],
        'severity': masar['severity'],
        'status': masar['status'],
        'time': masar['ioc_timestamp'],
        'timens': masar['ioc_timestamp_nano'],
        'value': value,
        'oldid': masar['masar_data_id']
    }
    
    return ret
    
def eventpvAdd (eventpvs, cTarget):
    
    """
    id	*auto*	INTEGER
    event	_event\id_	REFERENCES event(id)
    pv	pv\pv_name	INTEGER
    dtype	masar_data\dbr_type	INTEGER
    severity	masar_data\severity	INTEGER
    status	masar_data\status	INTEGER
    time	masar_data\ioc_timestamp	INTEGER
    timens	masar_data\ioc_timestamp_nano	INTEGER
    value	masar_data\d_value, s_value, l_value, array_value	TEXT
    """
    
    cTarget.executemany("""
        INSERT INTO event_pv(event, pv, dtype, severity, status, time, timens, value)
        VALUES (:event, :pv, :dtype, :severity, :status, :time, :timens, :value)
        """, eventpvs)
    
    return cTarget.lastrowid
    
def main(args):
    lvl = logging.getLevelName(args.log_level)
    if isinstance(lvl, str):
        raise ValueError("Bad level name, must be eg. ERROR, WARN, INFO, DEBUG")

    logging.basicConfig(level=lvl)

    connSource = sqlite.connect(args.source)
    connSource.row_factory = sqlite.Row
    connSource.create_aggregate('py_concat_unique', 1, ConcatUnique)

    connTarget = connect(args.target)
    cTarget = connTarget.cursor()
    
    pv_missing = 0 

    try:
        numconf, = connSource.execute('select count(*) from service_config').fetchone()
        
        # Loop through all configurations
        for confn, ServiceConfig in enumerate(connSource.execute("""
            SELECT service_config_name, service_config_create_date, 
                service_config_desc, service_config_status, service_config_id
            FROM service_config
            """).fetchall()):
            print 'config %s %d/%d'%(ServiceConfig['service_config_name'], confn, numconf)
 
             # Build config entry, enter it, return new id (needed by config_pv and event)
            newConfigID = configAdd(configEntry(ServiceConfig), cTarget)

            name2id = {}

            # Loop through all pVs in config          
            for pv in connSource.execute("""
                SELECT pv.pv_id, pv.pv_name, 
                    pvgroup__serviceconfig.service_config_id,
                    py_concat_unique(pv_group.pv_group_name) AS pv_group_name
                FROM pv
                    JOIN pv__pvgroup
                        ON pv.pv_id = pv__pvgroup.pv_id
                    JOIN pv_group
                        ON pv__pvgroup.pv_group_id = pv_group.pv_group_id
                    JOIN pvgroup__serviceconfig
                        ON pv_group.pv_group_id = pvgroup__serviceconfig.pv_group_id
                WHERE pvgroup__serviceconfig.service_config_id=?
                GROUP BY pv.pv_id
                """, (ServiceConfig['service_config_id'],)).fetchall():

                # print ('p', end='') 
                name2id[pv['pv_name']] = pvAdd(pvEntry(pv, newConfigID), cTarget)
                
            for eventn, event in enumerate(connSource.execute("""
                SELECT service_event_UTC_time,
                    service_event_user_name,
                    service_event_user_tag,
                    service_event_approval,
                    service_event_id
                FROM service_event
                WHERE service_config_id=?
                """, (ServiceConfig['service_config_id'], )).fetchall()):

                if eventn%20==0:
                    print 'event', eventn

                newEventID = eventAdd(eventEntry(event, newConfigID), cTarget)

                rows = []

                for masar in connSource.execute("""
                    SELECT dbr_type, severity, status, ioc_timestamp,
                        ioc_timestamp_nano, dbr_type, d_value, s_value, l_value,
                        is_array, array_value, pv_name, masar_data_id
                    FROM masar_data
                    WHERE service_event_id=?
                    """, (event['service_event_id'],)).fetchall():
                    
                    # convert pv_name to new pv id number
                    newpvID = name2id.get(masar['pv_name'])

                    if newpvID is None:
                        print ("Warning: {} exists in the masar_data table, but not in the pv table".format(masar['pv_name']))
                        pv_missing += 1
                    else:
                        rows.append(eventpvEntry (masar, newpvID, newEventID))

                eventpvAdd (rows, cTarget)

    finally:
        connTarget.commit()
        connTarget.close()
        connSource.close()
        print("Connections closed.")
        print("{} PVs exist in masar_data table, but not in pv table".format(pv_missing))
        
if __name__=='__main__':
    main(getargs())

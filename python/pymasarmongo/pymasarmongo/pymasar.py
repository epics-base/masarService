"""
Created on Jul 28, 2014

@author: shengb
"""

import time
from collections import OrderedDict

import pymongo

__configdb = "service_config"
__eventdb = "service_event"


def counter(conn, collection, name, idx=None):
    """Create a counter document, which gives an auto increment id.
    
    :param conn: MongoDB connection object
    :type conn: object
    
    :param collection: MongoDB collection name
    :type collection: str

    :param name: configuration name, which should be unique in the whole database
    :type name: str
    
    :param idx: update current counter to this index number, which is mainly for migrating a SQL database.
    :type name: int
    
    """
    collectdoc = conn[collection]["counters"]
    ret = collectdoc.find({"_id": name})
    if ret.count() == 0:
        collectdoc.insert({"_id": name, "idx": 0})
        #collectdoc.ensure_index("_id", unique=True)
        #collectdoc.create_index("_id", unique=True)
    if idx is None:
        ret = collectdoc.find_and_modify(query={'_id': name}, update={"$inc": {'idx': 1}}, upsert=False, full_response=True)
        if ret:
            idx = collectdoc.find({"_id": name}, {"idx": 1, "_id": 0}).limit(1)[0]["idx"]
        else:
            raise RuntimeError("Cannot identify unique index number")
    else:
        ret = collectdoc.update({'_id': name}, {"$set": {'idx': idx}}, upsert=False, full_response=True)
        if not ret:
            raise RuntimeError("Cannot identify unique index number")
    return idx


def saveconfig(conn, collection, name, **kwds):
    """Save a new MASAR configuration entity.
    
    :param conn: MongoDB connection object
    :type conn: object
    
    :param collection: MongoDB collection name
    :type collection: str

    :param name: configuration name, which should be unique in the whole database
    :type name: str
    
    :param desc: description for this configuration which could be null, or with 255 characters. 
    :type desc: str

    :param configidx: index number for this configuration, which is auto increased sequence number
    :type desc: int

    :param system: system name with up to 255 characters, which is "all" by default. 
    :type system: str

    :param status: either active or inactive, which presents the configuration status
    :type param: str
    
    :param version: version number, which is an integer
    :type version: int
    
    :param pvlist: a Python dictionary to host all pvs belong to this configuration if it is given
    
             with structure as::
             
                 {"names": [],
                  "descs": []
                 }
                 
    :type pvlist: dict
    
    :returns: id of new configuration
    
    :raises: KeyError, RuntimeError
    
    """
    pvlist = kwds.get("pvlist", OrderedDict())
    if not isinstance(pvlist, dict):
        raise ValueError("pvlist has to be a Python dictionary.")
    if pvlist:
        assert "names" in pvlist.keys()

    entry = retrieveconfig(conn, collection, name=name)
    if len(entry) != 0:
        raise ValueError("Configuration (%s) exists already."%name)

    desc = kwds.get("desc", None)
    status = kwds.get("status", "active")
    if status not in ["active", "inactive"]:
        raise ValueError("Status has to be either active or inactive.")
    system = kwds.get("system", None)
    version = kwds.get("version", None)
    cidx = kwds.get("configidx", None)
    date = kwds.get("created_on", None)
    configdoc = conn[collection][__configdb]
    if date is None:
        confid = configdoc.insert({"configidx": counter(conn, collection, __configdb, idx=cidx),
                                   "name": name,
                                   "desc": desc,
                                   "system": system,
                                   "status": status,
                                   "version": version,
                                   "created_on": time.strftime("%Y-%m-%d %H:%M:%S"),
                                   "pvlist": pvlist})
    else:
        confid = configdoc.insert({"configidx": counter(conn, collection, __configdb, idx=cidx),
                                   "name": name,
                                   "desc": desc,
                                   "system": system,
                                   "status": status,
                                   "version": version,
                                   "created_on": date,
                                   "pvlist": pvlist})
    configdoc.ensure_index([("configidx", pymongo.DESCENDING)], background=True, unique=True)
    configdoc.ensure_index([("name", pymongo.DESCENDING)], background=True, unique=True)
    #configdoc.ensure_index(("cid", pymongo.DESCENDING), background=True, unique=True)
    return confid


def updateconfig(conn, collection, name, **kwds):
    """Update an existing MASAR configuration according given name.
    
    :param conn: MongoDB connection object
    :type conn: object
    
    :param collection: MongoDB collection name
    :type collection: str

    :param name: configuration name, which should be unique in the whole database
    :type name: str
    
    :param configidx: index number for this configuration, which is auto increased sequence number
    :type desc: int

    :param desc: description for this configuration which could be null, or with 255 characters.
    :type desc: str

    :param system: system name with up to 255 characters, which is "all" by default. 
    :type system: str

    :param status: either active or inactive, which presents the configuration status
    :type param: str
    
    :param version: version number, which is an integer
    :type version: int
    
    :param pvlist: a Python dictionary to host all pvs belong to this configuration if it is given
    
             with structure as::
             
                 {"names": [],
                  "descs": []
                 }
                 
    :type pvlist: dict
    
    :returns: True if updated successfully
    
    :raises: KeyError, RuntimeError

    """
    
    desc = kwds.get("desc", None)
    status = kwds.get("status", None)
    if status is not None and status not in ["active", "inactive"]:
        raise ValueError("Status has to be either active or inactive.")
    system = kwds.get("system", None)
    version = kwds.get("version", None)
    pvlist = kwds.get("pvlist", None)
    configidx = kwds.get("configidx", None)

    if name is None and configidx:
        raise RuntimeError("Cannot identify configuration to update.")

    res = retrieveconfig(conn, collection, name=name, configidx=configidx)
    if len(res) != 1:
        raise RuntimeError("Wrong Mongo document for %s" % name)
    pvlist0 = res[0]["pvlist"]
    if pvlist0 and pvlist is not None and pvlist0 != pvlist:
        raise RuntimeError("PV collection list exists already, and should not be changed.")
    
    params = {}
    if desc is not None:
        params.update({"desc": desc})
    if status is not None:
        params.update({"status": status})
    if system is not None:
        params.update({"system": system})
    if version is not None:
        params.update({"version": version})
    if pvlist is not None and pvlist and isinstance(pvlist, dict):
        if "names" not in pvlist.keys():
            raise KeyError('Cannot find key ("names") for pv names.')
        params.update({"pvlist": pvlist})
    params.update({"updated_on": time.strftime("%Y-%m-%d %H:%M:%S")})
    conn[collection][__configdb].update({"_id": res[0]["_id"]},
                                        {"$set": params},
                                        upsert=False)
    return True
    

def retrieveconfig(conn, collection, name=None, system=None, status=None, configidx=None, eventidx=None, withpvs=False):
    """Retrieve a MASAR configuration according given name, or system name.
    Wildcard is supported:
        * for matching characters matching
    
    :param conn: MongoDB connection object
    :type conn: object
    
    :param collection: MongoDB collection name
    :type collection: str

    :param configidx: index number for this configuration, which is auto increased sequence number
    :type desc: int

    :param eventidx: event index number, only get configuration that this event belongs to
    :type desc: int

    :param name: configuration name, which should be unique in the whole database
    :type name: str

    :param system: system name with up to 255 characters, which is "all" by default. 
    :type system: str

    :param status: either active or inactive, which presents the configuration status
    :type param: str

    :param withpvs: flag to identify whether to get pvs
    :type withpvs: bool

    :returns: list of masar configuration

        each configuration has structure like: ::

            {'_id': ,                   #id number generated by mongodb
             'configidx': ,             #index number sequence increased
             'name':  ,                 # name of this configuration
             'desc': ,                  # brief description
             'pvlist': {"names": [],
                        "descs": [] },  # pv list dictionary
             'status': ,                # active/inactive
             'system': ,                # system name
             'version': ,               # version number
             'created_on': ,            # created date
             'updated_on': ,            # last updated date
             }

    :raises: RuntimeError
    
    """
    if not conn.alive():
        raise RuntimeError("MongoDB connection is inactive.")

    query = {}
    if eventidx is not None:
        configs = list(conn[collection][__eventdb].find({"eventidx": eventidx}, {"configidx": 1}))
        if len(configs) != 0:
            query['configidx'] = configs[0]["configidx"]
        else:
            return configs
    else:
        if configidx is not None:
            query.update({"configidx": configidx})
        if name is not None:
            if "*" in name:
                query.update({"name": {'$regex': "^"+name.replace("*", ".*"), '$options': 'i'}})
            else:
                query.update({"name": name})
        if system is not None:
            if "*" in system:
                query.update({"system": {'$regex': "^"+system.replace("*", ".*"), '$options': 'i'}})
            else:
                query.update({"system": system})
        if status is not None and status in ["active", "inactive"]:
            query.update({"status": status})

    if withpvs:
        return list(conn[collection][__configdb].find(query))
    else:
        return list(conn[collection][__configdb].find(query, {"pvlist": 0}))


def retrieveevents(conn, collection, **kwds):
    """Retrieve event header information.
    Save a new MASAR event with data.

    :param conn: MongoDB connection object
    :type conn: object

    :param collection: MongoDB collection name
    :type collection: str

    :param configidx: configuration index number which this data set refers to
    :type desc: int

    :param eventidx: event index number, which is None by default. For database migration purpose.
    :type desc: int

    :param comment: a brief comments of this data set.
    :type desc: str

    :param approval: status if this data set, approved or not.
    :type system: bool

    :param username: user name, which refers who saved this data set
    :type param: str

    :param start: start time for time window based search.
    :type start: str

    :param end: end time for time window based search.
    :type end: str

             time string format: "%Y-%m-%d %H:%M:%S", for example "2012-03-29 18:47:44"

    :returns: event header information

    :raises: KeyError, RuntimeError

    """

    if not conn.alive():
        raise RuntimeError("MongoDB connection is inactive.")

    configid = kwds.get("configidx", None)
    eventidx = kwds.get("eventidx", None)
    start = kwds.get("start", None)
    end = kwds.get("end", None)
    comment = kwds.get("comment", None)
    user = kwds.get("username", None)
    
    query = {}
    if comment is not None:
        if "*" in comment:
            query.update({"comment": {'$regex': "^"+comment.replace("*", ".*"), '$options': 'i'}})
        else:
            query.update({"comment": comment})
    if user is not None:
        if "*" in user:
            query.update({"username": {'$regex': "^"+user.replace("*", ".*"), '$options': 'i'}})
        else:
            query.update({"username": user})
    if "approval" in kwds.keys():
        query.update({"approval": bool(kwds.get("approval", True))})
    if start is not None and end is not None:
        query.update({"created_on": {"$gte": start, "$lte": end}})
    elif start is not None:
        query.update({"created_on": {"$gte": start}})
    elif end is not None:
        query.update({"created_on": {"$lte": end}})
    
    if configid is not None:
        if isinstance(configid, (list, tuple)):
            query.update({"configidx": {"$in": configid}})
        else:
            query.update({"configidx": configid})

    if eventidx is not None:
        if isinstance(eventidx, (list, tuple)):
            query.update({"eventidx": {"$in": eventidx}})
        else:
            query.update({"eventidx": eventidx})
    return list(conn[collection][__eventdb].find(query, {'masar_data': 0}))
    

def retrievesnapshot(conn, collection, eventidx):
    """Retrieve MASAR event data.

    :param conn: MongoDB connection object
    :type conn: object

    :param collection: MongoDB collection name
    :type collection: str

    :param eventidx: event index number, which is None by default. For database migration purpose.
    :type eventidx: int

    :returns: MASAR data


        a Python list to host all pv values with meta data:
        [(u'pv name', u'string value', u'double value', u'long value', u'dbr type', u'isConnected', u'secondsPastEpoch',
          u'nanoSeconds', u'timeStampTag', u'alarmSeverity', u'alarmStatus', u'alarmMessage', u'is_array', u'array_value'),
         (),
         ...
        ]


    :raises: RuntimeError
    """
    if not conn.alive():
        raise RuntimeError("MongoDB connection is inactive.")
    #cur = conn[collection][__eventdb].find({"eventidx": eventidx}, {'masar_data': 1, '_id': 0}).limit(1)
    cur = conn[collection][__eventdb].find({"eventidx": eventidx}, {'_id': 0}).limit(1)
    return cur[0]
    

def saveevent(conn, collection, **kwds):
    """Save a new MASAR event with data.

    :param conn: MongoDB connection object
    :type conn: object

    :param collection: MongoDB collection name
    :type collection: str

    :param configidx: configuration index number which this data set refers to
    :type desc: int

    :param comment: a brief comments of this data set.
    :type desc: str

    :param approval: status if this data set, approved or not.
    :type system: bool

    :param username: user name, which refers who saved this data set
    :type param: str

    :param eventidx: event index number, which is None by default. For database migration purpose.
    :type desc: int

    :param created_on: local time referring to the first time it was created, which is None by default. For database migration purpose.
    :type created_on: str

             time string format: "%Y-%m-%d %H:%M:%S", for example "2012-03-29 18:47:44"

    :param data: collected value from each EPICS V3 channel with meta data
    :type  data: list

        a Python list to host all pv values:
        (u'pv name', u'string value', u'double value', u'long value', u'dbr type', u'isConnected', u'secondsPastEpoch',
         u'nanoSeconds', u'timeStampTag', u'alarmSeverity', u'alarmStatus', u'alarmMessage', u'is_array', u'array_value')


    :returns: id of new event

    :raises: KeyError, RuntimeError

    """
    if not conn.alive():
        raise RuntimeError("MongoDB connection is inactive.")
    
    configid = kwds.get("configidx", None)
    if configid is None:
        raise RuntimeError("Cannot identify configuration index number.")
    if conn[collection][__configdb].find({"configidx": configid}).limit(1).count() != 1:
        raise ValueError("Unknown configuration index number (%s)" % configid)

    comment = kwds.get("comment", None)
    approval = kwds.get("approval", False)
    username = kwds.get("username", None)
    
    # data field to store data from IOC. 
    masardata=kwds.get("masar_data", None)
    if masardata is None:
        raise RuntimeError("Data set can not be empty.")

    eidx = kwds.get("eventidx", None)
    eventdoc = conn[collection][__eventdb]

    date = kwds.get("created_on", None)
    if date is None:
        eventid = eventdoc.insert({"eventidx": counter(conn, collection, __eventdb, idx=eidx),
                                   "configidx": configid,
                                   "comment": comment,
                                   "approval": approval,
                                   "created_on": time.strftime("%Y-%m-%d %H:%M:%S"),
                                   "masar_data": masardata,
                                   "username": username})
    else:
        eventid = eventdoc.insert({"eventidx": counter(conn, collection, __eventdb, idx=eidx),
                                   "configidx": configid,
                                   "comment": comment,
                                   "approval": approval,
                                   "created_on": date,
                                   "masar_data": masardata,
                                   "username": username})
    eventdoc.ensure_index([("eventidx", pymongo.DESCENDING)], background=True, unique=True)
    return eventdoc.find({"_id": eventid}).limit(1)[0]["eventidx"]


def updateevent(conn, collection, **kwds):
    """Update MASAR event status, and/or comments.

    :param conn: MongoDB connection object
    :type conn: object

    :param collection: MongoDB collection name
    :type collection: str

    :param eventidx: event index number to identify which event would be updated.
    :type desc: int

    :param comment: a brief comments of this data set.
    :type desc: str

    :param approval: status if this data set, approved or not.
    :type system: bool

    :param username: user name, which refers who saved this data set
    :type param: str

    :returns: True if succeeded

    :raises: KeyError, RuntimeError
    """
    if not conn.alive():
        raise RuntimeError("MongoDB connection is inactive.")
    eid = kwds.get("eventidx", None)
    if eid is None:
        raise RuntimeError("Unknown MASAR event to update.")

    comment = kwds.get("comment", None)
    approval = kwds.get("approval", None)
    username = kwds.get("username", None)
    params = {}
    if comment is not None:
        params['comment'] = comment
    if approval is not None:
        params['approval'] = approval
    if username is not None:
        params['username'] = username
    if params:
        params["updated_on"] = time.strftime("%Y-%m-%d %H:%M:%S")
        conn[collection][__eventdb].update({"eventidx": eid},
                                           {"$set": params},
                                            upsert=False)
    else:
        raise RuntimeError("No fields to update.")

    return True

# dslPYMongo.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# This code is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author: Guobao Shen   2014.08

import os
import re
import json

from masarclient.ntmultiChannel import NTMultiChannel

from pymasarmongo.db import utils
from pymasarmongo.pymasarmongo import pymasar

__all__ = ['DSL']


class DSL(object):
    """Implements Data Source Layer to interface with MongoDB."""
    def __init__(self):
        """constructor"""
        #define    DBF_STRING  0
        #define    DBF_INT     1
        #define    DBF_SHORT   1
        #define    DBF_FLOAT   2
        #define    DBF_ENUM    3
        #define    DBF_CHAR    4
        #define    DBF_LONG    5
        #define    DBF_DOUBLE  6
        self.epicsInt = [1, 4, 5]
        self.epicsString = [0, 3]
        self.epicsDouble = [2, 6]
        self.epicsNoAccess = [7]

    def __del__(self):
        """destructor"""
        print ('close MongoDB connection.')
        #utils.close(self.mongoconn)

    def dispatch(self, fname, fargs):
        """Dispatch a request"""
        actions = (("retrieveServiceConfigProps", self.retrieveSystems),
                   ("retrieveServiceConfigs", self.retrieveServiceConfigs),
                   ("retrieveServiceEvents", self.retrieveServiceEvents),
                   ("retrieveSnapshot", self.retrieveSnapshot),
                   ("saveSnapshot", self.saveSnapshot),
                   ('updateSnapshotEvent', self.approveSnapshotEvent)
                   )
        for (params, func) in actions:
            if re.match(params, fname):
                return func(fargs)

    def request(self, *argument):
        """issue request"""
        if len(argument) == 1:
            argument = argument[0]
            func = argument['function']
            result = self.dispatch(func, argument)
        else:
            func = argument[1]
            func = func['function']
            result = self.dispatch(func, argument)
        return (result, )

    def _parseParams(self, params, key):
        """Check request parameters"""
        results = []
        if len(key) == 0:
            return results
        for k in key:
            try:
                results.append(params[k])
            except KeyError:
                results.append(None)
        return results
    
    def retrieveSystems(self, params):
        """Retrieve system list

        :param params: a dictionary to carry query condition with structure like: ::

            {"system": [optional], # system name, wildcast allowed with * for multiple characters matching
             "configname": [optional], # configuration name, wildcast allowed with * for multiple characters matching
            }

        :returns: list with tuple with header description for each field. Structure like: ::

            [('config_id', 'config_idx', 'system_key', 'system_val'), ...]

        :raises:

        """
        key = ['system', 'configname']
        system, configname = self._parseParams(params, key)

        mongoconn, collection = utils.conn(host=os.environ["MASAR_MONGO_HOST"],
                                           port=os.environ["MASAR_MONGO_PORT"],
                                           db=os.environ["MASAR_MONGO_DB"])
        if system is None and configname is None:
            result = pymasar.retrieveconfig(mongoconn, collection)
        elif system is None:
            result = pymasar.retrieveconfig(mongoconn, collection, name=configname)
        else:
            if system.lower() == "all":
                result = pymasar.retrieveconfig(mongoconn, collection)
            else:
                result = pymasar.retrieveconfig(mongoconn, collection, system=system)
        utils.close(mongoconn)
        results = [('config_prop_id', 'config_idx', 'system_key', 'system_val')]
        for res in result:
            results.append((int(str(res["_id"]), 16), res["configidx"], "system", res["system"]))

        return results

    def retrieveServiceConfigs(self, params):
        """Retrieve configurations

        :param params: a dictionary to carry query condition with structure like: ::

            {"configname": [optional], # configuration name, wildcast allowed with * for multiple characters matching
             "system": [optional], # system name, wildcast allowed with * for multiple characters matching
             "configversion": [optional], # configuration version number
             "status": [optional], # either active or inactive, otherwise reset to None
            }

            or {'eventid': , # event index number to get which configuration this event belongs to}

        :returns: list with tuple with header description for each field. Structure like: ::

            [('config_idx', 'config_name', 'config_desc', 'config_create_date', 'config_version', 'status'), ...]

        :raises:

        """
        key = ['configname', 'configversion', 'system', 'status', 'eventid']
        configname, version, system, status, eventid = self._parseParams(params, key)
        if isinstance(eventid, (str, unicode)):
            eventid = int(eventid)
        if status is not None:
            status = status.lower()
            if status not in ["active", "inactive"]:
                status = None
        if system is not None and system.lower() == "all":
                system = None
        mongoconn, collection = utils.conn(host=os.environ["MASAR_MONGO_HOST"],
                                           port=os.environ["MASAR_MONGO_PORT"],
                                           db=os.environ["MASAR_MONGO_DB"])
        if eventid is not None:
            result = pymasar.retrieveconfig(mongoconn, collection, eventidx=eventid)
        elif system is None and configname is None:
            result = pymasar.retrieveconfig(mongoconn, collection, status=status)
        elif system is None:
            result = pymasar.retrieveconfig(mongoconn, collection, name=configname, status=status)
        else:
            result = pymasar.retrieveconfig(mongoconn, collection, system=system, status=status)
        utils.close(mongoconn)
        results = [('config_idx', 'config_name', 'config_desc', 'config_create_date', 'config_version', 'status')]
        for res in result:
            results.append((res["configidx"], res["name"], res["desc"], res["created_on"], res["version"], res["status"]))

        return results

    def retrieveServiceEvents(self, params):
        """Retrieve events

        :param params: a dictionary to carry query condition with structure like: ::

            {"configid": , # configuration index number
             "start": [optional], # start time string for time window based search with format: "%Y-%m-%d %H:%M:%S"
             "end": [optional], # end time string for time window based search with format: "%Y-%m-%d %H:%M:%S"
             "comment": [optional], # comments, wildcast allowed with * for multiple characters matching
             "user": [optional], # user name, wildcast allowed with * for multiple characters matching
             "approval": , # data set status, default is True
            }

        :returns: list with tuple with header description for each field. Structure like: ::

            [(event_id, config_id, comments, event_time, event_serial_tag), ...]

        :raises:

        """
        key = ['configid', 'eventid', 'start', 'end', 'comment', 'user', 'approval']
        cid, eid, start, end, comment, user, approval = self._parseParams(params, key)
        if approval is None:
            approval = True
        else:
            approval = bool(json.loads(str(approval).lower()))
        if isinstance(cid, (str, unicode)):
            cid = int(cid)
        if isinstance(eid, (str, unicode)):
            eid = int(eid)
        mongoconn, collection = utils.conn(host=os.environ["MASAR_MONGO_HOST"],
                                           port=os.environ["MASAR_MONGO_PORT"],
                                           db=os.environ["MASAR_MONGO_DB"])
        result = pymasar.retrieveevents(mongoconn, collection,
                                        configidx=cid, eventidx=eid,
                                        start=start, end=end, comment=comment,
                                        username=user, approval=approval)
        utils.close(mongoconn)

        results = [("event_id", "config_id", "comments", "event_time", "user_name")]
        for res in result:
            results.append((res["eventidx"], res["configidx"], res["comment"], res["created_on"], res["username"]))
        return results

    def retrieveSnapshot(self, params):
        """Retrieve snapshot data

        :param params: a dictionary to carry query condition with structure like: ::

            {"eventid": , # event index number}

        :returns: 2-d list with tuple with header description for each field. Structure like: ::

            [[('user tag', 'event time', 'service config name', 'service name'),
              ('pv name', 'string value', 'double value', 'long value', 'dbr type', 'isConnected',
               'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 'alarmSeverity', 'alarmStatus', 'alarmMessage',
               'is_array', 'array_value')], # header information to determine returning data
             [(comment, date, config name, None),
              (value for pv1 as described above),
              (value for pv2),
              ...]

        :raises:

        """
        key = ['eventid', 'comment']
        eid, _ = self._parseParams(params, key)
        result = [[('user tag', 'event time', 'service config name', 'service name'),
                   ('pv name', 'string value', 'double value', 'long value', 'dbr type', 'isConnected',
                    'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 'alarmSeverity', 'alarmStatus', 'alarmMessage',
                    'is_array', 'array_value')]]
        if eid is not None:
            if isinstance(eid, (str, unicode)):
                eid = int(eid)
            mongoconn, collection = utils.conn(host=os.environ["MASAR_MONGO_HOST"],
                                               port=os.environ["MASAR_MONGO_PORT"],
                                               db=os.environ["MASAR_MONGO_DB"])
            eiddata = pymasar.retrievesnapshot(mongoconn, collection, eid)
            configname = pymasar.retrieveconfig(mongoconn, collection, configidx=eiddata["configidx"])[0]["name"]
            utils.close(mongoconn)
            temp = [(eiddata["comment"], eiddata["created_on"], configname, None), ]
            for d in eiddata["masar_data"]:
                temp.append(tuple(d))
            result.append(temp)
        return result

    def saveSnapshot(self, params):
        """Save event with data.

        :param params: a dictionary to carry query condition with structure like: ::

            [[(channel name,), (string value,),(double value,),(long value,),(dbr type),(is connected),
              (second past epoch,),(nano seconds,),(time stamp tag,),
              (alarm severity,),(alarm status,),(alarm message,),
              (is_array), (array_value)
             ],
             {"configname": , # configuration name which the new data set belongs to
              "comment": [optional], # comment description for this new data set
              "approval": [optional], # approval status, False is not provided
              "username": [optional], # user name who commands this action
             }
            ]

        :returns: list with tuple with header description for each field. Structure like: ::

            [event_id] or [-1] if fault

        :raises: ValueError

        """
        key = ['configname', 'comment', 'approval', 'username']
        config, comment, approval, username = self._parseParams(params[1], key)
        if config is None:
            raise ValueError("Unknown configuration when saving a new snapshot event.")
        if approval is None:
            approval = False
        else:
            approval = bool(json.loads(str(approval).lower()))

        result = NTMultiChannel(params[0])
        dataLen = result.getNumberChannel()
        if dataLen == 0:
            raise RuntimeError("No available snapshot data.")

        # values format: the value is raw data from IOC
        # [(channel name,), (value,), (dbr type), (is connected),
        #  (second past epoch,), (nano seconds,), (time stamp tag,),
        # (alarm severity,), (alarm status,), (alarm message,)]
        pvnames = result.getChannelName()
        values = result.getValue()
        dbrtype = result.getDbrType()
        isconnected = result.getIsConnected()
        severity = result.getSeverity()
        status = result.getStatus()
        message = result.getMessage()
        sec = result.getSecondsPastEpoch()
        nanosec = result.getNanoseconds()
        usertag = result.getUserTag()

        # data format: the data is prepared to save into rdb
        # rawdata format
        # [('channel name', 'string value', 'double value', 'long value', 'dbr type', 'is connected',
        #   'seconds past epoch', 'nano seconds', 'time stamp tag', 'alarm severity', 'alarm status',
        #   'alarm message', 'is_array', 'array_value'),
        #  ...
        # ]
        datas = []

        # get IOC raw data
        for i in range(dataLen):
            tmp = []
            if isinstance(values[i], (list, tuple)):
                tmp = [pvnames[i], "", None, None, dbrtype[i], isconnected[i],
                       sec[i], nanosec[i], usertag[i], severity[i], status[i], message[i],
                       1, values[i]]
            else:
                if dbrtype[i] in self.epicsString:
                     tmp = [pvnames[i], values[i], None, None, dbrtype[i], isconnected[i],
                            sec[i], nanosec[i], usertag[i], severity[i], status[i], message[i],
                            0, None]
                else:
                     tmp = [pvnames[i], str(values[i]), values[i], values[i], dbrtype[i], isconnected[i],
                            sec[i], nanosec[i], usertag[i], severity[i], status[i], message[i],
                            0, None]
            datas.append(tmp)

        # save into database
        try:
            mongoconn, collection = utils.conn(host=os.environ["MASAR_MONGO_HOST"],
                                               port=os.environ["MASAR_MONGO_PORT"],
                                               db=os.environ["MASAR_MONGO_DB"])
            configs = pymasar.retrieveconfig(mongoconn, collection, name=config)
            if len(configs) != 1:
                raise RuntimeError("Cannot find a unique configuration.")

            eid = pymasar.saveevent(mongoconn, collection,
                                    configidx=configs[0]["configidx"],
                                    comment=comment,
                                    approval=approval,
                                    username=username,
                                    masar_data=datas)

            utils.close(mongoconn)
            return [eid, ]
        except:
            # keep the same format with a normal operation
            return [-1]

    def retrieveChannelNames(self, params):
        """Retrieve PV name list of given configuration(s).

        :param params: a dictionary to carry query condition with structure like: ::

            {"configname": , # configuration name, wildcast allowed with * for multiple characters matching
            }

        :returns: list of pv name like: ::

            [pv1, pv2, ...]

        :raises: ValueError

        """
        key = ['configname',  "comment"]
        config, _ = self._parseParams(params, key)

        if config is not None:
            mongoconn, collection = utils.conn(host=os.environ["MASAR_MONGO_HOST"],
                                               port=os.environ["MASAR_MONGO_PORT"],
                                               db=os.environ["MASAR_MONGO_DB"])
            result = pymasar.retrieveconfig(mongoconn, collection, name=config, withpvs=True)
            utils.close(mongoconn)
        else:
            raise ValueError("Known configuration name.")

        results = []
        for res in result:
            results = results + res["pvlist"]["names"]

        return results

    def approveSnapshotEvent(self, params):
        """Approve a new snapshot

        :param params: a dictionary to carry query condition with structure like: ::

            {"eventid": , # event index number
             "user": [optional], # user name, wildcast allowed with * for multiple characters matching
             "desc": [optional], # brief description
            }

        :returns: list as below: ::

            succeeded: [0, eventid]
            fail: [-1, eventid]
            exception: [-2, eventid]

        :raises: None

        """
        key = ['eventid', 'user', 'desc']
        eid, user, desc = self._parseParams(params, key)
        try:
            result = False
            if eid is not None:
                if isinstance(eid, (str, unicode)):
                    eid = int(eid)
                mongoconn, collection = utils.conn(host=os.environ["MASAR_MONGO_HOST"],
                                                   port=os.environ["MASAR_MONGO_PORT"],
                                                   db=os.environ["MASAR_MONGO_DB"])
                result = pymasar.updateevent(mongoconn, collection, eventidx=eid,
                                             approval=True, username=user,
                                             comment=desc)
                utils.close(mongoconn)

            if result:
                return [0, eid]
            else:
                return [-1, eid]
        except:
            return [-2, eid]

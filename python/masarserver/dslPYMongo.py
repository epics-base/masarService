# dslPYMongo.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# This code is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author: Guobao Shen   2014.08

import re
import json

from masarclient.nttable import NTTable

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
        self.epicsInt    = [1, 4, 5]
        self.epicsString = [0, 3]
        self.epicsDouble = [2, 6]
        self.epicsNoAccess = [7]

    def __del__(self):
        """destructor"""
        print ('close MongoDB connection.')
        # utils.close(self.mongoconn)

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

        mongoconn, collection = utils.conn()
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

        :returns: list with tuple with header description for each field. Structure like: ::

            [('config_idx', 'config_name', 'config_desc', 'config_create_date', 'config_version', 'status'), ...]

        :raises:

        """
        key = ['configname', 'configversion', 'system', 'status']
        configname, version, system, status = self._parseParams(params, key)
        if status is not None:
            status = status.lower()
            if status not in ["active", "inactive"]:
                status = None
        if system.lower() == "all":
            system = None
        mongoconn, collection = utils.conn()
        if system is None and configname is None:
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
        key = ['configid', 'start', 'end', 'comment', 'user', 'approval']
        cid, start, end, comment, user, approval = self._parseParams(params, key)
        if approval is None:
            approval = True
        else:
            approval = bool(json.loads(str(approval).lower()))
        if isinstance(cid, (str, unicode)):
            cid = int(cid)
        mongoconn, collection = utils.conn()
        result = pymasar.retrieveevents(mongoconn, collection,
                                        configidx=cid, start=start, end=end, comment=comment,
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
            mongoconn, collection = utils.conn()
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
        rawdata = params[0]
        nttable = NTTable(rawdata, True)
        numberValueCount = nttable.getNumberValues()
        if numberValueCount == 1 and 'status' == nttable.getLabel()[0] and not nttable.getValue(0)[0]:
            raise ValueError("Got empty data set")

        # values format: the value is raw data from IOC
        # [(channel name,), (string value,),(double value,),(long value,),(dbr type),(is connected),
        #  (second past epoch,),(nano seconds,),(time stamp tag,),(alarm severity,),(alarm status,),(alarm message,),
        # (is_array), (array_value)]
        values = []

        # data format: the data is prepared to save into rdb
        # rawdata format
        # [('channel name', 'string value', 'double value', 'long value', 'dbr type', 'is connected',
        #   'seconds past epoch', 'nano seconds', 'time stamp tag', 'alarm severity', 'alarm status',
        #   'alarm message', 'is_array', 'array_value'),
        #  ...
        # ]
        datas = []
        dataLen = len(nttable.getValue(0))

        dbrtype = nttable.getValue(4)
        is_array = nttable.getValue(12)
        # get IOC raw data
        for i in range(numberValueCount):
            if i == 13:
                raw_array_value = nttable.getValue(i)
                array_value = []
                for j in range(len(is_array)):
                    if dbrtype[j] in self.epicsDouble:
                        array_value.append(raw_array_value[j][1])
                    elif dbrtype[j] in self.epicsInt:
                        array_value.append(raw_array_value[j][2])
                    elif dbrtype[j] in self.epicsString:
                        array_value.append(raw_array_value[j][0])
                    elif dbrtype[j] in self.epicsNoAccess:
                        array_value.append(raw_array_value[j][0])
                values.append(array_value)
            else:
                values.append(list(nttable.getValue(i)))
        # problem when a negative value is passed from C++
        #define DBF_FLOAT   2
        #define DBF_DOUBLE  6
        for i in range(len(values[2])):
            if values[4][i] in [2, 6] and values[2][i] < 0:
                values[3][i] = int(values[2][i])

        # initialize data for rdb
        for j in range(dataLen):
            datas.append(())

        # convert data format values ==> datas
        for i in range(numberValueCount):
            for j in range(dataLen):
                datas[j] = datas[j] + (values[i][j],)

        # save into database
        try:
            mongoconn, collection = utils.conn()
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
            mongoconn, collection = utils.conn()
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
                mongoconn, collection = utils.conn()
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

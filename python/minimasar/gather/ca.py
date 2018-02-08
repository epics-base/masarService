
import logging
_log = logging.getLogger(__name__)

import time

from functools import partial

from cothread.catools import caget, FORMAT_TIME

from p4p.rpc import RemoteError
from p4p.wrapper import Value
import minimasar.ops_base

class Gatherer(object):
    def __init__(self, queue=None):
        pass

    def gather(self, pvs):
        # assume called on main thread (were cothread was first imported)

        try:
            values = caget(pvs, format=FORMAT_TIME, timeout = 2, throw = False)

            ret = {
                'value':[],
                'channelName':[],
                'severity': [],
                'status': [],
                'message': [],
                'secondsPastEpoch': [],
                'nanoseconds': [],
                'userTag': [],
                'isConnected': [],
                'dbrType': [],
                'readonly': [False]*len(values),
                'groupName': ['']*len(values),
                'tags': ['']*len(values),
            }

            for value in values:
                ret['channelName'].append(value.name)
                ret['isConnected'].append(value.ok)
                ret['message'].append('') # ???

                if value.ok:
                    ret['severity'].append(value.severity)
                    ret['status'].append(value.status)
                    ret['dbrType'].append(value.datatype)
                    sec, nsec = value.raw_stamp
                    #sec = int(value.timestamp)
                    #nsec = (value.timestamp-sec)*1e9

                    #TODO Union handling in p4p means that field types don't match dbrType (eg. double for DBF_FLOAT)
                    ret['value'].append(value)
                else:
                    ret['severity'].append(0)
                    ret['status'].append(0)
                    ret['dbrType'].append(7)
                    sec = int(time.time())
                    nsec = 0

                    ret['value'].append(0)

                ret['secondsPastEpoch'].append(sec)
                ret['nanoseconds'].append(nsec)
                ret['userTag'].append(0)

            return Value(minimasar.ops_base.multiType, ret)
        except Exception as e:
            _log.exception("Failed to gather: %s", pvs)
            raise RemoteError("Error while fetching PV values")

"""
This is client library for masar (Machine snapshot, archiving, and retrieve) service.
It is implemented under EPICS V4 framework, and use pvAccess channel RPC as communication
protocol. The data structure used here includes NTNameValue for passing arguments, and NTTable
for data transfer.

Current masar service uses SQLite as underneath relational database back-end.

The new version is based on pvaPy module.

Created on Oct 23, 2011
modified: May 15, 2014

@author: shengb
"""

import pvaccess

__version__ = '2.0.0'

class client():
    def __init__(self, channelname = 'masarService'):
        """
        masar service client library. Default channel name is masarService.
        """
        #self.channelname = channelname
        self.rpc = pvaccess.RpcClient(channelname)
    
    def __isFault(self, label, nttable):        
        #label = nttable.getScalarArray('label')
        if label[0] == 'status' and not nttable.getScalarArray('status')[0]:
            return True
        return False

    def retrieveSystemList(self):
        """
        Retrieve all system defined for masar service. 
        
        Parameters: None
        Result:     list with all system name, otherwise, False if nothing is found.
        """
        request = pvaccess.PvObject({'system' : pvaccess.STRING, 'function' : pvaccess.STRING})
        request.set({'system' : '*', 'function' : 'retrieveServiceConfigProps' })
        nttable = self.rpc.invoke(request)

        label = nttable.getScalarArray('label')
        if self.__isFault(label, nttable):
            return False

        expectedlabel = ['config_prop_id', 'config_idx', 'system_key', 'system_val']
        if label != expectedlabel:
            raise RuntimeError("Data structure not as expected for retrieveSystemList().")

        return (sorted(set(nttable.getScalarArray(label[-1]))))

    def retrieveServiceConfigs(self, params):
        """
        Retrieve all configurations existing in current masar database.
        All values for parameters have to be string since current NTNameValue accepts string only.
        A wildcast search is supported for service name, configuration name, and system,
        with "*" for multiple characters search, and "?" for single character.

        Parameters: a dictionary with predefined keys as below:
                    'servicename': [optional] the service name, which should be 'masar'.
                    'configname':  [optional] the configuration name.
                    'system':      [optional] retrieve configuration only belongs to given system.
                                   It will retrieve all configurations if it is empty.
        Result:     list of list with the following format:
                    id []:           index value of each configuration
                    name []:         name of each configuration
                    description []:  description of each configuration
                    created date []: date when each configuration was created
                    version []       version number
                    status []:       status, active/inactive

                    otherwise, False if nothing is found.
        """
        if not isinstance(params, dict):
            raise RuntimeError("Parameters have to be a Python dictionary")

        pvobj = {'function': pvaccess.STRING}
        for k in params.keys():
            pvobj[k] = pvaccess.STRING

        if not params.has_key('servicename'):
            pvobj['servicename'] = pvaccess.STRING
            params['servicename'] = 'masar'

        if not params.has_key('system'):
            pvobj['system'] = pvaccess.STRING
            params['system'] = 'all'
        elif params['system'] == "*":
            params['system'] = 'all'

        params['function'] = 'retrieveServiceConfigs'
        request = pvaccess.PvObject(pvobj)
        request.set(params)

        nttable = self.rpc.invoke(request)

        label = nttable.getScalarArray('label')
        if self.__isFault(label, nttable):
            return False

        expectedlabel=['config_idx', 'config_name', 'config_desc', 'config_create_date',
                       'config_version', 'status']
        if label != expectedlabel:
            raise RuntimeError("Data structure not as expected for retrieveServiceConfigs().")

        return (nttable.getScalarArray(label[0]),
                nttable.getScalarArray(label[1]),
                nttable.getScalarArray(label[2]),
                nttable.getScalarArray(label[3]),
                nttable.getScalarArray(label[4]),
                nttable.getScalarArray(label[5]))

    def retrieveServiceEvents(self, params):
        """
        Retrieve event list which belong to a particular snapshot configuration.
        It retrieves event id, user name, comment, and date, but without real data from IOC.
        All values for parameters have to be string since current NTNameValue accepts string only.
        A wildcast search is supported for comment, and user name,
        with "*" for multiple characters search, and "?" for single character.

        Internally, the date is saved in UTC format.

        Parameters: a dictionary which can have any combination of the following predefined keys:
                    'configid': id to identify which configuration it belongs to
                    'start':    The time window start string
                    'end':      The time window end   string
                    'comment':  event contain given comment.
                    'user':     who did that event
        result:     list of list with the following format:
                    id []:     list of each event id
                    comment:   a list to show comment for each event
                    user name: user name list
                    date []:   time list to show when that event happened in UTC format

                    otherwise, False if nothing is found.
        """
        if not isinstance(params, dict):
            raise RuntimeError("Parameters have to be a Python dictionary.")

        if not params.has_key('configid'):
            raise RuntimeError("service configuration ID is not available.")

        pvobj = {'function': pvaccess.STRING}
        for k in params.keys():
            pvobj[k] = pvaccess.STRING

        params['function'] = 'retrieveServiceEvents'
        request = pvaccess.PvObject(pvobj)
        request.set(params)

        nttable = self.rpc.invoke(request)

        label = nttable.getScalarArray('label')
        expectedlabel = ["event_id", "config_id", "comments", "event_time", "user_name"]
        if label != expectedlabel:
            raise RuntimeError("Data structure not as expected for retrieveServiceEvents().")
        if self.__isFault(label, nttable):
            return False

        # 0: service_event_id,
        # 1: service_config_id,
        # 2: service_event_user_tag,
        # 3: service_event_UTC_time,
        # 4: service_event_user_name
        return (nttable.getScalarArray(label[0]),
                nttable.getScalarArray(label[2]),
                nttable.getScalarArray(label[3]),
                nttable.getScalarArray(label[4]))

    def retrieveSnapshot(self, params):
        """
        Retrieve a particular snapshot, which is flagged to be an approved snapshot, with real data.
        The value is stored in 3 formats: string, double, and long.
        If original value is an array, it is stored in array_value.
        User needs to combine the dbr_type information to get right value.

        DBR_TYPE is defined in db_access.h as below:
            #define DBF_STRING      0
            #define DBF_INT         1
            #define DBF_SHORT       1
            #define DBF_FLOAT       2
            #define DBF_ENUM        3
            #define DBF_CHAR        4
            #define DBF_LONG        5
            #define DBF_DOUBLE      6
            #define DBF_NO_ACCESS   7

        They are mapped in masar service:
            epicsLong   =   [1, 4, 5]
            epicsString =   [0, 3]
            epicsDouble =   [2, 6]
            epicsNoAccess = [7]
        which means for example, if original value is DBR_SHORT, the right place to find it will be in double valu$
        in the return result.

        Parameters: a dictionary which can have any combination of the following predefined keys:
                    'eventid':  id of a particular event
                    'start':    The time range from
                    'end':      The time range to
                    'comment':  event contain given comment.

        result:     list of list with the following format:
                    pv name []:          pv name list
                    string value []:     value list in string format
                    double value []      value list in double format
                    long value []        value list in long format
                    dbr_type []:         EPICS DBR types
                    isConnected []:      connection status, either True or False
                    secondsPastEpoch []: seconds after EPOCH time
                    nanoSeconds []:      nano-seconds
                    alarmSeverity []:    EPICS IOC severity
                    alarmStatus []:      EPICS IOC status
                    is_array []:         whether value is array, either True or False
                    array_value [[]]:    if it is array, the value is stored here.

                    otherwise, False if nothing is found.
        """
        if not isinstance(params, dict):
            raise RuntimeError("Parameters have to be a Python dictionary.")

        if not params.has_key('eventid'):
            raise RuntimeError("MASAR snapshot ID is not available.")

        pvobj = {'function': pvaccess.STRING}
        for k in params.keys():
            pvobj[k] = pvaccess.STRING

        params['function'] = 'retrieveSnapshot'
        request = pvaccess.PvObject(pvobj)
        request.set(params)

        nttable = self.rpc.invoke(request)

        label = nttable.getScalarArray('label')
        expectedlabel = ['pv name', 'string value', 'double value', 'long value', 'dbr type', 
                         'isConnected', 'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 
                         'alarmSeverity', 'alarmStatus', 'alarmMessage', 'is_array', 'array_value']
        if label != expectedlabel:
            raise RuntimeError("Data structure not as expected for retrieveSnapshot().")

        if self.__isFault(label, nttable):
            return False

        return (nttable.getScalarArray(label[0]),
                nttable.getScalarArray(label[1]),
                nttable.getScalarArray(label[2]),
                nttable.getScalarArray(label[3]),
                nttable.getScalarArray(label[4]),
                nttable.getScalarArray(label[5]),
                nttable.getScalarArray(label[6]),
                nttable.getScalarArray(label[7]),
                nttable.getScalarArray(label[9]),
                nttable.getScalarArray(label[10]),
                nttable.getScalarArray(label[12]),
                nttable.getStructureArray(label[13]))

    def saveSnapshot(self, params):
        """
        This function is to take a machine snapshot data and send data to client for preview .
        Meanwhile the data will be saved into database with a default flag to identify
        that this preview is not approved by the user yet.
        It gives user a opportunity to confirm whether the snapshot is good or not.

        It creates an entry in both event list table, and event data table.

        Parameters: a dictionary which can have any combination of the following predefined keys:
                    'servicename': [optional] exact service name if given
                    'configname':  exact configuration name
                    'comment':     [optional] exact comment.

        result:     list of list with the following format:
                    id: id of this new event
                    pv name []:          pv name list
                    string value []:     value list in string format
                    double value []      value list in double format
                    long value []        value list in long format
                    dbr_type []:         EPICS DBR types
                    isConnected []:      connection status, either True or False
                    secondsPastEpoch []: seconds after EPOCH time
                    nanoSeconds []:      nano-seconds
                    alarmSeverity []:    EPICS IOC severity
                    alarmStatus []:      EPICS IOC status
                    is_array []:         whether value is array, either True or False
                    array_value [[]]:    if it is array, the value is stored here.

                    otherwise, False if operation failed.
        """
        if not isinstance(params, dict):
            raise RuntimeError("Parameters have to be a Python dictionary.")

        if not params.has_key('configname'):
            raise RuntimeError("service configuration name is not available.")

        pvobj = {'function': pvaccess.STRING}
        for k in params.keys():
            pvobj[k] = pvaccess.STRING

        params['function'] = 'saveSnapshot'
        request = pvaccess.PvObject(pvobj)
        request.set(params)

        nttable = self.rpc.invoke(request)

        label = nttable.getScalarArray('label')
        expectedlabel = ['pv name', 'string value', 'double value', 'long value', 'dbr type', 
                         'isConnected', 'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 
                         'alarmSeverity', 'alarmStatus', 'alarmMessage', 'is_array', 'array_value']
        label4error = ['status']
        if label == expectedlabel:
            # [event id,
            #  pv name,string value,double value,long value,
            #  dbr type,isConnected,secondsPastEpoch,nanoSeconds,timeStampTag,
            #  alarmSeverity,alarmStatus,alarmMessage, is_array, array_value]
            return (nttable.getTimeStamp().getInt('userTag'),
                    nttable.getValue(0),
                    nttable.getValue(1),
                    nttable.getValue(2),
                    nttable.getValue(3),
                    nttable.getValue(4),
                    nttable.getValue(5),
                    nttable.getValue(6),
                    nttable.getValue(7),
                    nttable.getValue(9),
                    nttable.getValue(10),
                    nttable.getValue(12),
                    nttable.getValue(13))
        elif label == label4error:
            return nttable.getScalarArray('status')[0]
        else:
            raise RuntimeError("Data structure not as expected for saveSnapshot().")

    def updateSnapshotEvent(self, params):
        """
        Approve a particular snapshot.
        User can put name and give a comment to that snapshot.
        Parameters: a dictionary which can have any combination of the following predefined keys:
                    'eventid': id of event to be approval
                    'user':    user name to identify who approves/takes this snapshot
                    'desc':    any comment to describe this snapshot.

        result:     True, otherwise, False if operation failed.
        """
        if not isinstance(params, dict):
            raise RuntimeError("Parameters have to be a Python dictionary.")

        if not params.has_key('eventid'):
            raise RuntimeError("snapshot event id is not available.")

        pvobj = {'function': pvaccess.STRING}
        for k in params.keys():
            pvobj[k] = pvaccess.STRING

        params['function'] = 'updateSnapshotEvent'
        request = pvaccess.PvObject(pvobj)
        request.set(params)

        nttable = self.rpc.invoke(request)

        label = nttable.getScalarArray('label')
        expectedlabel = ['status']
        if label != expectedlabel:
            raise RuntimeError("Data structure not as expected for updateSnapshotEvent().")

        return nttable.getScalarArray('status')[0]

    def getLiveMachine(self, params):
        """
        Get live data with given pv list, and uses pv name as both key and value.
        Same as retrieveSnapshot function, for a scalar pv, its value is carried in string, double and long. For a$
        its value is carried in array_value. Client needs to check the pv is an array by checking is_array, and ch$
        by checking dbr_type.

        Parameters: a dictionary which can have any combination of the following predefined keys:
                    'servicename': [optional] exact service name if given
                    'configname':  exact configuration name
                    'comment':     [optional] exact comment.

        result:     list of list with the following format:
                    pv name []:          pv name list
                    string value []:     value list in string format
                    double value []      value list in double format
                    long value []        value list in long format
                    dbr_type []:         EPICS DBR types
                    isConnected []:      connection status, either True or False
                    secondsPastEpoch []: seconds after EPOCH time
                    nanoSeconds []:      nano-seconds
                    alarmSeverity []:    EPICS IOC severity
                    alarmStatus []:      EPICS IOC status
                    is_array []:         whether value is array, either True or False
                    array_value [[]]:    if it is array, the value is stored here.

                    otherwise, False if operation failed.
        """
        if not isinstance(params, dict):
            raise RuntimeError("Parameters have to be a Python dictionary.")

        if not params.has_key('configname'):
            raise RuntimeError("service config name is not available.")

        pvobj = {'function': pvaccess.STRING}
        for k in params.keys():
            pvobj[k] = pvaccess.STRING

        params['function'] = 'getLiveMachine'
        request = pvaccess.PvObject(pvobj)
        request.set(params)

        nttable = self.rpc.invoke(request)

        label = nttable.getScalarArray('label')
        expectedlabel = ['pv name', 'string value', 'double value', 'long value', 'dbr type', 
                         'isConnected', 'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 
                         'alarmSeverity', 'alarmStatus', 'alarmMessage', 'is_array', 'array_value']
        label4error = ['status']
        if label == expectedlabel:
            # [pv name,string value,double value,long value,
            #  dbr type,isConnected,secondsPastEpoch,nanoSeconds,timeStampTag,
            #  alarmSeverity,alarmStatus,alarmMessage, is_array, array_value]
            return (nttable.getValue(0),
                    nttable.getValue(1),
                    nttable.getValue(2),
                    nttable.getValue(3),
                    nttable.getValue(4),
                    nttable.getValue(5),
                    nttable.getValue(6),
                    nttable.getValue(7),
                    nttable.getValue(9),
                    nttable.getValue(10),
                    nttable.getValue(12),
                    nttable.getValue(13))
        elif label == label4error:
            return nttable.getScalarArray('status')[0]
        else:
            raise RuntimeError("Data structure not as expected for getLiveMachine().")

#if __name__ == "__main__":
    #mc = client('masarService4Test')
    #mc.retrieveSystemList()
    #mc.retrieveServiceConfigs({'configname': '*', 'system': 'all'})
    #mc.retrieveServiceEvents({'configid': '1', 'user':'*'})
    #print mc.retrieveSnapshot({'eventid': '1005', 'comment':'*'})

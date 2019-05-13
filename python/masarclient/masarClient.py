"""
This is client library for masar (Machine snapshot, archiving, and retrieve) service.
It is implemented under EPICS V4 framework, and use pvAccess channel RPC as communication
protocol. The data structure used here includes NTNameValue for passing arguments, and NTTable
for data transfer.

Current masar service uses SQLite as underneath relational database back-end.

NOTE: Call masar.epicsExit.registerExit() before exit to avoid undesired destruction problem as below:

Created on Oct 23, 2011

@author: shengb
"""

from p4p.client.thread import Context
from minimasar.client import MASAR

class client():
    def __init__(self, channelname = 'masarService'):
        """
        masar service client library. Default channel name is masarService.
        """
        self.channelname = channelname
        self._pva_context = Context('pva')
        self._proxy = MASAR(context=self._pva_context, format=channelname+':')

    def retrieveSystemList(self):
        """
        Retrieve all system defined for masar service. 
        
        Parameters: None
        Result:     list with all system name, otherwise, False if nothing is found.
        """
        nttable = self._proxy.retrieveServiceConfigProps()
        return sorted(set(nttable.value.system_val))
    
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
        nttable = self._proxy.retrieveServiceConfigs(**params)
        return (nttable.value.config_idx,
                nttable.value.config_name,
                nttable.value.config_desc,
                nttable.value.config_create_date,
                nttable.value.config_version,
                nttable.value.status)
    
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
                    'start':    The time range from
                    'end':      The time range to
                    'comment':  event contain given comment. 
                    'user':     who did that event
        result:     list of list with the following format:
                    id []:     list of each event id
                    comment:   a list to show comment for each event
                    user name: user name list
                    date []:   time list to show when that event happened in UTC format
                    
                    otherwise, False if nothing is found.
        """
        nttable = self._proxy.retrieveServiceEvents(**params)
        return (nttable.value.event_id,
                nttable.value.comments,
                nttable.value.event_time,
                nttable.value.user_name)
    
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
        which means for example, if original value is DBR_SHORT, the right place to find it will be in double value array
        in the return result.
        
        Parameters: a dictionary which can have any combination of the following predefined keys:
                    'eventid':  id of a particular event
                    'start':    The time range from
                    'end':      The time range to
                    'comment':  event contain given comment. 

        result:     list of list with the following format:
                    pv name []:          pv name list
                    value []             value list
                    dbrTypee []          EPICS V3 DBR type for each channel
                    isConnected []:      connection status, either True or False
                    secondsPastEpoch []: seconds after EPOCH time
                    nanoSeconds []:      nano-seconds
                    userTags []:
                    alarmSeverity []:    EPICS IOC severity
                    alarmStatus []:      EPICS IOC status
                    alarmMessage []:     EPICS IOC pv status message
                            
                    otherwise, False if nothing is found.
        """
        R = self._proxy.retrieveSnapshot(**params)
        return (R.channelName,
                R.value,
                R.dbrType,
                R.isConnected,
                R.secondsPastEpoch,
                R.nanoseconds,
                R.userTag,
                R.severity,
                R.status,
                R.message)
        
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
                    id:                  id of this new event
                    pv name []:          pv name list
                    value []             value list
                    dbrTypee []          EPICS V3 DBR type for each channel
                    isConnected []:      connection status, either True or False
                    secondsPastEpoch []: seconds after EPOCH time
                    nanoSeconds []:      nano-seconds
                    userTags []:
                    alarmSeverity []:    EPICS IOC severity
                    alarmStatus []:      EPICS IOC status
                    alarmMessage []:     EPICS IOC pv status message

                    otherwise, False if nothing is found.
        """
        print "saveSnapshot", params
        R = self._proxy.saveSnapshot(**params)
        return (R.timeStamp.userTag, # actually new event #
                R.channelName,
                R.value,
                R.dbrType,
                R.userTag,
                R.isConnected,
                R.secondsPastEpoch,
                R.nanoseconds,
                R.severity,
                R.status,
                R.message)

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
        R = self._proxy.saveSnapshot(**params)
        return R.value
    
    def getLiveMachine(self, params, conn_time=1.0, resp_time=5.0):
        """
        Get live data with given pv list, and uses pv name as both key and value. 
        Same as retrieveSnapshot function, for a scalar pv, its value is carried in string, double and long. For a waveform/array, 
        its value is carried in array_value. Client needs to check the pv is an array by checking is_array, and check its data type 
        by checking dbr_type.

        Parameters: param: a dictionary which can have any combination of the following predefined keys:
                              'servicename': [optional] exact service name if given
                              'configname':  exact configuration name
                              'comment':     [optional] exact comment. 
                    conn_time: waiting time for connection, 1.0 by default;
                    resp_time: waiting time for response, 5.0 by default;

        result:     list of list with the following format:
                    pv name []:          pv name list
                    value []             value list
                    dbrTypee []          EPICS V3 DBR type for each channel
                    isConnected []:      connection status, either True or False
                    secondsPastEpoch []: seconds after EPOCH time
                    nanoSeconds []:      nano-seconds
                    userTags []:
                    alarmSeverity []:    EPICS IOC severity
                    alarmStatus []:      EPICS IOC status
                    alarmMessage []:     EPICS IOC pv status message

                    otherwise, False if operation failed.
        """
        R = self._proxy.getCurrentValue(names=params)
        return (R.channelName,
                R.value,
                R.dbrType,
                R.userTag,
                R.isConnected,
                R.secondsPastEpoch,
                R.nanoseconds,
                R.severity,
                R.status,
                R.message)

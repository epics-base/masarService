"""
This is client library for masar (Machine snapshot, archiving, and retrieve) service.
It is implemented under EPICS V4 framework, and use pvAccess channel RPC as communication
protocol. The data structure used here includes NTNameValue for passing arguments, and NTTable
for data transfer.

Current masar service uses SQLite as underneath relational database back-end.

NOTE: Call epicsExit() before exit to avoid undesired destruction problem as below:
      sys.exit(epicsExit())

Created on Oct 23, 2011

@author: shengb
"""

from channelRPC import ChannelRPC
from ntnameValue import NTNameValue
from nttable import NTTable
from alarm import Alarm
from timeStamp import TimeStamp

class client():
    def __init__(self, channelname = 'masarService'):
        """
        masar service client library. Default channel name is masarService.
        """
        self.channelname = channelname

    def __clientRPC(self, function, params):
        """
        internal library for pvAccess channel RPC.
        """
        alarm = Alarm()
        timeStamp = TimeStamp()
    
        ntnv = NTNameValue(function,params)
        
        # now do issue + wait
        channelRPC = ChannelRPC(self.channelname,"record[process=true]field()")
        channelRPC.issueConnect()
        if not channelRPC.waitConnect(1.0) :
            print channelRPC.getMessage()
            raise Exception(channelRPC.getMessage())
        channelRPC.issueRequest(ntnv.getNTNameValue(),False)
        result = channelRPC.waitRequest()
        if(result==None) :
            print channelRPC.getMessage()
            raise Exception(channelRPC.getMessage())
        nttable = NTTable(result)
        nttable.getAlarm(alarm.getAlarmPy())    
        nttable.getTimeStamp(timeStamp.getTimeStampPy())
        return nttable
    
    def __isFault(self, nttable):        
        label = nttable.getLabel()
        if label[0] == 'status' and not nttable.getValue(0)[0]:
            return True
        return False

    def retrieveSystemList(self):
        """
        Retrieve all system defined for masar service. 
        
        Parameters: None
        Result:     list with all system name, otherwise, False if nothing is found.
        """
        function = 'retrieveServiceConfigProps'
        params = {}
        nttable = self.__clientRPC(function, params)

        if self.__isFault(nttable):
            return False
        
        valueCounts = nttable.getNumberValues()
        results = nttable.getValue(valueCounts-1)
        return (sorted(set(results)))
    
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
                    
                    otherwise, False if nothing is found.
        """
        function = 'retrieveServiceConfigs'
        nttable = self.__clientRPC(function, params)
        
        if self.__isFault(nttable):
            return False
        
        return (nttable.getValue(0),
                nttable.getValue(1),
                nttable.getValue(2),
                nttable.getValue(3),
                nttable.getValue(4)) 
    
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
        function = 'retrieveServiceEvents'
        nttable = self.__clientRPC(function, params)

        if self.__isFault(nttable):
            return False
        
        # 0: service_event_id,
        # 1: service_config_id,
        # 2: service_event_user_tag,
        # 3: service_event_UTC_time,
        # 4: service_event_user_name
        return (nttable.getValue(0), 
                nttable.getValue(2),
                nttable.getValue(3),
                nttable.getValue(4))
    
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
        function = 'retrieveSnapshot'
        # [pv name,string value,double value,long value,
        #  dbr type,isConnected,secondsPastEpoch,nanoSeconds,timeStampTag,
        #  alarmSeverity,alarmStatus,alarmMessage, is_array, array_value]
        nttable = self.__clientRPC(function, params)

        if self.__isFault(nttable):
            return False
        
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
        function = 'saveSnapshot'
        nttable = self.__clientRPC(function, params)

        if self.__isFault(nttable):
            return False
        
        ts = TimeStamp()
        # [pv name,string value,double value,long value,
        #  dbr type,isConnected,secondsPastEpoch,nanoSeconds,timeStampTag,
        #  alarmSeverity,alarmStatus,alarmMessage, is_array, array_value]
        nttable.getTimeStamp(ts.getTimeStampPy())
        return (ts.getUserTag(),
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
        function = 'updateSnapshotEvent'
        nttable = self.__clientRPC(function, params)
#
#        if self.__isFault(nttable):
#            return False
        
        return nttable.getValue(0)[0]
    
    def getLiveMachine(self, params):
        """
        Get live data with given pv list, and uses pv name as both key and value. 
        Same as retrieveSnapshot function, for a scalar pv, its value is carried in string, double and long. For a waveform/array, 
        its value is carried in array_value. Client needs to check the pv is an array by checking is_array, and check its data type 
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
                    is_array []:         whether value is array, either True or False
                    array_value [[]]:    if it is array, the value is stored here.
                            
                    otherwise, False if operation failed.
        """        
        function = 'getLiveMachine'
        nttable = self.__clientRPC(function, params)

        if self.__isFault(nttable):
            return False
        
        # channelName,stringValue,doubleValue,longValue,dbrType,isConnected, is_array, array_value
        return (nttable.getValue(0),
                nttable.getValue(1),
                nttable.getValue(2),
                nttable.getValue(3),
                nttable.getValue(4),
                nttable.getValue(5),
                nttable.getValue(12),
                nttable.getValue(13))

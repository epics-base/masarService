from channelRPC import ChannelRPC
from ntnameValue import NTNameValue
from nttable import NTTable
from alarm import Alarm
from timeStamp import TimeStamp

class client():
    def __init__(self, channelname = 'masarService'):
        self.channelname = channelname

    def __clientRPC(self, function, params):
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
        function = 'retrieveServiceConfigProps'
        params = {}
        nttable = self.__clientRPC(function, params)

        if self.__isFault(nttable):
            return False
        
        valueCounts = nttable.getNumberValues()
        results = nttable.getValue(valueCounts-1)
        return (sorted(set(results)))
    
    def retrieveServiceConfigs(self, params):
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
        function = 'updateSnapshotEvent'
        nttable = self.__clientRPC(function, params)
#
#        if self.__isFault(nttable):
#            return False
        
        return nttable.getValue(0)[0]
    
    def getLiveMachine(self, params):
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

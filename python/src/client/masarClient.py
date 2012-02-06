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
    #    channelRPC = ChannelRPC("masarService","record[process=true]field()")    
        channelRPC = ChannelRPC(self.channelname,"record[process=true]field()")
        channelRPC.issueConnect()
        if not channelRPC.waitConnect(1.0) :
            print channelRPC.getMessage()
            exit(1)
        channelRPC.issueRequest(ntnv.getNTNameValue(),False)
        result = channelRPC.waitRequest()
        if(result==None) :
            print channelRPC.getMessage()
            exit(1)
        nttable = NTTable(result)
        nttable.getAlarm(alarm.getAlarmPy())    
        nttable.getTimeStamp(timeStamp.getTimeStampPy())
        return nttable
    
    # example to operate a nttable
    #    valueCounts = nttable.getNumberValues()
    #    label = nttable.getLabel()
    #    for i in range(valueCounts):
    #        value = nttable.getValue(i)
    
    def retrieveSystemList(self):
        function = 'retrieveServiceConfigProps'
        params = {}
        nttable = self.__clientRPC(function, params)
        valueCounts = nttable.getNumberValues()
        results = nttable.getValue(valueCounts-1)
        return (sorted(set(results)))
    
    def retrieveServiceConfigProps(self, params):
        function = 'retrieveServiceConfigProps'
        print ("=== test %s ===" %function)
        params = {'propname': 'system', 
                  'configname': 'sr_qs'
                  }
        self.__clientRPC(function, params)
        print ("=== test %s end ===" %function)
        
    def retrieveServiceConfigs(self, params):
        function = 'retrieveServiceConfigs'
        nttable = self.__clientRPC(function, params)
        return (nttable.getValue(0),
                nttable.getValue(1),
                nttable.getValue(2),
                nttable.getValue(3),
                nttable.getValue(4)) 
    
    def retrieveServiceEvents(self, params):
        function = 'retrieveServiceEvents'
        nttable = self.__clientRPC(function, params)
#        service_event_id,service_config_id,service_event_user_tag,service_event_UTC_time
        return (nttable.getValue(0), 
                nttable.getValue(2),
                nttable.getValue(3))
    
    def retrieveSnapshot(self, params):
        function = 'retrieveSnapshot'
#        [pv name,string value,double value,long value,
#        dbr type,isConnected,secondsPastEpoch,nanoSeconds,timeStampTag,
#        alarmSeverity,alarmStatus,alarmMessage]
        nttable = self.__clientRPC(function, params)
        return (nttable.getValue(0), 
                nttable.getValue(1), 
                nttable.getValue(2),
                nttable.getValue(3),
                nttable.getValue(4),
                nttable.getValue(5),
                nttable.getValue(6),
                nttable.getValue(7),
                nttable.getValue(9),
                nttable.getValue(10))
    
    def saveSnapshot(self, params):
        function = 'saveSnapshot'
        nttable = self.__clientRPC(function, params)
        status = nttable.getValue(0)
        return status[0]
    
if __name__ == '__main__':
    mc = client()
    mc.retrieveSystemList()
    params = {'system': 'bd1',
              'servicename': 'masar'}
    mc.retrieveServiceConfigs(params)
#    retrieveServiceConfigProps()
#    retrieveServiceEvents()
#    retrieveSnapshot()

    #    params = {'configname': 'sr_bpm',
    #              'servicename': 'masar'}
#        params = {'configname': 'sr_test',
#                  'servicename': 'masar'}

    params = {'configname': 'ltbd1_quad',
              'servicename': 'masar'}
    if mc.saveSnapshot(params):
        print ("Successfully saved a snapshot.")
    else:
        print ("Failed to save a snapshot.")
    # example to operate a nttable
#    valueCounts = nttable.getNumberValues()
#    print (valueCounts)
#    label = nttable.getLabel()
#    print (label)
#    for i in range(valueCounts):
#        value = nttable.getValue(i)
#        print (value)
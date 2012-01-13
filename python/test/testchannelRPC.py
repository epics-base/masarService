from channelRPC import ChannelRPC as ChannelRPC
from ntnameValue import NTNameValue as NTNameValue
from nttable import NTTable as NTTable
from alarm import Alarm as Alarm
from timeStamp import TimeStamp as TimeStamp

alarm = Alarm()
timeStamp = TimeStamp()

#function = "saveMasar"
#params = {'function': 'saveMasar',
#          'servicename': 'masar',
#          'configname': 'test',
#          'comment': 'this is a comment'
#          }

#function = 'retrieveMasar'
#params = {'eventid': 35}

def testRPC(function, params):
    ntnv = NTNameValue(function,params)
    print ntnv
    
#    channelRPC = ChannelRPC("masarService")
#    if not channelRPC.connect(1.0) :
#        print channelRPC.getMessage()
#        exit(1)
#    result =  channelRPC.request(ntnv.getNTNameValue(),False)
#    if(result==None) :
#        print channelRPC.getMessage()
#        exit(1)
#    nttable = NTTable(result)
#    print nttable
#    
    # now do issue + wait
    channelRPC = ChannelRPC("masarService","record[process=true]field()")
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
    print nttable
    
    nttable.getAlarm(alarm.getAlarmPy())
    print alarm;
    
    nttable.getTimeStamp(timeStamp.getTimeStampPy())
    print timeStamp;
    
    numberValues = nttable.getNumberValues()
    print "numberValues",numberValues
    
    label = nttable.getLabel()
    print "label",label
    
    i = 0
    while i < numberValues :
        value = nttable.getValue(i)
        print "value",label[i],value
        i += 1

if __name__ == '__main__':
# ======    
    function = 'retrieveServiceConfigs'
    print ("=== test %s ===" %function)
    params = {'system': 'sr'
              }
    testRPC(function, params)
    print ("=== test %s end ===" %function)

# ======    
    function = 'retrieveServiceConfigProps'
    print ("=== test %s ===" %function)
    params = {'propname': 'system', 
              'configname': 'sr_qs'
              }
    testRPC(function, params)
    print ("=== test %s end ===" %function)
# ======    
    function = 'retrieveServiceEvents'
    print ("=== test %s ===" %function)
    params = {'configid': '1'}
    testRPC(function, params)
    print ("=== test %s end ===" %function)

# ======    
#    function = 'retrieveMasar'
#    print ("=== test %s ===" %function)
#    params = {'eventid': '56'}
#    testRPC(function, params)
#    print ("=== test %s end ===" %function)


from channelRPC import ChannelRPC as ChannelRPC
from ntnameValue import NTNameValue as NTNameValue
from nttable import NTTable as NTTable
from alarm import Alarm as Alarm
from timeStamp import TimeStamp as TimeStamp

alarm = Alarm()
timeStamp = TimeStamp()

function = "saveSnapshot"
args = { "name0" : "value0",
         "name1" : "value1"
       }

ntnv = NTNameValue(function,args)
print ntnv

channelRPC = ChannelRPC("masarService")
if not channelRPC.connect(1.0) :
    print channelRPC.getMessage()
    exit(1)
result =  channelRPC.request(ntnv.getNTNameValue(),False)
if(result==None) :
    print channelRPC.getMessage()
    exit(1)
nttable = NTTable(result)
print nttable
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

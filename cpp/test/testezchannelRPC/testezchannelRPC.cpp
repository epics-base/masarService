/*testezchannelRPC.cpp */

/* Author: Marty Kraimer */

#include <pv/CDRMonitor.h>
#include <pv/ezchannelRPC.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;

static String channelName("masarService");

static void dump(EZChannelRPC::shared_pointer const & channelRPC)
{
    printf("%s\n",channelRPC->getMessage().c_str());
}

void test()
{
    EZChannelRPC::shared_pointer channelRPC = 
        EZChannelRPC::shared_pointer(new EZChannelRPC(channelName));
    bool result = channelRPC->connect(1.0);
    if(!result) {dump(channelRPC); return;}
    PVStructure::shared_pointer pvNameValue
        = NTNameValue::create(true,false,false);
    NTNameValue ntNameValue(pvNameValue);
    PVString * pvFunction = ntNameValue.getFunction();
    PVStringArray *pvNames = ntNameValue.getNames();
    PVStringArray *pvValues = ntNameValue.getValues();
    int n = 1;
    String name[] = {String("system")};
    String value[] = {String("sr")};
    pvNames->put(0,n,name,0);
    pvValues->put(0,n,value,0);
    pvFunction->put("retrieveServiceConfigs");
    PVStructure::shared_pointer pvResponse = channelRPC->request(pvNameValue,false);
    if(pvResponse.get()==0) {dump(channelRPC); return;}
    String builder;
    pvResponse->toString(&builder);
    printf("response\n%s\n",builder.c_str());
    channelRPC->destroy();
}

int main(int argc,char *argv[])
{
    test();
    epicsThreadSleep(1.0);
    epicsExitCallAtExits();
    epicsThreadSleep(1.0);
    CDRMonitor::get().show(stdout,true);
}

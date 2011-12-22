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
    CreateRequest::shared_pointer createRequest = getCreateRequest();
    PVStructure::shared_pointer pvRequest = 
         createRequest->createRequest("record[process=true]field()");
    EZChannelRPC::shared_pointer channelRPC = 
        EZChannelRPC::shared_pointer(new EZChannelRPC(channelName,pvRequest));
    bool result = channelRPC->connect(1.0);
    if(!result) {dump(channelRPC); return;}
    PVStructure::shared_pointer pvNameValue
        = NTNameValue::create(true,false,false);
    NTNameValue ntNameValue(pvNameValue);
    PVString * pvFunction = ntNameValue.getFunction();
    PVStringArray *pvNames = ntNameValue.getNames();
    PVStringArray *pvValues = ntNameValue.getValues();
    int n = 2;
    String name[] = {String("name 0"),String("name 1")};
    String value[] = {String("value 0"),String("value 1")};
    pvNames->put(0,n,name,0);
    pvValues->put(0,n,value,0);
    pvFunction->put("test");
    result = channelRPC->request(pvNameValue,false);
    if(!result) {dump(channelRPC); return;}
    epics::pvData::PVStructure::shared_pointer pvReponse =
        channelRPC->getResponse();
    String builder;
    pvReponse->toString(&builder);
    printf("response\n%s\n",builder.c_str());
    channelRPC->destroy();
}

int main(int argc,char *argv[])
{
    test();
    epicsThreadSleep(2.0);
    epicsExitCallAtExits();
    CDRMonitor::get().show(stdout,true);
}

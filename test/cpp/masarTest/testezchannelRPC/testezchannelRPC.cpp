/*testezchannelRPC.cpp */

/* Author: Marty Kraimer */

#include <pv/ezchannelRPC.h>

#include <pv/nttable.h>
#include <pv/ntnameValue.h>

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
    NTNameValuePtr ntNameValue
        = NTNameValue::create(true,false,false);
    PVStringPtr & pvFunction = ntNameValue->getFunction();
    PVStringArrayPtr & pvNames = ntNameValue->getNames();
    PVStringArrayPtr & pvValues = ntNameValue->getValues();
    int n = 1;
//    String name[] = {String("system")};
//    String value[] = {String("sr")};
    String name[] = {String("eventid")};
    String value[] = {String("19")};
//    int n = 2;
//    String name[] = {String("configname"), String("servicename")};
//    String value[] = {String("sr_test"), String("masar")};
    pvNames->put(0,n,name,0);
    pvValues->put(0,n,value,0);
//    pvFunction->put("retrieveServiceConfigs");
//    pvFunction->put("saveMasar");
    pvFunction->put("retrieveSnapshot");
    PVStructure::shared_pointer pvResponse = channelRPC->request(ntNameValue->getPVStructure(),false);
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
}

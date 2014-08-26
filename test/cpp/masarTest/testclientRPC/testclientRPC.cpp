/*testChannelRPCC.cpp */

/* Author: Marty Kraimer */

#include <epicsExit.h>
#include <pv/thread.h>
#include <pv/event.h>
#include <pv/rpcClient.h>
#include <pv/clientFactory.h>

#include <pv/nttable.h>
#include <pv/ntnameValue.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;

static String channelName("masarService");

static void dump(RPCClientPtr const & channelRPC)
{
    cout << channelRPC->getMessage() << endl;
}

void test()
{
    RPCClientPtr channelRPC = 
        RPCClientPtr(RPCClient::create(channelName,PVStructurePtr()));
    bool result = channelRPC->connect(1.0);
    if(!result) {dump(channelRPC); return;}
    NTNameValuePtr ntNameValue
        = NTNameValue::create(true,false,false);
    PVStringPtr pvFunction = ntNameValue->getFunction();
    PVStringArrayPtr pvNames = ntNameValue->getNames();
    PVStringArrayPtr pvValues = ntNameValue->getValues();
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
    PVStructurePtr pvResponse = channelRPC->request(ntNameValue->getPVStructure(),false);
    if(pvResponse==NULL) {dump(channelRPC); return;}
    cout << "response\n" << pvResponse->dumpValue(cout) << endl;
    channelRPC->destroy();
}

int main(int argc,char *argv[])
{
    ClientFactory::start();
    test();
    ClientFactory::stop();
}

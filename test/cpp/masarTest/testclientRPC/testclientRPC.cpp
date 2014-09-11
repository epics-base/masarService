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
using namespace epics::nt;

FieldCreatePtr fieldCreate = getFieldCreate();

typedef std::tr1::shared_ptr<RPCClient> RPCClientPtr;

static string channelName("masarService");

void test()
{
    RPCClientPtr channelRPC = 
        RPCClientPtr(RPCClient::create(channelName));
    bool result = channelRPC->connect(1.0);
    if(!result) {
        cout<< "connect failed\n";
        return;
    }
    NTNameValueBuilderPtr builder = NTNameValue::createBuilder();
    NTNameValuePtr ntnamevalue = builder ->
         value(pvString) ->
         add("function",fieldCreate->createScalar(pvString)) ->
         create();
    PVStructurePtr pv = ntnamevalue->getPVStructure();
    PVStringPtr pvFunction = pv->getSubField<PVString>("function");
    PVStringArrayPtr pvNames = pv->getSubField<PVStringArray>("names");
    PVStringArrayPtr pvValues = pv->getSubField<PVStringArray>("values");
    size_t n = 2;
    shared_vector<string> name(n);
    shared_vector<string> value(n);
    name[0] = string("configname");
    name[1] = string("servicename");
    value[0] = string("test");
    value[1] = string("masar");
    pvNames->replace(freeze(name));
    pvValues->replace(freeze(value));
    pvFunction->put("retrieveSnapshot");
    try {
cout << *ntnamevalue->getPVStructure() << endl;
        PVStructurePtr pvResponse = channelRPC->request(ntnamevalue->getPVStructure());
        cout << *pvResponse << endl;
    } catch (std::exception &e)
    {
        cout << e.what() << endl;
        return;
    }
    channelRPC->destroy();
}

int main(int argc,char *argv[])
{
    ClientFactory::start();
    test();
    ClientFactory::stop();
}

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
    size_t n = 11;
    shared_vector<string> name(n);
    shared_vector<string> value(n);
    value[0] = "masarExample0000";
    value[1] = "masarExample0001";
    value[2] = "masarExample0002";
    value[3] = "masarExample0003";
    value[4] = "masarExample0004";
    value[5] = "masarExampleCharArray";
    value[6] = "masarExampleStringArray";
    value[7] = "masarExampleLongArray";
    value[8] = "masarExampleDoubleArray";
    value[9] = "masarExampleBoUninit";
    value[10] = "masarExampleMbboUninit";
    for(size_t i=0; i<n; ++i) name[i] = "";
    pvNames->replace(freeze(name));
    pvValues->replace(freeze(value));
    pvFunction->put("getLiveMachine");
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

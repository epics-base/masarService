/*gatherV3DataTest.cpp */

/* Author: Marty Kraimer */

#include <sstream>

#include <pv/gatherV3Data.h>
#include <pv/clientFactory.h>
#include <pv/caProvider.h>


using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::masar;
using namespace epics::nt;

void testGet(bool debug,GatherV3DataPtr gather)
{
    NTMultiChannelPtr ntmultiChannel = gather->getNTMultiChannel();
    cout << "calling gather->get\n";
    bool result = gather->get();
    if(!result) cout << "get failed\n";
    if(debug) {
        cout << *ntmultiChannel->getPVStructure() << endl;
    }
    PVUnionArrayPtr values = ntmultiChannel->getValue();
    PVIntArrayPtr severitys = ntmultiChannel->getSeverity();
    PVBooleanArrayPtr isConnecteds = ntmultiChannel->getIsConnected();
    PVStringArrayPtr channelNames = ntmultiChannel->getChannelName();
    if(debug) {
        cout << "value " << *values << endl;
        cout << "severity " << *severitys << endl;
        cout << "isConnected " << *isConnecteds << endl;
        cout << "channelName " << *channelNames << endl;
    }
}

void testConnect(bool debug,GatherV3DataPtr gather)
{
    cout << "calling gather->connect\n";
    bool result = gather->connect(5.0);
    if(!result) {
        cout << "connect failed " << gather->getMessage() << endl;
        cout << "This test requires the test V3 database"
           " of the gather service.\n"; 
        cout << "It must be started before running this test\n";
    }
    testGet(debug,gather);
    testGet(debug,gather);
    cout << "calling gather->disconnect\n";
    gather->disconnect();
}

void test(bool debug, size_t count)
{
    size_t n = 1000;
    if(debug) n = count;
    shared_vector<string> names(n);
    char name[40];
    for(size_t i=0; i<n; i++) {
        sprintf(name,"masarExample%4.4d",(int)i);
        names[i] = string(name);
    }
    shared_vector<const string> channelName(freeze(names));
    GatherV3DataPtr gather = GatherV3Data::create(channelName);
    NTMultiChannelPtr ntmultiChannel = gather->getNTMultiChannel();
    if(debug) {
        cout << *ntmultiChannel->getPVStructure() << endl;
    }
    testConnect(debug,gather);
    testConnect(debug,gather);
}

int main(int argc,char *argv[])
{
    ClientFactory::start();
    ::epics::pvAccess::ca::CAClientFactory::start();
    bool debug = false;
    if(argc>1) {
        char * arg = argv[1];
        if(strcmp(arg,"debug")==0) {
           cout << "debug is true\n";
           debug = true;
        }
    }
    size_t n = 10;
    if(argc>2){
        n = atoi(argv[2]);
    }
    test(debug, n);
    return(0);
}


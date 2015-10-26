/*gatherV3DataExample.cpp */

/* Author: Marty Kraimer */

#include <sstream>
#include "epicsThread.h"

#include <pv/gatherV3Data.h>
#include <pv/clientFactory.h>
#include <pv/caProvider.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::masar;
using namespace epics::nt;

void test()
{
    size_t n = 1000;
    shared_vector<string> names(n);
    char name[40];
    for(size_t i=0; i<n; i++) {
        sprintf(name,"masarExample%4.4d",(int)i);
        names[i] = string(name);
    }
    shared_vector<const string> channelName(freeze(names));
    GatherV3DataPtr gather = GatherV3Data::create(channelName);
    bool result = gather->connect(10.0);
    if(!result) {
        cout << "connect failed " << gather->getMessage() << endl;
        cout <<"This test requires the test V3 database"
           " of the gather service.\n";
        cout << "It must be started before running this test\n";
        return;
    }
    for(int ntimes=0; ntimes<10; ++ntimes) {
        cout << "calling get ntime " << ntimes << endl;
        result = gather->get();
        if(!result) cout <<"get failed " << gather->getMessage() << endl;
        NTMultiChannelPtr multi = gather->getNTMultiChannel();
        PVBooleanArrayPtr isConnected = multi->getIsConnected();
        shared_vector<const boolean> data = isConnected->view();
        for(size_t i=0; i<n; i++) {
            if(!data[i]) {
                cout << "channel " << channelName[i] << " not connected\n";
            }
        }
    }
    gather->destroy();
}

int main(int argc,char *argv[])
{
    ClientFactory::start();
    ::epics::pvAccess::ca::CAClientFactory::start();
    test();
    ::epics::pvAccess::ca::CAClientFactory::stop();
    ClientFactory::stop();
    return 0;
}


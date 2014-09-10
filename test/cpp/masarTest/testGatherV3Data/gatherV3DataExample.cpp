/*gatherV3DataExample.cpp */

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

NTMultiChannelPtr getLiveMachine(
        shared_vector<const string> const & channelName )
{
    GatherV3DataPtr gather = GatherV3Data::create(channelName);

    // wait one second, which is a magic number for now.
    // The waiting time might be removed later after stability test.
    bool result = gather->connect(1.0);
    if(!result) {
        cout << "connect failed\n";
        cout << "This test requires the test V3 database of the gather service.\n";
        cout << "It must be started before running this test\n";
    }
    result = gather->get();

    NTMultiChannelPtr ntmultiChannel = gather->getNTMultiChannel();
    cout << *ntmultiChannel->getPVStructure() << endl;

    cout << "isConnected " << *ntmultiChannel->getIsConnected() << endl;
    gather->destroy();
    return ntmultiChannel;
}


void test()
{
    size_t n = 11;
    shared_vector<string> channelName(n);
    channelName[0] = "masarExample0000";
    channelName[1] = "masarExample0001";
    channelName[2] = "masarExample0002";
    channelName[3] = "masarExample0003";
    channelName[4] = "masarExample0004";
    channelName[5] = "masarExampleCharArray";
    channelName[6] = "masarExampleStringArray";
    channelName[7] = "masarExampleLongArray";
    channelName[8] = "masarExampleDoubleArray";
    channelName[9] = "masarExampleBoUninit";
    channelName[10] = "masarExampleMbboUninit";

    shared_vector<const string> xxx(freeze(channelName));

    NTMultiChannelPtr pvt = getLiveMachine(xxx);
    pvt = getLiveMachine(xxx);
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


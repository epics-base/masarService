/*testDSLGetLiveMachine.cpp */

/* Author: Marty Kraimer */

#include <epicsExit.h>
#include <pv/thread.h>
#include <pv/event.h>
#include <pv/clientFactory.h>
#include <pv/caProvider.h>

#include <pv/dslPY.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::masar;

void test()
{
    DSLPtr dslRdb(createDSL_RDB());
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
    const shared_vector<const string> names(freeze(name));
    const shared_vector<const string> values(freeze(value));
    try {
        PVStructurePtr pvResponse = dslRdb->request(
             "getLiveMachine",names,values);
        cout << *pvResponse << endl;
    } catch (std::exception &e)
    {
        cout << e.what() << endl;
        return;
    }
    for(int i=0; i<3; ++i) {
        try {
            PVStructurePtr pvResponse = dslRdb->request(
                 "getLiveMachine",names,values);
            cout << "alarm.message ";
            cout << pvResponse->getSubField<PVString>("alarm.message")->get() << endl;
        } catch (std::exception &e)
        {
            cout << e.what() << endl;
            return;
        }
    }
}

int main(int argc,char *argv[])
{
    ClientFactory::start();
    ::epics::pvAccess::ca::CAClientFactory::start();
    test();
    ::epics::pvAccess::ca::CAClientFactory::stop();
    ClientFactory::stop();
}

/*testRetrieveServiceConfigs.cpp */

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

FieldCreatePtr fieldCreate = getFieldCreate();

void test()
{
    DSLPtr dslRdb(createDSL_RDB());
    size_t n = 2;
    shared_vector<string> name(n);
    shared_vector<string> value(n);
    name[0] = "configname";
    value[0] = "test";
    name[1] = "servicename";
    value[1] = "masar";
    const shared_vector<const string> names(freeze(name));
    const shared_vector<const string> values(freeze(value));
    try {
        PVStructurePtr pvResponse = dslRdb->request(
             "retrieveServiceConfigs",names,values);
        cout << *pvResponse << endl;
    } catch (std::exception &e)
    {
        cout << e.what() << endl;
        return;
    }
}

int main(int argc,char *argv[])
{
    ClientFactory::start();
    ::epics::pvAccess::ca::CAClientFactory::start();
    test();
//    ::epics::pvAccess::ca::CAClientFactory::stop();
    ClientFactory::stop();
}

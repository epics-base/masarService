/*masarServiceRun.cpp */

/* Author: Marty Kraimer */

#include <cstddef>
#include <cstdlib>
#include <cstddef>
#include <string>
#include <cstdio>
#include <memory>
#include <iostream>

#include <cantProceed.h>
#include <epicsStdio.h>
#include <epicsMutex.h>
#include <epicsEvent.h>
#include <epicsThread.h>
#include <epicsExit.h>
#include <epicsExport.h>

#include <pv/clientFactory.h>
#include <pv/pvIntrospect.h>
#include <pv/pvData.h>
#include <pv/rpcServer.h>
#include <pv/masarService.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::masar;


void masarService(const char * name)
{
    RPCServer::shared_pointer rpcServer(new RPCServer());
    MasarService::shared_pointer service(MasarService::shared_pointer(new MasarService()));
    rpcServer->registerService(name,service);
    cout << "===Starting channel RPC server: " << name << endl;
    cout << "===Use CTRl-Z to stop " << name << " server." << endl;
    rpcServer->run();
}

int main(int argc,char *argv[])
{
    ClientFactory::start();
    ServerContext::shared_pointer pvaServer =
        startPVAServer(PVACCESS_ALL_PROVIDERS,0,true,true);
    const char *name = "masarService";
    if(argc>1) name = argv[1];
    std::cout << name << endl;
    masarService(name);
    pvaServer->shutdown();
    epicsThreadSleep(1.0);
    pvaServer->destroy();
    return (0);
}

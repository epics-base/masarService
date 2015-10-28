/*masarServiceRun.cpp */

/* Author: Marty Kraimer */

#include <cstddef>
#include <cstdlib>
#include <cstddef>
#include <string>
#include <cstdio>
#include <memory>
#include <iostream>
#include <signal.h>

#include <pv/clientFactory.h>
#include <pv/caProvider.h>

#include <cantProceed.h>
#include <epicsStdio.h>
#include <epicsMutex.h>
#include <epicsEvent.h>
#include <epicsThread.h>
#include <epicsExit.h>
#include <epicsExport.h>
#include <iocsh.h>

#include <pv/pvIntrospect.h>
#include <pv/pvData.h>
#include <pv/rpcServer.h>
#include <pv/masarService.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::masar;


void sighandler(int sig)
{
    /*
    Some of the more commonly used signals:
    1       HUP (hang up)
    2       INT (interrupt)
    3       QUIT (quit)
    6       ABRT (abort)
    9       KILL (non-catchable, non-ignorable kill)
    14      ALRM (alarm clock)
    15      TERM (software termination signal)
    */
    cout << endl <<"===Signal " << sig << " Caught..." << endl;
    cout << "===Use CTRl-D or exit() command to stop server." << endl;
}

struct ThreadRunnerParam {
    RPCServer::shared_pointer server;
    int timeToRun;
};

static void threadRunner(void* usr)
{
    ThreadRunnerParam* pusr = static_cast<ThreadRunnerParam*>(usr);
    ThreadRunnerParam param = *pusr;
    delete pusr;

    param.server->run(param.timeToRun);
}

int main(int argc,char *argv[])
{
    ClientFactory::start();
    ::epics::pvAccess::ca::CAClientFactory::start();
    const char *name = "masarService";
    if(argc>1) name = argv[1];

    // register SIGNAL ABORT, TERM, and INT
    signal(SIGABRT, &sighandler);
    signal(SIGTERM, &sighandler);
    signal(SIGINT,  &sighandler);
    // set the prompt to the service name
    setenv("IOCSH_PS1", "masarService> ", 1);
    RPCServer::shared_pointer rpcServer(new RPCServer());
    MasarService::shared_pointer service(MasarService::shared_pointer(new MasarService()));
    rpcServer->registerService(name, RPCService::shared_pointer(service));
    rpcServer->printInfo();

    cout << "===Starting channel RPC server: " << name << endl;
    cout << "===Use CTRl-D or exit() command to stop server." << endl;

    {
        auto_ptr<ThreadRunnerParam> param(new ThreadRunnerParam());
        param->server = rpcServer;
        param->timeToRun = 0.0; // Let the server run forever until getting exit() or CTRL-D

        epicsThreadCreate("masar server thread",
                          epicsThreadPriorityMedium,
                          epicsThreadGetStackSize(epicsThreadStackBig),
                          threadRunner, param.get());

        // let the thread delete 'param'
        param.release();
    }

    iocsh(NULL);
    rpcServer->destroy();
    return (0);
}

#ifdef XXXXX
int main(int argc,char *argv[])
{
    ClientFactory::start();
    ::epics::pvAccess::ca::CAClientFactory::start();
    const char *name = "masarService";
    if(argc>1) name = argv[1];
    RPCServer server;
    MasarService::shared_pointer service(MasarService::shared_pointer(new MasarService()));
    server.registerService(name,service);
    service.reset();
    server.printInfo();
    server.run();
    return 0;
}
#endif


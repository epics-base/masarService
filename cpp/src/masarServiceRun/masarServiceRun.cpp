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
//#include <pv/pvAccess.h>
//#include <pv/serverContext.h>
//#include <pv/pvDatabase.h>
#include <pv/pvServiceProvider.h>
#include <pv/masarService.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::pvIOC;
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

void masarService(const char * name)
{
    PVServiceChannelCTX::shared_pointer myCTX = PVServiceChannelCTX::getPVServiceChannelCTX();
    MasarService::shared_pointer service(MasarService::shared_pointer(new MasarService()));
    ServiceChannelRPC::shared_pointer serviceChannelRPC(new ServiceChannelRPC(name,service));

    cout << "===Starting channel RPC server: " << name << endl;
    cout << "===Use CTRl-D or exit() command to stop " << name << " server." << endl;

    iocsh(NULL);
}

int main(int argc,char *argv[])
{
    const char *name = "masarService";
    if(argc>1) name = argv[1];

    // register SIGNAL ABORT, TERM, and INT
    signal(SIGABRT, &sighandler);
    signal(SIGTERM, &sighandler);
    signal(SIGINT, &sighandler);

    // set the prompt to the service name
    setenv("IOCSH_PS1", "masarService> ", 1);

    masarService(name);

    epicsExitCallAtExits();
    epicsThreadSleep(1.0);
    return (0);
}

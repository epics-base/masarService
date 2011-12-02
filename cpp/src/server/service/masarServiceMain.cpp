/*masarServiceMain.cpp */

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

#include <epicsExport.h>

#include <pv/pvIntrospect.h>
#include <pv/pvData.h>
#include <pv/pvAccess.h>
#include <pv/serverContext.h>

#include <pv/pvDatabase.h>
#include <pv/pvServiceProvider.h>
#include <pv/masarService.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::pvIOC;
using namespace epics::masar;

int main(int argc,char *argv[])
{
    PVServiceChannelCTX::shared_pointer myCTX
        = PVServiceChannelCTX::shared_pointer(new PVServiceChannelCTX());
    MasarService::shared_pointer service
        = MasarService::shared_pointer(new MasarService());
    ServiceChannelRPC::shared_pointer serviceChannelRPC
        = ServiceChannelRPC::shared_pointer(
            new ServiceChannelRPC("masarService",service));
    cout << "masarService\n";
    string str;
    while(true) {
        cout << "Type exit to stop: \n";
        getline(cin,str);
        if(str.compare("exit")==0) break;
        
    }
    return(0);
}


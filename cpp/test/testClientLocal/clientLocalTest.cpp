/*clientLocalTest.cpp */

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
#include <pv/nt.h>

#include <pv/pvDatabase.h>
#include <pv/masarService.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvIOC;
using namespace epics::pvAccess;
using namespace epics::masar;

// following is just temporary until remote is ready

class LocalRPC :
    public ChannelRPCRequester,
    public std::tr1::enable_shared_from_this<LocalRPC>
{
public:
    POINTER_DEFINITIONS(LocalRPC);
    LocalRPC(MasarService::shared_pointer const &  masarService);
    PVStructure::shared_pointer request(
        PVStructure::shared_pointer const & pvArgument);
    virtual ~LocalRPC(){}
    virtual void channelRPCConnect(
        const Status& status,ChannelRPC::shared_pointer const & channelRPC){}
    virtual void requestDone(
        const Status& status,PVStructure::shared_pointer const & pvResponse);
    virtual String getRequesterName(){return "localRPC";}
    virtual void message(String message,MessageType messageType)
    { printf("message %s\n",message.c_str());}

private:
    LocalRPC::shared_pointer getPtrSelf()






    {
        return shared_from_this();
    }
    MasarService::shared_pointer masarService;
    PVStructure::shared_pointer pvResponse;
};

LocalRPC::LocalRPC(MasarService::shared_pointer const &  masarService)
: masarService(masarService),
  pvResponse(PVStructure::shared_pointer())
{}

PVStructure::shared_pointer LocalRPC::request(
    PVStructure::shared_pointer const & pvArgument)
{
     masarService->request(getPtrSelf(),pvArgument);
     return pvResponse;
}

void LocalRPC::requestDone(
    const Status& status,PVStructure::shared_pointer const & pvResponse)
{
    if(!status.isSuccess()) {
        String message("bad status:");
        message += status.getMessage();
        throw std::invalid_argument(message);
    }
    this->pvResponse = pvResponse;
}




int main(int argc,char *argv[])
{
    MasarService::shared_pointer service
        = MasarService::shared_pointer(new MasarService());
    LocalRPC::shared_pointer rpc
        = LocalRPC::shared_pointer(new LocalRPC(service));
    PVStructure::shared_pointer pvNameValue
        = NTNameValuePair::create(true,false,false);
    NTNameValuePair ntNameValuePair(pvNameValue);
    PVString * pvFunction = ntNameValuePair.getFunction();
    PVStringArray *pvNames = ntNameValuePair.getNames();
    PVStringArray *pvValues = ntNameValuePair.getValues();
    int n = 2;
    String name[] = {String("name 0"),String("name 1")};
    String value[] = {String("value 0"),String("value 1")};
    pvNames->put(0,n,name,0);
    pvValues->put(0,n,value,0);
    pvFunction->put("test");
    PVStructure::shared_pointer pvResult = rpc->request(pvNameValue);
    String builder;
    pvResult->toString(&builder);
    printf("result\n%s\n",builder.c_str());
    return(0);
}


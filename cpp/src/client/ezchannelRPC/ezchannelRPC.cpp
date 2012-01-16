/* ezchannelRPC.cpp */
/*
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Author Marty Kraimer 2011.12 */


#include <pv/ezchannelRPC.h>

namespace epics { namespace pvAccess { 

using namespace epics::pvData;

static void deleteStatic(void *)
{
// If the following is called python will crash.
//    ClientFactory::stop();
}

static void initStatic(void *) {
    ClientFactory::start();
    epicsAtExit(&deleteStatic,0);
}

static epicsThreadOnceId initOnce = EPICS_THREAD_ONCE_INIT;

EZChannelRPC::EZChannelRPC(
    String channelName)
: channelName(channelName),
  pvRequest(getCreateRequest()->createRequest("record[process=true]field()")),
  requesterName("ezchannelRPC"),
  isOK(true)
{
    epicsThreadOnce(&initOnce, &initStatic, 0);
}

EZChannelRPC::EZChannelRPC(
    String channelName,
    PVStructure::shared_pointer pvRequest)
: channelName(channelName),
  pvRequest(pvRequest),
  requesterName("ezchannelRPC"),
  isOK(true)
{
    epicsThreadOnce(&initOnce, &initStatic, 0);
}

EZChannelRPC::~EZChannelRPC()
{
}

void EZChannelRPC::destroy()
{
    Lock xx(mutex);
    if(channel.get()!=0) {
        channel->destroy();
        channel.reset();
        pvRequest.reset();
        channelRPC.reset();
        pvResponse.reset();
    }
}

bool EZChannelRPC::connect(double timeOut)
{
    issueConnect();
    return waitConnect(timeOut);
}

void EZChannelRPC::issueConnect()
{
    event.tryWait(); // make sure event is empty
    ChannelAccess::shared_pointer const &channelAccess = getChannelAccess();
    ChannelProvider::shared_pointer const &channelProvider
         = channelAccess->getProvider(String("pvAccess"));
    channel = channelProvider->createChannel(
        channelName,
        getPtrSelf(),
        ChannelProvider::PRIORITY_DEFAULT);
}

bool EZChannelRPC::waitConnect(double timeOut) {
    // wait for channel to connect
    bool ok = event.wait(timeOut);
    if(!ok) return ok;
    channelRPC = channel->createChannelRPC(getPtrSelf(),pvRequest);
    event.wait();
    return isOK;
}

epics::pvData::PVStructure::shared_pointer EZChannelRPC::request(
    PVStructure::shared_pointer const & pvArgument,
    bool lastRequest)
{
    issueRequest(pvArgument,lastRequest);
    return waitRequest();
}

void EZChannelRPC::issueRequest(
    PVStructure::shared_pointer const & pvArgument,
    bool lastRequest)
{
    event.tryWait(); // make sure event is empty
    channelRPC->request(pvArgument,lastRequest);
}

epics::pvData::PVStructure::shared_pointer EZChannelRPC::waitRequest()
{
    bool ok = event.wait();
    if(!ok) {
        isOK = false;
        lastMessage = "event.wait failed\n";
        pvResponse = epics::pvData::PVStructure::shared_pointer();
    }
    return pvResponse;
}

String EZChannelRPC::getMessage() { return lastMessage;}


void EZChannelRPC::channelCreated(
    const Status& status,
    Channel::shared_pointer const & channel)
{
//printf("EZChannelRPC::channelCreate\n");
    isOK = status.isOK();
    this->channel = channel;
    if(!isOK) {
        String message = Status::StatusTypeName[status.getType()];
        message += " " + status.getMessage();
        lastMessage = message;
        event.signal();
    }
}

void EZChannelRPC::channelStateChange(
    Channel::shared_pointer const & channel,
    Channel::ConnectionState connectionState)
{
    this->channel = channel;
    this->connectionState = connectionState;
    event.signal();
}

String EZChannelRPC::getRequesterName(){ return requesterName;}

void EZChannelRPC::message(String message,MessageType messageType)
{
    lastMessage = epics::pvData::messageTypeName[messageType];
    lastMessage += " " + message;
}

void EZChannelRPC::channelRPCConnect(
    const Status& status,
    ChannelRPC::shared_pointer const & channelRPC)
{
    this->channelRPC = channelRPC;
    if(!status.isOK()) {
        isOK = false;
        String message = Status::StatusTypeName[status.getType()];
        message += " " + status.getMessage();
        lastMessage = message;
    }
    event.signal();
}

void EZChannelRPC::requestDone(
    const Status& status,
    PVStructure::shared_pointer const & pvResponse)
{
//printf("EZChannelRPC::requestDone\n");
    this->pvResponse = pvResponse;
    if(!status.isOK()) {
        isOK = false;
        String message = Status::StatusTypeName[status.getType()];
        message += " " + status.getMessage();
        lastMessage = message;
    }
    event.signal();
}
    

}}

/* ezchannelRPC.h */
/*
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Author Marty Kraimer 2011.12 */

#ifndef EZCHANNELRPC_H
#define EZCHANNELRPC_H

#include <cstddef>
#include <cstdlib>
#include <cstddef>
#include <string>
#include <cstdio>

#include <cadef.h>
#include <epicsStdio.h>
#include <epicsMutex.h>
#include <epicsEvent.h>
#include <epicsThread.h>
#include <epicsExit.h>


#include <pv/lock.h>
#include <pv/event.h>

#include <pv/pvIntrospect.h>
#include <pv/pvData.h>
#include <pv/pvAccess.h>
#include <pv/clientFactory.h>
#include <pv/alarm.h>
#include <pv/pvAlarm.h>
#include <pv/timeStamp.h>
#include <pv/pvTimeStamp.h>
#include <pv/nt.h>


namespace epics { namespace pvAccess { 

/**
 * This class provides an easy way to make a channelRPC request.
 * The client provides a PVStructure that is the argument for the
 * channelRPC request and receives a PVStructure that holds the result.
 * @author mrk
 *
 */
class EZChannelRPC :
    public ChannelRequester,
    public ChannelRPCRequester,
    public std::tr1::enable_shared_from_this<EZChannelRPC>
{
public:
    POINTER_DEFINITIONS(EZChannelRPC);
    /** Constructor
     * The channelName is the name of the channelRPC server.
     */
    EZChannelRPC(
        epics::pvData::String channelName);
    /** Constructor
     * The channelName is the name of the channelRPC server.
     * pvRequest is a request structure to pass to the server.
     */
    EZChannelRPC(
        epics::pvData::String channelName,
        epics::pvData::PVStructure::shared_pointer pvRequest);
    /**
     * Destructor
     */
    virtual ~EZChannelRPC();
    /** destroy the channelRPC.
     * This will clean up all resources used by the channelRPC
     */
    void destroy();
    /**
     * Connect to the server.
     * The method blocks until the connection is made or a timeout occurs.
     * It is the same as calling issueConnect and then waitConnect.
     * @param timeout timeout in seconds to wait.
     * @returns (false,true) If (not connected, is connected).
     * If false then connect must be reissued.
     */
    bool connect(double timeout);
    /**
     * Issue a connect request and return immediately.
     * waitConnect must be called to complete the request.
     */
    void issueConnect();
    /**
     * Wait for the connect request to complete.
     * @param timeout timeout in seconds to wait.
     * @returns (false,true) If (not connected, is connected).
     * If false then connect must be reissued.
     */
    bool waitConnect(double timeout);
    /**
     * Make a channelRPC request.
     * @param pvArgument The argument to pass to the server.
     * @param lastRequest If true an automatic destroy is made.
     * @returns the result. If the result is null then getMessage can be called to get the reason.
     */
    epics::pvData::PVStructure::shared_pointer  request(
        epics::pvData::PVStructure::shared_pointer const & pvArgument,
        bool lastRequest);
    /**
     * Issue a channelRPC request and return immediately.
     * waitRequest must be called to complete the request.
     * @param pvAgument The argument to pass to the server.
     * @param lastRequest If true an automatic destroy is made.
     */
    void  issueRequest(
        epics::pvData::PVStructure::shared_pointer const & pvArgument,
        bool lastRequest);
    /**
     * Wait for the request to complete.
     * @returns the result. If the result is null then getMessage can be called to get the reason.
     */
    epics::pvData::PVStructure::shared_pointer  waitRequest();
    /**
     * Get the reason why a connect or request failed.
     * @returns the message.
     */
    epics::pvData::String getMessage();
    // remaining methods are callbacks, i.e. not called by user code
    virtual void channelCreated(
        const epics::pvData::Status& status,
        Channel::shared_pointer const & channel);
    virtual void channelStateChange(
        Channel::shared_pointer const & channel,
        Channel::ConnectionState connectionState);
    virtual epics::pvData::String getRequesterName();
    virtual void message(
        epics::pvData::String message,
        epics::pvData::MessageType messageType);
    virtual void channelRPCConnect(
        const epics::pvData::Status& status,
        ChannelRPC::shared_pointer const & channelRPC);
    virtual void requestDone(
        const epics::pvData::Status& status,
        epics::pvData::PVStructure::shared_pointer const & pvResponse);
private:
    EZChannelRPC::shared_pointer getPtrSelf()
    {
        return shared_from_this();
    }
    epics::pvData::String channelName;
    epics::pvData::PVStructure::shared_pointer pvRequest;
    epics::pvData::String requesterName;
    bool isOK;
    epics::pvData::Event event;
    epics::pvData::Mutex mutex;
    epics::pvData::String lastMessage;
    Channel::shared_pointer channel;
    Channel::ConnectionState connectionState;
    ChannelRPC::shared_pointer channelRPC;
    epics::pvData::PVStructure::shared_pointer pvResponse;
};

}}

#endif  /* EZCHANNELRPC_H */

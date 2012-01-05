/* gatherV3Double.h */
/*
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Author Marty Kraimer 2011.11 */

#ifndef GATHERV3DOUBLE_H
#define GATHERV3DOUBLE_H

#include <cstddef>
#include <cstdlib>
#include <cstddef>
#include <string>
#include <cstdio>

#include <cadef.h>
#include <epicsStdio.h>
#include <epicsMutex.h>
#include <epicsEvent.h>

#include <pv/lock.h>
#include <pv/event.h>

#include <pv/pvIntrospect.h>
#include <pv/pvData.h>
#include <pv/alarm.h>
#include <pv/pvAlarm.h>
#include <pv/timeStamp.h>
#include <pv/pvTimeStamp.h>
#include <pv/nt.h>


namespace epics { namespace pvAccess { 

/**
 * Gather an array of V3 scalar double values.
 * The complete set of data is presented as an NTTable.
 * The NTTable has the optional fields alarm and timeStamp.
 * @author mrk
 *
 */
class GatherV3Double :
    public std::tr1::enable_shared_from_this<GatherV3Double>
{
public:
    POINTER_DEFINITIONS(GatherV3Double);
    /**
     * Constructor
     * @param channelNames   The array of channelNames to gather
     * @param numberChannels The number of channels to gather.
     */
    GatherV3Double(epics::pvData::String channelNames[],int numberChannels);
    /**
     * Destructor
     */
    ~GatherV3Double();
    /**
     * Connect to the V3 channels.
     * @param timeOut Timeout is seconds to wait.
     * @returns (false,true) If (not connected, is connected) to all channels.
     * If false then all channels are cleared and connect must be reissued.
     */
    bool connect(double timeOut);
    /**
     * Disconnect from the V3 channels.
     */
    void disconnect();
    /**
     * get the current values of the V3 channels.
     * NOTE: get MUST be called by the same thread that calls connect.
     * @returns (false,true) If (all, not all ) gets were successful.
     * If false getMessage can be called to get the reason.
     * If any channel is disconnected then false is returned.
     */
    bool get();
    /**
     * get the reason why a connect or get failed.
     * @returns the message.
     */
    epics::pvData::String getMessage();
    /**
     * The data is saved as an NTTable with alarm and timeStamp. Get it.
     * @returns the NTTable.
     */
    epics::pvData::PVStructure::shared_pointer getNTTable();
    /**
     * Get the array of values for each V3 channel.
     * @returns The array.
     */
    epics::pvData::PVDoubleArray *getValue();
    /**
     * Get the array of delta times for each V3 channel.
     * This is the time difference relative to the NTTable timeStamp.
     * @returns The array.
     */
    epics::pvData::PVDoubleArray *getDeltaTime();
    /**
     * Get the array of severity value for each V3 channel.
     * @returns The array.
     */
    epics::pvData::PVIntArray *getSeverity();
    /**
     * Get the array of connection state for each V3 channel.
     * @returns The array.
     */
    epics::pvData::PVBooleanArray *getIsConnected();
    /**
     * Get the array of channel names for each V3 channel.
     * @returns The array.
     */
    epics::pvData::PVStringArray  *getChannelName();
private:
    GatherV3Double::shared_pointer getPtrSelf()
    {
        return shared_from_this();
    }
    class GatherV3DoublePvt *pvt;
};

}}

#endif  /* GATHERV3DOUBLE_H */

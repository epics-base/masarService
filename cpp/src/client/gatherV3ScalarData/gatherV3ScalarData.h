/* gatherV3ScalarData.h */
/*
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Author Marty Kraimer 2011.11 */

#ifndef GATHERV3SCALARDATA_H
#define GATHERV3SCALARDATA_H

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
class GatherV3ScalarData :
    public std::tr1::enable_shared_from_this<GatherV3ScalarData>
{
public:
    POINTER_DEFINITIONS(GatherV3ScalarData);
    /**
     * Constructor
     * @param channelNames   The array of channelNames to gather
     * @param numberChannels The number of channels to gather.
     * @param type           The data type. Must be int, double, or string
     */
    GatherV3ScalarData(
        epics::pvData::String channelNames[],
        int numberChannels);
    /**
     * Destructor
     */
    ~GatherV3ScalarData();
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
     * put new values to the V3 channels.
     * NOTE: get MUST be called by the same thread that calls connect.
     * @returns (false,true) If (all, not all ) puts were successful.
     * If false getMessage can be called to get the reason.
     * If any channel is disconnected then false is returned.
     * The data must be in the return values from
     * getLongValue, getDoubleValue, getStringValue.
     * For each channel the one used depends on the channel DBRType.
     */
    bool put();
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
     * @returns The data array.
     * If the data type is not int an empty array is returned.
     */
    epics::pvData::PVLongArray *getLongValue();
    /**
     * Get the array of values for each V3 channel.
     * @returns The data array.
     * If the data type is not double an empty array is returned.
     */
    epics::pvData::PVDoubleArray *getDoubleValue();
    /**
     * Get the array of values for each V3 channel.
     * @returns The array.
     * If the data type is not string an empty array is returned.
     */
    epics::pvData::PVStringArray *getStringValue();
    /**
     * Get the array of secondsPastEpoch for each V3 channel.
     * The epoch is midnight 1970 UTC time.
     * @returns The array of seconds.
     */
    epics::pvData::PVLongArray *getSecondsPastEpoch();
    /**
     * Get the array of nanoSeconds since the seconds.
     * @returns The array of nanoSeconds after the secsPastEpoch.
     */
    epics::pvData::PVIntArray *getNanoSeconds();
    /**
     * Get the array of timeStamp tag for each V3 channel.
     * @returns The array.
     */
    epics::pvData::PVIntArray *getTimeStampTag();
    /**
     * Get the array of alarm severity value for each V3 channel.
     * @returns The array.
     */
    epics::pvData::PVIntArray *getAlarmSeverity();
    /**
     * Get the array of alarm status value for each V3 channel.
     * @returns The array.
     */
    epics::pvData::PVIntArray *getAlarmStatus();
    /**
     * Get the array of alarm messages for each V3 channel.
     * This is just the string value of the status.
     * @returns The array.
     */
    epics::pvData::PVStringArray *getAlarmMessage();
    /**
     * Get the array of native DBR type for each V3 channel.
     * @returns The array.
     */
    epics::pvData::PVIntArray *getDBRType();
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
    GatherV3ScalarData::shared_pointer getPtrSelf()
    {
        return shared_from_this();
    }
    class GatherV3ScalarDataPvt *pvt;
};

}}

#endif  /* GATHERV3SCALARDATA_H */

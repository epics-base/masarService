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


namespace epics { namespace pvData { 

class GatherV3Double :
    public std::tr1::enable_shared_from_this<GatherV3Double>
{
public:
    POINTER_DEFINITIONS(GatherV3Double);
    GatherV3Double(String channelNames[],int numberChannels);
    ~GatherV3Double();
    bool connect(double timeOut);
    void disconnect();
    bool get();
    String getMessage();
    PVStructure::shared_pointer getNTTable();
    PVDoubleArray  *getValue();
    PVDoubleArray  *getDeltaTime();
    PVIntArray     *getSeverity();
    PVBooleanArray *getIsConnected();
    PVStringArray  *getChannelName();
private:
    static void createContext();
    GatherV3Double::shared_pointer getPtrSelf()
    {
        return shared_from_this();
    }
    class GatherV3DoublePvt *pvt;
};

}}

#endif  /* GATHERV3DOUBLE_H */

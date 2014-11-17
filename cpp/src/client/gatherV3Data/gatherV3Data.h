/* gatherV3Data.h */
/*
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Author Marty Kraimer 2011.11 */

#ifndef GATHERV3DATA_H
#define GATHERV3DATA_H

#include <cstddef>
#include <cstdlib>
#include <cstddef>
#include <string>
#include <vector>

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
#include <pv/sharedVector.h>
#include <pv/pvAccess.h>
#include <pv/nt.h>
#include <pv/ntmultiChannel.h>


namespace epics { namespace masar { 

/**
 * Gather an array of V3 scalar double values.
 * The complete set of data is presented as an NTMultiChannel.
 * @author mrk
 *
 */
class GatherV3Data;
typedef std::tr1::shared_ptr<GatherV3Data> GatherV3DataPtr;

namespace detail {

class GatherV3DataChannel;
typedef std::tr1::shared_ptr<GatherV3DataChannel> GatherV3DataChannelPtr;

class GatherV3DataChannel :
    public epics::pvAccess::ChannelRequester,
    public virtual epics::pvAccess::ChannelGetRequester,
    public virtual epics::pvAccess::ChannelPutRequester,
    public std::tr1::enable_shared_from_this<GatherV3DataChannel>
{
public :
    POINTER_DEFINITIONS(GatherV3DataChannel);

    virtual ~GatherV3DataChannel();
    virtual std::string getRequesterName() {return "GatherV3DataChannel";}
    virtual void message(
        std::string const &message,
        epics::pvData::MessageType messageType);
    virtual void channelCreated(
        const epics::pvData::Status& status,
        epics::pvAccess::Channel::shared_pointer const & channel);
    virtual void channelStateChange(
        epics::pvAccess::Channel::shared_pointer const & channel,
        epics::pvAccess::Channel::ConnectionState connectionState);
    virtual void channelGetConnect(
        const epics::pvData::Status& status,
        epics::pvAccess::ChannelGet::shared_pointer const & channelGet,
        epics::pvData::Structure::const_shared_pointer const & structure);
    virtual void getDone(
        const epics::pvData::Status& status,
        epics::pvAccess::ChannelGet::shared_pointer const & channelGet,
        epics::pvData::PVStructure::shared_pointer const & pvStructure,
        epics::pvData::BitSet::shared_pointer const & bitSet);
    virtual void channelPutConnect(
        const epics::pvData::Status& status,
        epics::pvAccess::ChannelPut::shared_pointer const & channelPut,
        epics::pvData::Structure::const_shared_pointer const & structure);
    virtual void putDone(
        const epics::pvData::Status& status,
        epics::pvAccess::ChannelPut::shared_pointer const & channelPut);
    virtual void getDone(
        const epics::pvData::Status& status,
        epics::pvAccess::ChannelPut::shared_pointer const & channelPut,
        epics::pvData::PVStructure::shared_pointer const & pvStructure,
        epics::pvData::BitSet::shared_pointer const & bitSet);
private:
    GatherV3DataChannel::shared_pointer getPtrSelf()
    {
        return shared_from_this();
    }
    GatherV3DataChannel(GatherV3DataPtr const& gatherV3Data, size_t offset);
    void init();
    void connect();
    void createGet();
    void get();
    void createPut();
    void put();
    void destroy();

    GatherV3DataPtr gatherV3Data;
    size_t offset;
    epics::pvAccess::Channel::shared_pointer channel;
    epics::pvAccess::ChannelGet::shared_pointer channelGet;
    epics::pvAccess::ChannelPut::shared_pointer channelPut;
    bool beingDestroyed;
    friend class epics::masar::GatherV3Data;
};
}

class GatherV3Data :
    public std::tr1::enable_shared_from_this<GatherV3Data>
{
public:
    POINTER_DEFINITIONS(GatherV3Data);
    /**
     * Factory
     * @param channelNames   The array of channelNames to gather
     */
    static GatherV3DataPtr create(
        epics::pvData::shared_vector<const std::string> const & channelNames);
    /**
     * Destructor
     */
    ~GatherV3Data();
    /**
     * Connect to the V3 channels.
     * @param timeOut Timeout is seconds to wait.
     * @returns (false,true) If (not connected, is connected) to all channels.
     * If not connected to all channels getMessage can be called to find out why.
     * isConnected shows the status of each channel.
     * Connect can not be called again until disconnect is called.
     */
    bool connect(double timeOut);
    /**
     * destroy:
     */
    void destroy();
    /**
     *  Create channelGet.
     *  @returns (false,true) if all channelGets were created.
     */
    bool createGet();
    /**
     * get the current values of the V3 channels.
     * NOTE: get MUST be called by the same thread that calls connect.
     * @returns (false,true) If (all, not all ) gets were successful.
     * If false getMessage can be called to get the reason.
     * If any channel is disconnected then false is returned.
     * Note that the values of each channels data (The array methods
     * below) are updated as a result of the get request and will not
     * change until the next get request is issued.
     */
    bool get();
    /**
     *  Create channelPut.
     *  @returns (false,true) if all channelPut were created.
     */
    bool createPut();
    /**
     * put new values to the V3 channels.
     * NOTE: put MUST be called by the same thread that calls connect.
     * @returns (false,true) If (all, not all ) puts were successful.
     * If false getMessage can be called to get the reason.
     * If any channel is disconnected then false is returned.
     * The data must be put into the NTMultiChannel returned by getNTMultiChannel.
     */
    bool put();
    /**
     * get the reason why a connect or get failed.
     * @returns the message.
     */
    std::string getMessage(){return message;}
    /**
     * The data is saved as an NTMultiChannel with alarm and timeStamp. Get it.
     * @returns the NTMultiChannel.
     */
    epics::nt::NTMultiChannelPtr getNTMultiChannel() {return multiChannel;}
    /**
      * Are all the channels connected>
      * @return (true,false) if (all connected, not all connected)
      */
    bool isAllConnected();
private:
    GatherV3Data(
        epics::nt::NTMultiChannelPtr const &multiChannel,
           size_t numberChannel);
    GatherV3Data::shared_pointer getPtrSelf()
    {
        return shared_from_this();
    }
    void init();
    epics::pvAccess::ChannelProvider::shared_pointer channelProvider;
    epics::nt::NTMultiChannelPtr multiChannel;
    size_t numberChannel;
    epics::pvData::shared_vector<const std::string> channelName;
    epics::pvData::PVStructurePtr pvGetRequest;
    epics::pvData::PVStructurePtr pvPutRequest;
    epics::pvData::Mutex mutex;
    epics::pvData::Event event;
    epics::pvData::PVTimeStamp pvtimeStamp;
    epics::pvData::TimeStamp timeStamp;
    epics::pvData::PVAlarm pvalarm;
    epics::pvData::Alarm alarm;
    std::string message;
    epics::pvData::shared_vector<epics::masar::detail::GatherV3DataChannelPtr> channel;
    epics::pvData::shared_vector<epics::pvData::PVUnionPtr> value;
    epics::pvData::shared_vector<epics::pvData::boolean> isConnected;
    epics::pvData::shared_vector<epics::pvData::int64> secondsPastEpoch;
    epics::pvData::shared_vector<epics::pvData::int32> nanoseconds;
    epics::pvData::shared_vector<epics::pvData::int32> userTag;
    epics::pvData::shared_vector<epics::pvData::int32> alarmSeverity;
    epics::pvData::shared_vector<epics::pvData::int32> alarmStatus;
    epics::pvData::shared_vector<std::string> alarmMessage;
    epics::pvData::shared_vector<epics::pvData::int32> dbrType;
    epics::pvData::shared_vector<epics::pvData::PVStructurePtr>putPVStructure;
    epics::pvData::shared_vector<epics::pvData::BitSetPtr>putBitSet;
    int state;
    size_t numberConnected;
    size_t numberCallback;
    bool requestOK;
    bool getCreated;
    bool atLeastOneGet;
    bool putCreated;
    friend class epics::masar::detail::GatherV3DataChannel;
};

}}

#endif  /* GATHERV3DATA_H */

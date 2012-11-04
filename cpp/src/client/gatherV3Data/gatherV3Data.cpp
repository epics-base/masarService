/* gatherV3Data.cpp */
/*
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Author Marty Kraimer 2011.11 */

#include <stdexcept>
#include <vector>
#include <sstream>

#include <epicsExit.h>
#include <alarm.h>
#include <alarmString.h>

#include <pv/nttable.h>
#include <pv/gatherV3Data.h>

namespace epics { namespace pvAccess {

using namespace epics::pvData;
using std::tr1::static_pointer_cast;

struct GatherV3DataPvt;

enum State {
    idle,
    connecting,
    connected,
    getting,
    putting,
    destroying,
};

enum V3RequestType {
    requestDouble,
    requestLong,
    requestString
};

struct ChannelID
{
    GatherV3DataPvt *pvt;
    chid theChid;
    int offset;
    V3RequestType requestType;
    int elementLength;
    bool getIsConnected;
    dbr_short_t     status;
    dbr_short_t     severity;
    epicsTimeStamp  stamp;         
};

struct GatherV3DataPvt
{
    GatherV3DataPvt(
        bool hasFunction,bool hasTimeStamp, bool hasAlarm,
        StringArray const & valueNames,
        FieldConstPtrArray const &valueFields);
    ~GatherV3DataPvt(){}
    Mutex mutex;
    Event event;
    PVTimeStamp pvtimeStamp;
    TimeStamp timeStamp;
    PVAlarm pvalarm;
    Alarm alarm;
    String message;
    NTTablePtr nttable;
    PVStructurePtr pvStructure;
    int numberChannels;
    std::vector<ChannelID *> apchannelID; // array of  pointer to ChanneID
    PVDoubleArrayPtr pvdoubleValue;
    PVLongArrayPtr pvlongValue;
    PVStringArrayPtr pvstringValue;
    PVStructureArrayPtr pvarrayValue;
    PVLongArrayPtr pvsecondsPastEpoch;
    PVIntArrayPtr pvnanoSeconds;
    PVIntArrayPtr pvtimeStampTag;
    PVIntArrayPtr pvalarmSeverity;
    PVIntArrayPtr pvalarmStatus;
    PVStringArrayPtr pvalarmMessage;
    PVIntArrayPtr pvDBRType;
    PVBooleanArrayPtr pvisArray;
    PVBooleanArrayPtr pvisConnected;
    PVStringArrayPtr pvchannelName;
    State state;
    int numberConnected;
    int numberCallbacks;
    bool requestOK;
    epicsThreadId threadId;
};

GatherV3DataPvt::GatherV3DataPvt(
    bool hasFunction,bool hasTimeStamp, bool hasAlarm,
    StringArray const & valueNames,
    FieldConstPtrArray const &valueFields)
: nttable(NTTable::create(
       hasFunction,hasTimeStamp,hasAlarm,
       valueNames,valueFields))
{
   pvStructure = nttable->getPVStructure();
}

// concatenate a new message onto message
static void messageCat(
    GatherV3DataPvt *pvt,const char *cafunc,int castatus,int channel)
{
    String name = pvt->pvchannelName->get()[channel];
    String buf = String(cafunc);
    buf += " ";
    buf += String(ca_message(castatus));
    buf += " for channel ";
    buf += name;
    pvt->message += buf;
}

static void connectionCallback(struct connection_handler_args args)
{
    chid        chid = args.chid;
    ChannelID *id = static_cast<ChannelID *>(ca_puser(chid));
    GatherV3DataPvt * pvt = id->pvt;
    if(pvt->state==destroying) return;
    int offset = id->offset;

    boolean *data = pvt->pvisConnected->get();
    bool isConnected = data[offset];
    bool newState = ((ca_state(chid)==cs_conn) ? true : false);
    if(isConnected==newState) {
        printf("gatherV3Data connectionCallback."
               " Why extra connection callback?\n");
        return;
    }
    data[offset] = newState;
    Lock xx(pvt->mutex);
    if(newState) {
        int dbrType = ca_field_type(chid);
        unsigned long numberElements = ca_element_count(chid);
        switch(dbrType) {
        case DBF_STRING:
        case DBF_ENUM:
            id->requestType = requestString; break;
        case DBF_CHAR:
        case DBF_SHORT:
        case DBF_LONG:
            id->requestType = requestLong; break;
        case DBF_FLOAT:
        case DBF_DOUBLE:
            id->requestType = requestDouble; break;
        default:
            printf("warning %s has unsupported type %d\n",
                ca_name(chid),dbrType);
            id->requestType = requestString; break;
        }
        int32 *pvalue = pvt->pvDBRType->get();
        pvalue[offset] = dbrType;
        boolean *isArray =  pvt->pvisArray->get();
        if(numberElements==1) {
            isArray[offset] = false;
        } else {
            isArray[offset] = true;
        }
        pvt->numberConnected++;
        if(pvt->state==connecting && pvt->numberConnected==pvt->numberChannels) {
            pvt->event.signal();
        }
        return;
    }
    pvt->numberConnected--;
}

static void getCallback ( struct event_handler_args args )
{
    chid        chid = args.chid;
    ChannelID *id = static_cast<ChannelID *>(ca_puser(chid));
    GatherV3DataPvt * pvt = id->pvt;
    if(pvt->state!=getting) return;
    int offset = id->offset;
    Lock xx(pvt->mutex);
    pvt->numberCallbacks++;
    if ( args.status != ECA_NORMAL ) {
          messageCat(pvt,"getCallback",args.status,offset);
          if(pvt->numberCallbacks==pvt->numberChannels) {
              pvt->event.signal();
          }
          return;
    }
    id->getIsConnected = true;
    unsigned long numberElements = args.count;
    // all DBR_TIME_XXX start with status,severity, timeStamp
    const struct dbr_time_double * pTime =
         ( const struct dbr_time_double * ) args.dbr;
    id->severity = pTime->severity;
    id->status = pTime->status;
    id->stamp = pTime->stamp;
    boolean isArray = pvt->pvisArray->get()[offset];
    if(!isArray) {
        if(id->requestType==requestDouble) {
            const struct dbr_time_double * pTD =
                 ( const struct dbr_time_double * ) args.dbr;
            // set double value
            double * pvalue = pvt->pvdoubleValue->get();
            pvalue[offset] = pTD->value;
    
            // convert double value to string
            String * pstring = pvt->pvstringValue->get();
            char buffer[20];
            sprintf(buffer,"%e",pTD->value);
            pstring[offset] = String(buffer);
    
            // put the integer part to keep at least some information.
            int64 * plvalue = pvt->pvlongValue->get();
            plvalue[offset] = pTD->value;
        } else if(id->requestType==requestLong) {
            const struct dbr_time_long * pTL =
                 ( const struct dbr_time_long * ) args.dbr;
            // set long value as 64-bit
            int64 * pvalue = pvt->pvlongValue->get();
            pvalue[offset] = pTL->value;
    
            // put 64-bit long to a double array
            pvt->pvdoubleValue->get()[offset] = pTL->value;
    
            // convert long value to a string
            char buffer[20];
            sprintf(buffer,"%d",pTL->value);
            pvt->pvstringValue->get()[offset] = String(buffer);
        } else if(id->requestType==requestString) {
            const struct dbr_time_string * pTS =
                 ( const struct dbr_time_string * ) args.dbr;
            // set to string array only
            pvt->pvstringValue->get()[offset] = String(pTS->value);
        } else {
            throw std::logic_error("unknown DBR_TYPE");
        }
    } else {
        PVStructurePtr pvStructure = pvt->pvarrayValue->get()[offset];
        PVFieldPtrArray pvfields = pvStructure->getPVFields();
        PVStringArrayPtr pvstringarray = static_pointer_cast<PVStringArray>(pvfields[0]);
        PVDoubleArrayPtr pvdoublearray = static_pointer_cast<PVDoubleArray>(pvfields[1]);
        PVIntArrayPtr pvintarray = static_pointer_cast<PVIntArray>(pvfields[2]);
        if(id->requestType==requestDouble) {
            const struct dbr_time_double * pTD =
                 ( const struct dbr_time_double * ) args.dbr;
            // set double value
            pvdoublearray->setLength(numberElements);
            double * pvalue = pvdoublearray->get();
            memcpy(pvalue,&pTD->value,numberElements*sizeof(double));
        } else if(id->requestType==requestLong) {
            const struct dbr_time_long * pTL =
                 ( const struct dbr_time_long * ) args.dbr;
            // set long value as 32-bit
            pvintarray->setLength(numberElements);
            int32 * pvalue = pvintarray->get();
            memcpy(pvalue,&pTL->value,numberElements*sizeof(int32));
        } else if(id->requestType==requestString) {
            const struct dbr_time_string * pTS =
                 ( const struct dbr_time_string * ) args.dbr;
            // set to string array only
            pvstringarray->setLength(numberElements);
            String * pvalue = pvstringarray->get();
            const char *pfrom = pTS->value;
            for(unsigned long i=0; i<numberElements; i++) {
                pvalue[i] = String(pfrom);
                pfrom += MAX_STRING_SIZE;
            }
        } else {
            throw std::logic_error("unknown DBR_TYPE");
        }
    }

    if(pvt->numberCallbacks==pvt->numberConnected) {
        pvt->event.signal();
    }
}

static void putCallback ( struct event_handler_args args )
{
    chid        chid = args.chid;
    ChannelID *id = static_cast<ChannelID *>(ca_puser(chid));
    GatherV3DataPvt * pvt = id->pvt;
    if(pvt->state!=putting) return;
    int offset = id->offset;
    Lock xx(pvt->mutex);
    pvt->numberCallbacks++;
    if ( args.status != ECA_NORMAL ) {
          messageCat(pvt,"putCallback",args.status,offset);
          if(pvt->numberCallbacks==pvt->numberChannels) {
              pvt->event.signal();
          }
          return;
    }
    if(pvt->numberCallbacks==pvt->numberChannels) {
        pvt->event.signal();
    }
}

GatherV3Data::GatherV3Data(
    StringArray const & channelNames,
    int numberChannels)
: pvt(0)
{
    FieldCreatePtr fieldCreate = getFieldCreate();
    size_t naf = 3;
    StringArray names;
    names.reserve(naf);
    FieldConstPtrArray arrfields;
    arrfields.reserve(naf);
    names.push_back("stringValue");
    names.push_back("doubleValue");
    names.push_back("intValue");
    arrfields.push_back(fieldCreate->createScalarArray(pvString));
    arrfields.push_back(fieldCreate->createScalarArray(pvDouble));
    arrfields.push_back(fieldCreate->createScalarArray(pvInt));
    StructureConstPtr arrStructure = fieldCreate->createStructure(
         names,arrfields);
    int n = 14;
    StringArray fieldNames;
    fieldNames.reserve(n);
    FieldConstPtrArray fields;
    fields.reserve(n);
    // The order is mapped into SQL query sequence to keep data format consistency.
    // Update RDB query each time when fields order is changed.
    // fields order & type
    // 'pv name', 'string value', 'double value', 'long value',
    // string,     string,         double,         long,      ,
    // 'array value',     'isArray', 'dbr type', 'isConnected',
    // structureArray,     boolean,   int,        boolean,
    // 'secondsPastEpoch', 'nanoSeconds', 'timeStampTag',
    // long,                int,           int,          
    // 'alarmSeverity', 'alarmStatus', 'alarmMessage'
    //  int,             int,           string
    fieldNames.push_back("channelName");
    fieldNames.push_back("stringValue");
    fieldNames.push_back("doubleValue");
    fieldNames.push_back("longValue");
    fieldNames.push_back("dbrType");
    fieldNames.push_back("isConnected");
    fieldNames.push_back("secondsPastEpoch");
    fieldNames.push_back("nanoSeconds");
    fieldNames.push_back("timeStampTag");
    fieldNames.push_back("alarmSeverity");
    fieldNames.push_back("alarmStatus");
    fieldNames.push_back("alarmMessage");
    fieldNames.push_back("isArray");
    fieldNames.push_back("arrayValue");
    fields.push_back(fieldCreate->createScalarArray(pvString));
    fields.push_back(fieldCreate->createScalarArray(pvString));
    fields.push_back(fieldCreate->createScalarArray(pvDouble));
    fields.push_back(fieldCreate->createScalarArray(pvLong));
    fields.push_back(fieldCreate->createScalarArray(pvInt));
    fields.push_back(fieldCreate->createScalarArray(pvBoolean));
    fields.push_back(fieldCreate->createScalarArray(pvLong));
    fields.push_back(fieldCreate->createScalarArray(pvInt));
    fields.push_back(fieldCreate->createScalarArray(pvInt));
    fields.push_back(fieldCreate->createScalarArray(pvInt));
    fields.push_back(fieldCreate->createScalarArray(pvInt));
    fields.push_back(fieldCreate->createScalarArray(pvString));
    fields.push_back(fieldCreate->createScalarArray(pvBoolean));
    fields.push_back(fieldCreate->createStructureArray(arrStructure));
    

    pvt = new GatherV3DataPvt(false,true,true,fieldNames,fields);
    pvt->nttable->attachTimeStamp(pvt->pvtimeStamp);
    pvt->nttable->attachAlarm(pvt->pvalarm);
    pvt->pvtimeStamp.attach(pvt->pvStructure->getSubField("timeStamp"));
    pvt->pvalarm.attach(pvt->pvStructure->getSubField("alarm"));
    pvt->numberChannels = numberChannels;
//    ChannelID **apchannelID = new ChannelID*[numberChannels];
    pvt->apchannelID.resize(numberChannels);
    for(int i=0; i<numberChannels; i++) {
        ChannelID *pChannelID = new ChannelID();
        pChannelID->pvt = pvt;
        pChannelID->theChid = 0;
        pChannelID->offset = i;
        pChannelID->requestType = requestString;
        pChannelID->elementLength = 1;
        pChannelID->getIsConnected = false;
        pChannelID->status = epicsAlarmUDF;
        pChannelID->severity = epicsSevInvalid;
        pChannelID->stamp.secPastEpoch = 0;
        pChannelID->stamp.nsec = 0;
        pvt->apchannelID[i] = pChannelID;
    }

    pvt->pvchannelName = static_pointer_cast<PVStringArray>(
        pvt->nttable->getPVField(0));
    pvt->pvchannelName->setCapacity(numberChannels);
    pvt->pvchannelName->setCapacityMutable(false);
    pvt->pvchannelName->put(0,numberChannels,channelNames,0);

    pvt->pvstringValue = static_pointer_cast<PVStringArray>(
        pvt->nttable->getPVField(1));
    pvt->pvstringValue->setCapacity(numberChannels);
    pvt->pvstringValue->setCapacityMutable(false);
    pvt->pvstringValue->setLength(numberChannels);
    String *pstrings = pvt->pvstringValue->get();
    for (int i=0; i<numberChannels; i++) {
         pstrings[i] = String("0.0");
    }

    pvt->pvdoubleValue = static_pointer_cast<PVDoubleArray>(
        pvt->nttable->getPVField(2));
    pvt->pvdoubleValue->setCapacity(numberChannels);
    pvt->pvdoubleValue->setCapacityMutable(false);
    pvt->pvdoubleValue->setLength(numberChannels);
    double *pdouble = pvt->pvdoubleValue->get();
    for (int i=0; i<numberChannels; i++) pdouble[i] = 0.0;

    pvt->pvlongValue = static_pointer_cast<PVLongArray>(
        pvt->nttable->getPVField(3));
    pvt->pvlongValue->setCapacity(numberChannels);
    pvt->pvlongValue->setCapacityMutable(false);
    pvt->pvlongValue->setLength(numberChannels);
    int64 * plong = pvt->pvlongValue->get();
    for (int i=0; i<numberChannels; i++) plong[i] = 0.0;

    pvt->pvDBRType = static_pointer_cast<PVIntArray>(
        pvt->nttable->getPVField(4));
    pvt->pvDBRType->setCapacity(numberChannels);
    pvt->pvDBRType->setCapacityMutable(false);
    pvt->pvDBRType->setLength(numberChannels);
    int32 *pDBRType = pvt->pvDBRType->get();
    for (int i=0; i<numberChannels; i++) pDBRType[i] = DBF_NO_ACCESS;

    pvt->pvisConnected = static_pointer_cast<PVBooleanArray>(
        pvt->nttable->getPVField(5));
    pvt->pvisConnected->setCapacity(numberChannels);
    pvt->pvisConnected->setCapacityMutable(false);
    pvt->pvisConnected->setLength(numberChannels);
    boolean *pbool = pvt->pvisConnected->get();
    for (int i=0; i<numberChannels; i++) pbool[i] = false;

    pvt->pvsecondsPastEpoch = static_pointer_cast<PVLongArray>(
        pvt->nttable->getPVField(6));
    pvt->pvsecondsPastEpoch->setCapacity(numberChannels);
    pvt->pvsecondsPastEpoch->setCapacityMutable(false);
    pvt->pvsecondsPastEpoch->setLength(numberChannels);
    int64 * psecondsPastEpoch = pvt->pvsecondsPastEpoch->get();
    for (int i=0; i<numberChannels; i++) psecondsPastEpoch[i] = 0;

    pvt->pvnanoSeconds = static_pointer_cast<PVIntArray>(
        pvt->nttable->getPVField(7));
    pvt->pvnanoSeconds->setCapacity(numberChannels);
    pvt->pvnanoSeconds->setCapacityMutable(false);
    pvt->pvnanoSeconds->setLength(numberChannels);
    int32* pnanoSeconds = pvt->pvnanoSeconds->get();
    for (int i=0; i<numberChannels; i++) pnanoSeconds[i] = 0;

    pvt->pvtimeStampTag = static_pointer_cast<PVIntArray>(
        pvt->nttable->getPVField(8));
    pvt->pvtimeStampTag->setCapacity(numberChannels);
    pvt->pvtimeStampTag->setCapacityMutable(false);
    pvt->pvtimeStampTag->setLength(numberChannels);
    int32 *ptimeStampTag = pvt->pvtimeStampTag->get();
    for (int i=0; i<numberChannels; i++) ptimeStampTag[i] = 0;

    pvt->pvalarmSeverity = static_pointer_cast<PVIntArray>(
        pvt->nttable->getPVField(9));
    pvt->pvalarmSeverity->setCapacity(numberChannels);
    pvt->pvalarmSeverity->setCapacityMutable(false);
    pvt->pvalarmSeverity->setLength(numberChannels);
    int32 *palarmSeverity = pvt->pvalarmSeverity->get();
    for (int i=0; i<numberChannels; i++) palarmSeverity[i] = INVALID_ALARM;

    pvt->pvalarmStatus = static_pointer_cast<PVIntArray>(
        pvt->nttable->getPVField(10));
    pvt->pvalarmStatus->setCapacity(numberChannels);
    pvt->pvalarmStatus->setCapacityMutable(false);
    pvt->pvalarmStatus->setLength(numberChannels);
    int32 * palarmStatus = pvt->pvalarmStatus->get();
    for (int i=0; i<numberChannels; i++) palarmStatus[i] = epicsAlarmComm;

    pvt->pvalarmMessage = static_pointer_cast<PVStringArray>(
        pvt->nttable->getPVField(11));
    pvt->pvalarmMessage->setCapacity(numberChannels);
    pvt->pvalarmMessage->setCapacityMutable(false);
    pvt->pvalarmMessage->setLength(numberChannels);
    String * palarmMessage = pvt->pvalarmMessage->get();
    for (int i=0; i<numberChannels; i++) palarmMessage[i] = String();

    pvt->pvisArray = static_pointer_cast<PVBooleanArray>(
        pvt->nttable->getPVField(12));
    pvt->pvisArray->setCapacity(numberChannels);
    pvt->pvisArray->setCapacityMutable(false);
    pvt->pvisArray->setLength(numberChannels);
    pbool = pvt->pvisArray->get();
    for (int i=0; i<numberChannels; i++) pbool[i] = false;

    pvt->pvarrayValue = static_pointer_cast<PVStructureArray>(
        pvt->nttable->getPVField(13));
    pvt->pvarrayValue->setCapacity(numberChannels);
    pvt->pvarrayValue->setCapacityMutable(false);
    pvt->pvarrayValue->setLength(numberChannels);
    PVStructurePtr *ppPVStructure = pvt->pvarrayValue->get();
    StructureConstPtr pstructure
        = pvt->pvarrayValue->getStructureArray()->getStructure();
    PVDataCreatePtr pvDataCreate = getPVDataCreate();
    for (int i=0; i<numberChannels; i++) {
        ppPVStructure[i] = pvDataCreate->createPVStructure(pstructure);
    }

    pvt->state = idle;
    pvt->numberConnected = 0;
    pvt->numberCallbacks = 0;
    pvt->requestOK = false;
    pvt->threadId = 0;
}

GatherV3Data::~GatherV3Data()
{
    if(pvt->state!=idle) disconnect();
    for(int i=0; i<pvt->numberChannels; i++) {
        ChannelID *pChannelID = pvt->apchannelID[i];
        delete pChannelID;
    }
    delete pvt;
}

bool GatherV3Data::connect(double timeOut)
{
    if(pvt->state!=idle) {
        throw std::logic_error(
            "GatherV3Data::connect only legal when state is idle\n");
    }
    SEVCHK(ca_context_create(ca_enable_preemptive_callback),"ca_context_create");
    pvt->threadId = epicsThreadGetIdSelf();
    pvt->state = connecting;
    pvt->numberConnected = 0;
    pvt->numberCallbacks = 0;
    pvt->requestOK = true;
    pvt->event.tryWait();
    int numberChannels = pvt->numberChannels;
    boolean* isConnected = pvt->pvisConnected->get();
    String *channelNames = pvt->pvchannelName->get();
    for(int i=0; i< numberChannels; i++) {
        isConnected[i] = false;
        const char * channelName = channelNames[i].c_str();
        ChannelID *pchannelID = pvt->apchannelID[i];
        int result = ca_create_channel(
           channelName,
           connectionCallback,
           pchannelID,
           20,
           &pchannelID->theChid);
        if(result!=ECA_NORMAL) {
            printf("%s ca_create_channel failed %s\n",
               channelName,ca_message(result));
        }
    }
    ca_flush_io();
    std::stringstream ss;
    while(true) {
        int oldNumber = pvt->numberConnected;
        bool result = pvt->event.wait(timeOut);
        if(result && pvt->requestOK) {
            pvt->state = connected;
            return pvt->requestOK;
        }
        if(pvt->numberConnected!=pvt->numberChannels) {
            ss.str("");
            ss << (pvt->numberChannels - pvt->numberConnected);
            String buf = ss.str();
            buf += " channels of ";
            ss.str("");
            ss << pvt->numberChannels;
            buf += ss.str();
            buf += " are not connected.";
            pvt->message = buf;
            pvt->alarm.setMessage(pvt->message);
            pvt->alarm.setSeverity(invalidAlarm);
            pvt->alarm.setStatus(clientStatus);
        }
        if(oldNumber==pvt->numberConnected) {
            pvt->state = connected;
            return false;
        }
        timeOut = 1.0;
    }
    return false;
}

void GatherV3Data::disconnect()
{
    Lock xx(pvt->mutex);
    if(pvt->state==idle) return;
    if(pvt->threadId!=epicsThreadGetIdSelf()) {
        throw std::logic_error(
            "GatherV3Data::disconnect must be same thread that called connect\n");
    }
    int numberChannels = pvt->numberChannels;
    pvt->state = destroying;
    for(int i=0; i< numberChannels; i++) {
        chid theChid = pvt->apchannelID[i]->theChid;
        ca_clear_channel(theChid);
    }
    ca_context_destroy();
    pvt->state = idle;
}

bool GatherV3Data::get()
{
    if(pvt->state!=connected) {
        throw std::logic_error("GatherV3Data::get illegal state\n");
    }
    if(pvt->threadId!=epicsThreadGetIdSelf()) {
        throw std::logic_error(
            "GatherV3Data::get must be same thread that called connect\n");
    }
    pvt->state = getting;
    pvt->numberCallbacks = 0;
    pvt->requestOK = true;
    pvt->message = String();
    pvt->event.tryWait();
    pvt->timeStamp.getCurrent();
    pvt->alarm.setMessage("");
    pvt->alarm.setSeverity(noAlarm);
    pvt->alarm.setStatus(noStatus);
    for(int i=0; i< pvt->numberChannels; i++) {
        ChannelID *channelId = pvt->apchannelID[i];
        chid theChid = channelId->theChid;
        V3RequestType requestType = channelId->requestType;
        int req = DBR_TIME_DOUBLE;
        if(requestType==requestLong) req = DBR_TIME_LONG;
        if(requestType==requestString) req = DBR_TIME_STRING;
        int result = ca_array_get_callback(
            req,
            0,
            theChid,
            getCallback,
            pvt->apchannelID[i]);
        if(result==ECA_NORMAL) continue;
        if(result==ECA_DISCONN) {
            messageCat(pvt,"ca_get_callback",ECA_DISCONN,i);
            channelId->getIsConnected = false;
            pvt->requestOK = false;
            continue;
        }
        if(result!=ECA_NORMAL) {
            messageCat(pvt,"ca_get_callback",result,i);
            pvt->requestOK = false;
        }
    }
    ca_flush_io();
    bool result = false;
    while(true) {
        int oldNumber = pvt->numberCallbacks;
        result = pvt->event.wait(1.0);
        if(result) break;
        if(pvt->numberCallbacks==oldNumber) break;
    }
    if(!result) {
        pvt->message += " timeout";
        pvt->requestOK = false;
        pvt->alarm.setMessage(pvt->message);
        pvt->alarm.setSeverity(invalidAlarm);
        pvt->alarm.setStatus(clientStatus);
    }
    int numberChannels = pvt->numberChannels;
    boolean * isConnected = pvt->pvisConnected->get();
    int64 * secondsPastEpoch = pvt->pvsecondsPastEpoch->get();
    int32 * nanoSeconds = pvt->pvnanoSeconds->get();
    int32 * alarmSeverity = pvt->pvalarmSeverity->get();
    int32 * alarmStatus = pvt->pvalarmStatus->get();
    String * alarmMessage = pvt->pvalarmMessage->get();
    for(int i=0; i<numberChannels; i++) {
        ChannelID *pID = pvt->apchannelID[i];
        isConnected[i] = pID->getIsConnected;
        // pID->stamp.secPastEpoch should be 0 if record is not processed yet.
        // otherwise, use EPOCH time.
        if (pID->stamp.secPastEpoch > posixEpochAtEpicsEpoch)
            secondsPastEpoch[i] =
                pID->stamp.secPastEpoch + posixEpochAtEpicsEpoch;
        nanoSeconds[i] = pID->stamp.nsec;
        alarmSeverity[i] = pID->severity;
        alarmStatus[i] = pID->status;
        alarmMessage[i] = String(epicsAlarmConditionStrings[pID->status]);
        if(pvt->alarm.getSeverity()<pID->severity) {
            pvt->alarm.setSeverity(static_cast<AlarmSeverity>(alarmSeverity[i]));
            pvt->alarm.setStatus(static_cast<AlarmStatus>(alarmStatus[i]));
            pvt->alarm.setMessage(alarmMessage[i]);
        }
    }
    pvt->state = connected;
    return pvt->requestOK;
}

bool GatherV3Data::put()
{
    if(pvt->state!=connected) {
        throw std::logic_error("GatherV3Data::put illegal state\n");
    }
    if(pvt->threadId!=epicsThreadGetIdSelf()) {
        throw std::logic_error(
            "GatherV3Data::put must be same thread that called connect\n");
    }
    pvt->state = putting;
    pvt->numberCallbacks = 0;
    pvt->requestOK = true;
    pvt->message = String();
    pvt->event.tryWait();
    pvt->timeStamp.getCurrent();
    pvt->alarm.setMessage("");
    pvt->alarm.setSeverity(noAlarm);
    pvt->alarm.setStatus(noStatus);
    int64 * plvalue = pvt->pvlongValue->get();
    double * pdvalue = pvt->pvdoubleValue->get();
    String * psvalue = pvt->pvstringValue->get();
    PVStructurePtr * parrayvalue = pvt->pvarrayValue->get();
    boolean * isArray = pvt->pvisArray->get();
    for(int i=0; i< pvt->numberChannels; i++) {
        ChannelID *channelId = pvt->apchannelID[i];
        chid theChid = channelId->theChid;
        V3RequestType requestType = channelId->requestType;
        unsigned long count = 1;
        unsigned long sizebuf = 0;
        char *buffer = 0;
        const void *pdata = 0;
        int req = 0;
        if(isArray[i]) {
            switch(requestType) {
                case requestLong: {
                    req = DBR_LONG;
                    PVIntArrayPtr pvvalue = static_pointer_cast<PVIntArray>(
                         parrayvalue[i]->getScalarArrayField("intValue",pvInt));
                    count = pvvalue->getLength();
                    pdata = pvvalue->get();
                }
                break;
                case requestDouble: {
                    req = DBR_DOUBLE;
                    PVDoubleArrayPtr pvvalue = static_pointer_cast<PVDoubleArray>(
                         parrayvalue[i]->getScalarArrayField("doubleValue",pvDouble));
                    count = pvvalue->getLength();
                    pdata = pvvalue->get();
                }
                break;
                case requestString: {
                    req = DBR_STRING;
                    PVStringArrayPtr pvvalue = static_pointer_cast<PVStringArray>(
                         parrayvalue[i]->getScalarArrayField("stringValue",pvString));
                    int length = pvvalue->getLength();
                    String * values = pvvalue->get();
                    sizebuf = length*MAX_STRING_SIZE;
                    count = length;
                    buffer = new char[sizebuf];
                    memset(buffer,0,sizebuf);
                    pdata = buffer;
                    char *p = buffer;
                    for(int j=0; j< length; j++) {
                        String value = values[j];
                        const char *pfrom = value.c_str();
                        int num = value.length();
                        if(num>=MAX_STRING_SIZE) num = MAX_STRING_SIZE-1;
                        memcpy(p,pfrom,num);
                        p += MAX_STRING_SIZE;
                    }
                }
                break;
            default:
                 printf(
                     "%s warning gatherV3Data::put has unsupported type %d\n",
                     ca_name(theChid),requestType);
                    
            }
        } else {
            switch(requestType) {
            case requestLong:
                req = DBR_LONG; pdata = &plvalue[i]; break;
            case requestDouble:
                req = DBR_DOUBLE; pdata = &pdvalue[i]; break;
            case requestString:
                req = DBR_STRING; pdata = psvalue[i].c_str(); break;
            }
        }
        int result = ca_array_put_callback(
            req,
            count,
            theChid,
            pdata,
            putCallback,
            pvt->apchannelID[i]);
        if(result!=ECA_NORMAL) {
            messageCat(pvt,"ca_put_callback",result,i);
            pvt->requestOK = false;
        }
        if(sizebuf>0) delete[] buffer;
    }
    ca_flush_io();
    bool result = false;
    while(true) {
        int oldNumber = pvt->numberCallbacks;
        result = pvt->event.wait(1.0);
        if(result) break;
        if(pvt->numberCallbacks==oldNumber) break;
    }
    if(!result) {
        pvt->message += " timeout";
        pvt->requestOK = false;
        pvt->alarm.setMessage(pvt->message);
        pvt->alarm.setSeverity(invalidAlarm);
        pvt->alarm.setStatus(clientStatus);
    }
    pvt->state = connected;
    return pvt->requestOK;
}

String GatherV3Data::getMessage()
{
    return pvt->message;
}

PVStructurePtr GatherV3Data::getNTTableStructure()
{
    return pvt->pvStructure;
}

NTTablePtr  GatherV3Data::getNTTable(){
    return pvt->nttable;
}

PVDoubleArrayPtr GatherV3Data::getDoubleValue()
{
    return pvt->pvdoubleValue;
}

PVLongArrayPtr GatherV3Data::getLongValue()
{
    return pvt->pvlongValue;
}

PVStringArrayPtr GatherV3Data::getStringValue()
{
    return pvt->pvstringValue;
}

PVStructureArrayPtr GatherV3Data::getArrayValue()
{
    return pvt->pvarrayValue;
}

PVLongArrayPtr GatherV3Data::getSecondsPastEpoch()
{
    return pvt->pvsecondsPastEpoch;
}

PVIntArrayPtr GatherV3Data::getNanoSeconds()
{
    return pvt->pvnanoSeconds;
}

PVIntArrayPtr GatherV3Data::getTimeStampTag()
{
    return pvt->pvtimeStampTag;
}

PVIntArrayPtr GatherV3Data::getAlarmSeverity()
{
    return pvt->pvalarmSeverity;
}

PVIntArrayPtr GatherV3Data::getAlarmStatus()
{
    return pvt->pvalarmStatus;
}

PVStringArrayPtr GatherV3Data::getAlarmMessage()
{
    return pvt->pvalarmMessage;
}

PVIntArrayPtr GatherV3Data::getDBRType()
{
    return pvt->pvDBRType;
}

PVBooleanArrayPtr GatherV3Data::getIsArray()
{
    return pvt->pvisArray;
}

PVBooleanArrayPtr GatherV3Data::getIsConnected()
{
    return pvt->pvisConnected;
}

PVStringArrayPtr GatherV3Data::getChannelName()
{
    return pvt->pvchannelName;
}
int GatherV3Data::getConnectedChannels()
{
    return pvt->numberConnected;
}
}}

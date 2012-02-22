/* gatherV3ScalarData.cpp */
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

#include <pv/gatherV3ScalarData.h>

namespace epics { namespace pvAccess {

using namespace epics::pvData;

struct GatherV3ScalarDataPvt;

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
    requestString,
    requestCharArray
};

struct ChannelID
{
    GatherV3ScalarDataPvt *pvt;
    chid theChid;
    int offset;
    V3RequestType requestType;
    int elementLength;
    bool getIsConnected;
    dbr_short_t     status;
    dbr_short_t     severity;
    epicsTimeStamp  stamp;         
};

struct GatherV3ScalarDataPvt
{
    GatherV3ScalarDataPvt(
          PVStructure::shared_pointer const & pvStructure)
    : pvStructure(pvStructure),
      nttable(NTTable(pvStructure))
    {}
    ~GatherV3ScalarDataPvt(){}
    Mutex mutex;
    Event event;
    PVTimeStamp pvtimeStamp;
    TimeStamp timeStamp;
    PVAlarm pvalarm;
    Alarm alarm;
    String message;
    PVStructure::shared_pointer pvStructure;
    NTTable nttable;
    int numberChannels;
//    ChannelID **apchannelID; // array of  pointer to ChanneID
    std::vector<ChannelID *> apchannelID; // array of  pointer to ChanneID
    PVDoubleArray *pvdoubleValue;
    PVLongArray *pvlongValue;
    PVStringArray *pvstringValue;
    PVStructureArray *pvarrayValue;
    PVLongArray *pvsecondsPastEpoch;
    PVIntArray *pvnanoSeconds;
    PVIntArray *pvtimeStampTag;
    PVIntArray *pvalarmSeverity;
    PVIntArray *pvalarmStatus;
    PVStringArray *pvalarmMessage;
    PVIntArray *pvDBRType;
    PVBooleanArray *pvisArray;
    PVBooleanArray *pvisConnected;
    PVStringArray *pvchannelName;
    State state;
    int numberConnected;
    int numberCallbacks;
    bool requestOK;
    epicsThreadId threadId;
};

// concatenate a new message onto message
static void messageCat(
    GatherV3ScalarDataPvt *pvt,const char *cafunc,int castatus,int channel)
{
    StringArrayData data;
    pvt->pvchannelName->get(0,pvt->numberChannels,&data);
    String name = data.data[channel];
    //int len = name.length();
    //char buf[len+30];
    //following prevents compiler warning message
    //sprintf(buf,"%s %s for channel %s\n",
    //    cafunc,
    //    ca_message(castatus),
    //    name.c_str());
    // pvt->message += String(buf);
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
    GatherV3ScalarDataPvt * pvt = id->pvt;
    if(pvt->state==destroying) return;
    int offset = id->offset;

    BooleanArrayData data;
    pvt->pvisConnected->get(0,pvt->numberChannels,&data);
    bool isConnected = data.data[offset];
    bool newState = ((ca_state(chid)==cs_conn) ? true : false);
    if(isConnected==newState) {
        printf("gatherV3ScalarData connectionCallback."
               " Why extra connection callback?\n");
        return;
    }
    Lock xx(pvt->mutex);
    if(newState) {
        int dbrType = ca_field_type(chid);
        unsigned long numberElements = ca_element_count(chid);
        switch(dbrType) {
        case DBF_STRING:
        case DBF_ENUM:
            id->requestType = requestString; break;
        case DBF_CHAR:
            if(numberElements>1) {
                id->requestType = requestCharArray; break;
            }
            // just fall through
        case DBF_INT:
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
        IntArrayData data;
        pvt->pvDBRType->get(0,pvt->numberChannels,&data);
        int32 * pvalue = data.data;
        pvalue[offset] = dbrType;
        BooleanArrayData booldata;
        pvt->pvisArray->get(0,pvt->numberChannels,&booldata);
        bool *isArray = booldata.data;
        if(id->requestType==requestCharArray) {
            isArray[offset] = false;
        } else if(numberElements==1) {
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
    GatherV3ScalarDataPvt * pvt = id->pvt;
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
    DoubleArrayData doubledata;
    StringArrayData stringdata;
    LongArrayData longdata;
    IntArrayData intdata;
    BooleanArrayData booldata;
    StructureArrayData structdata;
    pvt->pvisArray->get(0,pvt->numberChannels,&booldata);
    bool isArray = booldata.data[offset];
    if(!isArray) {
        if(id->requestType==requestDouble) {
            const struct dbr_time_double * pTD =
                 ( const struct dbr_time_double * ) args.dbr;
            // set double value
            pvt->pvdoubleValue->get(0,pvt->numberChannels,&doubledata);
            double * pvalue = doubledata.data;
            pvalue[offset] = pTD->value;
    
            // convert double value to string
            pvt->pvstringValue->get(0,pvt->numberChannels,&stringdata);
            char buffer[20];
            sprintf(buffer,"%e",pTD->value);
            stringdata.data[offset] = String(buffer);
    
            // put the integer part to keep at least some information.
            pvt->pvlongValue->get(0,pvt->numberChannels,&longdata);
            int64 * plvalue = longdata.data;
            plvalue[offset] = pTD->value;
        } else if(id->requestType==requestLong) {
            const struct dbr_time_long * pTL =
                 ( const struct dbr_time_long * ) args.dbr;
            // set long value as 64-bit
            pvt->pvlongValue->get(0,pvt->numberChannels,&longdata);
            int64 * pvalue = longdata.data;
            pvalue[offset] = pTL->value;
    
            // put 64-bit long to a double array
            pvt->pvdoubleValue->get(0,pvt->numberChannels,&doubledata);
            doubledata.data[offset] = pTL->value;
    
            // convert long value to a string
            pvt->pvstringValue->get(0,pvt->numberChannels,&stringdata);
            char buffer[20];
            sprintf(buffer,"%d",pTL->value);
            stringdata.data[offset] = String(buffer);
        } else if(id->requestType==requestString) {
            const struct dbr_time_string * pTS =
                 ( const struct dbr_time_string * ) args.dbr;
            // set to string array only
            pvt->pvstringValue->get(0,pvt->numberChannels,&stringdata);
            String * pvalue = stringdata.data;
            pvalue[offset] = String(pTS->value);
        } else if(id->requestType==requestCharArray) {
            const struct dbr_time_char * pTS =
                 ( const struct dbr_time_char *) args.dbr;
            // set to string array only
            pvt->pvstringValue->get(0,pvt->numberChannels,&stringdata);
            String * pvalue = stringdata.data;
            const char *value = (const char *)(&pTS->value);
            pvalue[offset] = String(value);
        } else {
            throw std::logic_error("unknown DBR_TYPE");
        }
    } else {
        pvt->pvarrayValue->get(0,pvt->numberChannels,&structdata);
        PVStructure * pvStructure = structdata.data[offset];
        PVFieldPtrArray pvfields = pvStructure->getPVFields();
        PVStringArray *pvstringarray = static_cast<PVStringArray *>(pvfields[0]);
        PVDoubleArray *pvdoublearray = static_cast<PVDoubleArray *>(pvfields[1]);
        PVIntArray *pvintarray = static_cast<PVIntArray *>(pvfields[2]);
        if(id->requestType==requestDouble) {
            const struct dbr_time_double * pTD =
                 ( const struct dbr_time_double * ) args.dbr;
            // set double value
            pvdoublearray->setLength(numberElements);
            pvdoublearray->get(0,numberElements,&doubledata);
            double * pvalue = doubledata.data;
            memcpy(pvalue,&pTD->value,numberElements*sizeof(double));
        } else if(id->requestType==requestLong) {
            const struct dbr_time_long * pTL =
                 ( const struct dbr_time_long * ) args.dbr;
            // set long value as 32-bit
            pvintarray->setLength(numberElements);
            pvintarray->get(0,numberElements,&intdata);
            int32 * pvalue = intdata.data;
            memcpy(pvalue,&pTL->value,numberElements*sizeof(int32));
        } else if(id->requestType==requestString) {
            const struct dbr_time_string * pTS =
                 ( const struct dbr_time_string * ) args.dbr;
            // set to string array only
            pvstringarray->setLength(numberElements);
            pvstringarray->get(0,numberElements,&stringdata);
            String * pvalue = stringdata.data;
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
    GatherV3ScalarDataPvt * pvt = id->pvt;
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

GatherV3ScalarData::GatherV3ScalarData(
    String channelNames[],
    int numberChannels)
: pvt(0)
{
    IntArrayData intdata;
    StringArrayData strdata;
    LongArrayData longdata;
    DoubleArrayData doubledata;
    BooleanArrayData booldata;
    StructureArrayData structdata;

    FieldCreate *fieldCreate = getFieldCreate();
    int naf = 3;
    FieldConstPtrArray arrfields = new FieldConstPtr[naf];
    arrfields[0] = fieldCreate->createScalarArray("stringValue",pvString);
    arrfields[1] = fieldCreate->createScalarArray("doubleValue",pvDouble);
    arrfields[2] = fieldCreate->createScalarArray("intValue",pvInt);
    StructureConstPtr arrStructure = fieldCreate->createStructure(
         "arrayValue",naf,arrfields);
    
    int n = 14;
    FieldConstPtr fields[n];

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
    fields[0] = fieldCreate->createScalarArray("channelName",pvString);
    fields[1] = fieldCreate->createScalarArray("stringValue",pvString);
    fields[2] = fieldCreate->createScalarArray("doubleValue",pvDouble);
    fields[3] = fieldCreate->createScalarArray("longValue",pvLong);
    fields[4] = fieldCreate->createStructureArray("arrayValue",arrStructure);
    fields[5] = fieldCreate->createScalarArray("isArray",pvBoolean);
    fields[6] = fieldCreate->createScalarArray("dbrType",pvInt);
    fields[7] = fieldCreate->createScalarArray("isConnected",pvBoolean);
    fields[8] = fieldCreate->createScalarArray("secondsPastEpoch",pvLong);
    fields[9] = fieldCreate->createScalarArray("nanoSeconds",pvInt);
    fields[10] = fieldCreate->createScalarArray("timeStampTag",pvInt);
    fields[11] = fieldCreate->createScalarArray("alarmSeverity",pvInt);
    fields[12] = fieldCreate->createScalarArray("alarmStatus",pvInt);
    fields[13] = fieldCreate->createScalarArray("alarmMessage",pvString);

    PVStructure::shared_pointer pvStructure = NTTable::create(
        false,true,true,n,fields);
    pvt = new GatherV3ScalarDataPvt(pvStructure);
    pvt->nttable.attachTimeStamp(pvt->pvtimeStamp);
    pvt->nttable.attachAlarm(pvt->pvalarm);
    pvt->pvtimeStamp.attach(pvStructure->getSubField("timeStamp"));
    pvt->pvalarm.attach(pvStructure->getSubField("alarm"));
    pvt->numberChannels = numberChannels;
//    ChannelID **apchannelID = new ChannelID*[numberChannels];
    std::vector<ChannelID *> apchannelID(numberChannels);
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
        apchannelID[i] = pChannelID;
    }
    pvt->apchannelID = apchannelID;
    pvt->pvchannelName = static_cast<PVStringArray *>(pvt->nttable.getPVField(0));
    pvt->pvchannelName->setCapacity(numberChannels);
    pvt->pvchannelName->setCapacityMutable(false);
    pvt->pvchannelName->put(0,numberChannels,channelNames,0);

    pvt->pvstringValue = static_cast<PVStringArray *>(pvt->nttable.getPVField(1));
    pvt->pvstringValue->setCapacity(numberChannels);
    pvt->pvstringValue->setCapacityMutable(false);
    pvt->pvstringValue->get(0,numberChannels,&strdata);
    String *pstring = strdata.data;
    for (int i=0; i<numberChannels; i++) pstring[i] = 0.0;
    pvt->pvstringValue->setLength(numberChannels);

    pvt->pvdoubleValue = static_cast<PVDoubleArray *>(pvt->nttable.getPVField(2));
    pvt->pvdoubleValue->setCapacity(numberChannels);
    pvt->pvdoubleValue->setCapacityMutable(false);
    pvt->pvdoubleValue->get(0,numberChannels,&doubledata);
    double *pdouble = doubledata.data;
    for (int i=0; i<numberChannels; i++) pdouble[i] = 0.0;
    pvt->pvdoubleValue->setLength(numberChannels);

    pvt->pvlongValue = static_cast<PVLongArray *>(pvt->nttable.getPVField(3));
    pvt->pvlongValue->setCapacity(numberChannels);
    pvt->pvlongValue->setCapacityMutable(false);
    pvt->pvlongValue->get(0,numberChannels,&longdata);
    int64 *plong = longdata.data;
    for (int i=0; i<numberChannels; i++) plong[i] = 0.0;
    pvt->pvlongValue->setLength(numberChannels);

    pvt->pvarrayValue = static_cast<PVStructureArray *>(pvt->nttable.getPVField(4));
    pvt->pvarrayValue->setCapacity(numberChannels);
    pvt->pvarrayValue->setCapacityMutable(false);
    pvt->pvarrayValue->get(0,numberChannels,&structdata);
    PVStructure**ppPVStructure = structdata.data;
    StructureConstPtr pstructure
        = pvt->pvarrayValue->getStructureArray()->getStructure();
    PVDataCreate *pvDataCreate = getPVDataCreate();
    for (int i=0; i<numberChannels; i++) {
        ppPVStructure[i] = pvDataCreate->createPVStructure(0,pstructure);
    }
    pvt->pvarrayValue->setLength(numberChannels);

    pvt->pvisArray = static_cast<PVBooleanArray *>(pvt->nttable.getPVField(5));
    pvt->pvisArray->setCapacity(numberChannels);
    pvt->pvisArray->setCapacityMutable(false);
    pvt->pvisArray->get(0,numberChannels,&booldata);
    bool *pbool = booldata.data;
    for (int i=0; i<numberChannels; i++) pbool[i] = false;
    pvt->pvisArray->setLength(numberChannels);

    pvt->pvDBRType = static_cast<PVIntArray *>(pvt->nttable.getPVField(6));
    pvt->pvDBRType->setCapacity(numberChannels);
    pvt->pvDBRType->setCapacityMutable(false);
    pvt->pvDBRType->get(0,numberChannels,&intdata);
    int *pDBRType = intdata.data;
    for (int i=0; i<numberChannels; i++) pDBRType[i] = DBF_NO_ACCESS;
    pvt->pvDBRType->setLength(numberChannels);

    pvt->pvisConnected = static_cast<PVBooleanArray *>(pvt->nttable.getPVField(7));
    pvt->pvisConnected->setCapacity(numberChannels);
    pvt->pvisConnected->setCapacityMutable(false);
    pvt->pvisConnected->get(0,numberChannels,&booldata);
    pbool = booldata.data;
    for (int i=0; i<numberChannels; i++) pbool[i] = false;
    pvt->pvisConnected->setLength(numberChannels);

    pvt->pvsecondsPastEpoch = static_cast<PVLongArray *>(pvt->nttable.getPVField(8));
    pvt->pvsecondsPastEpoch->setCapacity(numberChannels);
    pvt->pvsecondsPastEpoch->setCapacityMutable(false);
    pvt->pvsecondsPastEpoch->get(0,numberChannels,&longdata);
    int64 *psecondsPastEpoch = longdata.data;
    for (int i=0; i<numberChannels; i++) psecondsPastEpoch[i] = 0;
    pvt->pvsecondsPastEpoch->setLength(numberChannels);

    pvt->pvnanoSeconds = static_cast<PVIntArray *>(pvt->nttable.getPVField(9));
    pvt->pvnanoSeconds->setCapacity(numberChannels);
    pvt->pvnanoSeconds->setCapacityMutable(false);
    pvt->pvnanoSeconds->get(0,numberChannels,&intdata);
    int32 *pnanoSeconds = intdata.data;
    for (int i=0; i<numberChannels; i++) pnanoSeconds[i] = 0;
    pvt->pvnanoSeconds->setLength(numberChannels);

    pvt->pvtimeStampTag = static_cast<PVIntArray *>(pvt->nttable.getPVField(10));
    pvt->pvtimeStampTag->setCapacity(numberChannels);
    pvt->pvtimeStampTag->setCapacityMutable(false);
    pvt->pvtimeStampTag->get(0,numberChannels,&intdata);
    int32 *ptimeStampTag = intdata.data;
    for (int i=0; i<numberChannels; i++) ptimeStampTag[i] = 0;
    pvt->pvtimeStampTag->setLength(numberChannels);

    pvt->pvalarmSeverity = static_cast<PVIntArray *>(pvt->nttable.getPVField(11));
    pvt->pvalarmSeverity->setCapacity(numberChannels);
    pvt->pvalarmSeverity->setCapacityMutable(false);
    pvt->pvalarmSeverity->get(0,numberChannels,&intdata);
    int *palarmSeverity = intdata.data;
    for (int i=0; i<numberChannels; i++) palarmSeverity[i] = INVALID_ALARM;
    pvt->pvalarmSeverity->setLength(numberChannels);

    pvt->pvalarmStatus = static_cast<PVIntArray *>(pvt->nttable.getPVField(12));
    pvt->pvalarmStatus->setCapacity(numberChannels);
    pvt->pvalarmStatus->setCapacityMutable(false);
    pvt->pvalarmStatus->get(0,numberChannels,&intdata);
    int *palarmStatus = intdata.data;
    for (int i=0; i<numberChannels; i++) palarmStatus[i] = epicsAlarmComm;
    pvt->pvalarmStatus->setLength(numberChannels);

    pvt->pvalarmMessage = static_cast<PVStringArray *>(pvt->nttable.getPVField(13));
    pvt->pvalarmMessage->setCapacity(numberChannels);
    pvt->pvalarmMessage->setCapacityMutable(false);
    pvt->pvalarmMessage->get(0,numberChannels,&strdata);
    String *palarmMessage = strdata.data;
    for (int i=0; i<numberChannels; i++) palarmMessage[i] = String();
    pvt->pvalarmMessage->setLength(numberChannels);

    pvt->state = idle;
    pvt->numberConnected = 0;
    pvt->numberCallbacks = 0;
    pvt->requestOK = false;
    pvt->threadId = 0;
//String builder;
//pvStructure->toString(&builder);
//printf("pvStructure\n%s\n",builder.c_str());
}

GatherV3ScalarData::~GatherV3ScalarData()
{
    if(pvt->state!=idle) disconnect();
    for(int i=0; i<pvt->numberChannels; i++) {
        ChannelID *pChannelID = pvt->apchannelID[i];
        delete pChannelID;
    }
//    delete pvt->apchannelID;
    delete pvt;
}

bool GatherV3ScalarData::connect(double timeOut)
{
    if(pvt->state!=idle) {
        throw std::logic_error(
            "GatherV3ScalarData::connect only legal when state is idle\n");
    }
    SEVCHK(ca_context_create(ca_enable_preemptive_callback),"ca_context_create");
    pvt->threadId = epicsThreadGetIdSelf();
    pvt->state = connecting;
    pvt->numberConnected = 0;
    pvt->numberCallbacks = 0;
    pvt->requestOK = true;
    pvt->event.tryWait();
    int numberChannels = pvt->numberChannels;
    BooleanArrayData bdata;
    pvt->pvisConnected->get(0,numberChannels,&bdata);
    bool *isConnected = bdata.data;
    StringArrayData sdata;
    pvt->pvchannelName->get(0,numberChannels,&sdata);
    String *channelNames = sdata.data;
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
//            char buf[30];
//            sprintf(buf,"%d channels of %d are not connected.",
//                (pvt->numberChannels - pvt->numberConnected),
//                 pvt->numberChannels);
//            pvt->message = String(buf);
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

void GatherV3ScalarData::disconnect()
{
    Lock xx(pvt->mutex);
    if(pvt->state==idle) return;
    if(pvt->threadId!=epicsThreadGetIdSelf()) {
        throw std::logic_error(
            "GatherV3ScalarData::disconnect must be same thread that called connect\n");
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

bool GatherV3ScalarData::get()
{
    if(pvt->state!=connected) {
        throw std::logic_error("GatherV3ScalarData::get illegal state\n");
    }
    if(pvt->threadId!=epicsThreadGetIdSelf()) {
        throw std::logic_error(
            "GatherV3ScalarData::get must be same thread that called connect\n");
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
        if(requestType==requestCharArray) req = DBR_TIME_CHAR;
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
        pvt->message += "timeout";
        pvt->requestOK = false;
        pvt->alarm.setMessage(pvt->message);
        pvt->alarm.setSeverity(invalidAlarm);
        pvt->alarm.setStatus(clientStatus);
    }
    int numberChannels = pvt->numberChannels;
    BooleanArrayData bdata;
    pvt->pvisConnected->get(0,numberChannels,&bdata);
    bool *isConnected = bdata.data;
    LongArrayData ldata;
    pvt->pvsecondsPastEpoch->get(0,numberChannels,&ldata);
    int64 *secondsPastEpoch = ldata.data;
    IntArrayData idata;
    pvt->pvnanoSeconds->get(0,numberChannels,&idata);
    int32 *nanoSeconds = idata.data;
    pvt->pvalarmSeverity->get(0,numberChannels,&idata);
    int32 *alarmSeverity = idata.data;
    pvt->pvalarmStatus->get(0,numberChannels,&idata);
    int32 *alarmStatus = idata.data;
    StringArrayData sdata;
    pvt->pvalarmMessage->get(0,pvt->numberChannels,&sdata);
    String *alarmMessage = sdata.data;
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

bool GatherV3ScalarData::put()
{
    if(pvt->state!=connected) {
        throw std::logic_error("GatherV3ScalarData::put illegal state\n");
    }
    if(pvt->threadId!=epicsThreadGetIdSelf()) {
        throw std::logic_error(
            "GatherV3ScalarData::put must be same thread that called connect\n");
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
    LongArrayData ldata;
    pvt->pvlongValue->get(0,pvt->numberChannels,&ldata);
    int64 * plvalue = ldata.data;
    DoubleArrayData ddata;
    pvt->pvdoubleValue->get(0,pvt->numberChannels,&ddata);
    double * pdvalue = ddata.data;
    StringArrayData sdata;
    pvt->pvstringValue->get(0,pvt->numberChannels,&sdata);
    String * psvalue = sdata.data;
    for(int i=0; i< pvt->numberChannels; i++) {
        ChannelID *channelId = pvt->apchannelID[i];
        chid theChid = channelId->theChid;
        V3RequestType requestType = channelId->requestType;
        const void *pdata = 0;
        int req = 0;
        switch(requestType) {
        case requestLong:
            req = DBR_LONG; pdata = &plvalue[i]; break;
        case requestDouble:
            req = DBR_DOUBLE; pdata = &pdvalue[i]; break;
        case requestString:
            req = DBR_STRING; pdata = psvalue[i].c_str(); break;
        case requestCharArray:
            req = DBR_CHAR; pdata = psvalue[i].c_str(); break;
        }
        int result = ca_put_callback(
            req,
            theChid,
            pdata,
            putCallback,
            pvt->apchannelID[i]);
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
        pvt->message += "timeout";
        pvt->requestOK = false;
        pvt->alarm.setMessage(pvt->message);
        pvt->alarm.setSeverity(invalidAlarm);
        pvt->alarm.setStatus(clientStatus);
    }
    pvt->state = connected;
    return pvt->requestOK;
}

String GatherV3ScalarData::getMessage()
{
    return pvt->message;
}

PVStructure::shared_pointer GatherV3ScalarData::getNTTable()
{
    return pvt->pvStructure;
}

PVDoubleArray * GatherV3ScalarData::getDoubleValue()
{
    return pvt->pvdoubleValue;
}

PVLongArray * GatherV3ScalarData::getLongValue()
{
    return pvt->pvlongValue;
}

PVStringArray * GatherV3ScalarData::getStringValue()
{
    return pvt->pvstringValue;
}

PVLongArray * GatherV3ScalarData::getSecondsPastEpoch()
{
    return pvt->pvsecondsPastEpoch;
}

PVIntArray * GatherV3ScalarData::getNanoSeconds()
{
    return pvt->pvnanoSeconds;
}

PVIntArray * GatherV3ScalarData::getTimeStampTag()
{
    return pvt->pvtimeStampTag;
}

PVIntArray * GatherV3ScalarData::getAlarmSeverity()
{
    return pvt->pvalarmSeverity;
}

PVIntArray * GatherV3ScalarData::getAlarmStatus()
{
    return pvt->pvalarmStatus;
}

PVStringArray * GatherV3ScalarData::getAlarmMessage()
{
    return pvt->pvalarmMessage;
}

PVIntArray * GatherV3ScalarData::getDBRType()
{
    return pvt->pvDBRType;
}

PVBooleanArray * GatherV3ScalarData::getIsConnected()
{
    return pvt->pvisConnected;
}

PVStringArray * GatherV3ScalarData::getChannelName()
{
    return pvt->pvchannelName;
}

}}

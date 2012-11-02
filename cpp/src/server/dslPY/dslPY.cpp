/* dslPY.cpp */
/**
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>

#include <string>
#include <stdexcept>
#include <memory>
#include <vector>

#include <pv/pvIntrospect.h>
#include <pv/pvData.h>
#include <pv/dsl.h>
#include <pv/nt.h>

#include <pv/gatherV3Data.h>

namespace epics { namespace masar { 

using namespace epics::pvData;
using namespace epics::pvAccess;
using std::tr1::static_pointer_cast;

class DSL_RDB;
typedef std::tr1::shared_ptr<DSL_RDB> DSL_RDBPtr;

class DSL_RDB :
    public DSL,
    public std::tr1::enable_shared_from_this<DSL_RDB>
{
public:
    POINTER_DEFINITIONS(DSL_RDB);
    DSL_RDB();
    virtual ~DSL_RDB();
    virtual void destroy();
    virtual PVStructurePtr request(
        String functionName,int num,StringArray const &names,StringArray const &values);
    bool init();
private:
    DSL_RDBPtr getPtrSelf()
    {
        return shared_from_this();
    }

    PyObject * prequest;
    PyObject * pgetchannames;
};

DSL_RDB::DSL_RDB()
    : prequest(0), pgetchannames(0)
{
   PyThreadState *py_tstate = NULL;
   Py_Initialize();
   PyEval_InitThreads();
   py_tstate = PyGILState_GetThisThreadState();
   PyEval_ReleaseThread(py_tstate);
}

DSL_RDB::~DSL_RDB()
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    if(prequest!=0) Py_XDECREF(prequest);
    if(pgetchannames!=0) Py_XDECREF(pgetchannames);
    PyGILState_Release(gstate);
    PyGILState_Ensure();
    Py_Finalize();
}

bool DSL_RDB::init()
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject * module = PyImport_ImportModule("masarserver.dslPY");
    if(module==0) {
        String message("dslPY");
        message += " does not exist or is not a python module";
        printf("DSL_RDB::init %s\n",message.c_str());
        return false;
    }
    PyObject *pclass = PyObject_GetAttrString(module, "DSL");
    if(pclass==0) {
        String message("class DSL");
        message += " does not exist";
        printf("DSL_RDB::init %s\n",message.c_str());
        Py_XDECREF(module);
        return false;
    }
    PyObject *pargs = Py_BuildValue("()");
    if (pargs == NULL) {
        Py_DECREF(pclass);
        printf("Can't build arguments list\n");
        return false;
    }
    PyObject *pinstance = PyEval_CallObject(pclass,pargs);
    Py_DECREF(pargs);
    if(pinstance==0) {
        String message("class DSL");
        message += " constructor failed";
        printf("DSL_RDB::init %s\n",message.c_str());
        Py_XDECREF(pclass);
        Py_XDECREF(module);
        return false;
    }
    prequest = PyObject_GetAttrString(pinstance, "request");
    if(prequest==0) {
        String message("DSL::request");
        message += " could not attach to method";
        printf("DSL_RDB::init %s\n",message.c_str());
        Py_XDECREF(pinstance);
        Py_XDECREF(pclass);
        Py_XDECREF(module);
        return false;
    }
    pgetchannames = PyObject_GetAttrString(pinstance, "retrieveChannelNames");
    if(pgetchannames==0) {
        String message("DSL::request");
        message += " could not attach to method";
        printf("DSL_RDB::init %s\n",message.c_str());
        Py_XDECREF(pinstance);
        Py_XDECREF(pclass);
        Py_XDECREF(module);
        return false;
    }
    Py_XDECREF(pinstance);
    Py_XDECREF(pclass);
    Py_XDECREF(module);
    PyGILState_Release(gstate);
    return true;
}

void DSL_RDB::destroy() {}

static NTTablePtr noDataEnetry(std::string message) {
    FieldCreatePtr fieldCreate = getFieldCreate();
    size_t  n = 1;
    StringArray names;
    FieldConstPtrArray fields;
    names.reserve(n);
    fields.reserve(n);
    names.push_back("status");
    fields.push_back(fieldCreate->createScalarArray(pvBoolean));
    NTTablePtr ntTable(NTTable::create(
        false,true,true,names,fields));
    PVStructurePtr pvStructure = ntTable->getPVStructure();

/* old
    FieldConstPtr fields = fieldCreate->createScalarArray("status",pvBoolean);
    PVStructurePtr pvStructure = NTTable::create(
        false,true,true,1, &fields);

    NTTable ntTable(pvStructure);
*/

    PVBooleanArrayPtr pvBoolVal = static_pointer_cast<PVBooleanArray> (ntTable->getPVField(0));
    BooleanArray temp(1);
    temp[0]=false;
    pvBoolVal -> put (0, 1, temp, 0);

    // Set alarm and severity
    PVAlarm pvAlarm;
    Alarm alarm;
    ntTable->attachAlarm(pvAlarm);

    alarm.setMessage(message);
    alarm.setSeverity(majorAlarm);
    alarm.setStatus(clientStatus);
    pvAlarm.set(alarm);

    // set time stamp
    PVTimeStamp pvTimeStamp;
    ntTable->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return ntTable;
}

static NTTablePtr retrieveSnapshot(PyObject * list)
{
    Py_ssize_t top_len = PyList_Size(list);
    if (top_len != 2) {
        return noDataEnetry("Wrong format for returned data from dslPY when retrieving masar data.");
    }
    PyObject * head_array = PyList_GetItem(list, 0); // get head array
    PyObject * head = PyList_GetItem(head_array, 1); // get label array
    Py_ssize_t tuple_size = PyTuple_Size(head);

    PyObject * data_array = PyList_GetItem(list, 1); // get data array
    // data length in each field
    // (the first row is a description instead of real data)
    Py_ssize_t numberChannels = PyList_Size(data_array) - 1;
    if (numberChannels < 0)
        return noDataEnetry("no channel found in this snapshot.");

    size_t strFieldLen = 3; // pv name, s_value, and alarm message are stored as string.

    FieldCreatePtr fieldCreate = getFieldCreate();

    StringArray names;
    names.reserve(tuple_size);

    // create fields
    // set label for each field
    // ('pv name', 'string value', 'double value', 'long value', 'dbr type', 'isConnected',
    //  'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 'alarmSeverity', 'alarmStatus', 'alarmMessage'
    //  'is_array', 'array_value')
    FieldConstPtrArray fields;
    fields.reserve(tuple_size);
    for (ssize_t i = 0; i < tuple_size; i ++){
        if (i == 0 || i == 1 || i == 11) { // pv_name: 0, string value: 1, alarm message: 11
            fields.push_back(fieldCreate->createScalarArray(pvString));
        } else if (i == 2) { // double value: 2
            fields.push_back(fieldCreate->createScalarArray(pvDouble));
        } else if(i!=13) {
            // long value: 3, dbr type: 4, secondsPastEpoch: 6, nanoSeconds: 7, timeStampTag: 8,
            // alarmSeverity: 9, alarmStatus: 10, is_array: 12
            fields.push_back(fieldCreate->createScalarArray(pvLong));
        } else {
            // for array value operation
            int naf = 3;
            FieldConstPtrArray arrfields(naf);
            arrfields[0] = fieldCreate->createScalarArray(pvString);
            arrfields[1] = fieldCreate->createScalarArray(pvDouble);
            arrfields[2] = fieldCreate->createScalarArray(pvInt);
            StringArray arrayVal(1);
            arrayVal[0] = "arrayValue";
            StructureConstPtr arrStructure = fieldCreate->createStructure(arrayVal,arrfields);
            fields.push_back(fieldCreate->createStructureArray(arrStructure));
        }
        names.push_back(PyString_AsString(PyTuple_GetItem(head, i)));
    }


    // create NTTable
    NTTablePtr ntTable(NTTable::create(
        false,true,true,names,fields));
    PVStructurePtr pvStructure = ntTable->getPVStructure();

    // initilize PVStructureArray for waveform/array record
    PVStructureArrayPtr pvarrayValue = static_pointer_cast<PVStructureArray>(ntTable->getPVField(13));
    pvarrayValue->setCapacity(numberChannels);
    pvarrayValue->setCapacityMutable(false);
    StructureArrayData structdata;
    pvarrayValue->get(0,numberChannels,structdata);
    StructureConstPtr pstructure = pvarrayValue->getStructureArray()->getStructure();
    PVDataCreatePtr pvDataCreate = getPVDataCreate();
    for (int i=0; i<numberChannels; i++) {
        PVStructurePtr ppPVStructure = structdata.data[i];
        ppPVStructure = pvDataCreate->createPVStructure(pstructure);
    }
    pvarrayValue->setLength(numberChannels);

    if (numberChannels > 0) {
        std::vector<std::vector<String> > pvNames (strFieldLen);
        for (size_t i = 0; i < pvNames.size(); i++){
            pvNames[i].resize(numberChannels);
        }
        std::vector<double> dVals(numberChannels);
        std::vector<std::vector<int64> > lVals(tuple_size-strFieldLen-1); //[dataLen];
        for(size_t i=0; i<lVals.size(); i++) {
            lVals[i].resize(numberChannels);
        }

        // Get values for each fields from list
        PyObject * sublist;

        pvarrayValue->get(0,numberChannels,structdata);

        for (int index = 0; index < numberChannels; index++ ){
            sublist = PyList_GetItem(data_array, index+1);
            for (int i = 0; i < tuple_size-1; i ++) { // tuple_size -1: do not parse waveform tuple directly.
                PyObject * temp = PyTuple_GetItem(sublist, i);
                // ('pv name', 'string value', 'double value', 'long value', 'dbr type', 'isConnected',
                //  'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 'alarmSeverity', 'alarmStatus', 'alarmMessage'
                //  'is_array', 'array_value')
                if (i == 0 ) { // pv_name: 0
                    // PyString_Check for type check?
                    if (PyString_AsString (temp) == NULL) {
                        pvNames[0][index] = "";
                    } else {
                        pvNames[0][index] = PyString_AsString (temp);
                    }
                } else if (i == 1 ) { // string value: 1
                    // PyString_Check for type check?
                    if (PyString_AsString (temp) == NULL) {
                        pvNames[1][index] = "";
                    } else {
                        pvNames[1][index] = PyString_AsString (temp);
                    }
                } else if (i == 11 ) { // alarm message: 11
                    // PyString_Check for type check?
                    if (PyString_AsString (temp) == NULL) {
                        pvNames[2][index] = "";
                    } else {
                        pvNames[2][index] = PyString_AsString (temp);
                    }
                } else if (i == 2) { // double value: 2
                    // PyDouble_Check for type check?
                    dVals[index] = PyFloat_AsDouble (temp);
                } else if (i!=13){
                    // long value: 3, dbr type: 4, isConnected: 5, secondsPastEpoch: 6, nanoSeconds: 7,
                    // timeStampTag: 8, alarmSeverity: 9, alarmStatus: 10, is_array: 12
                    // PyLong_Check for type check?
                    if (i == 12) {
                        lVals[i-4][index] = PyLong_AsLongLong (temp);
                    } else {
                        lVals[i-3][index] = PyLong_AsLongLong (temp);
                    }
                }
            }

            PVStructurePtr pvStructure = structdata.data[index];
            // retrieve array value
            if (lVals[8][index] == 1) {
                // EPICS DBR type
                //#define    DBF_STRING  0
                //#define    DBF_INT     1
                //#define    DBF_SHORT   1
                //#define    DBF_FLOAT   2
                //#define    DBF_ENUM    3
                //#define    DBF_CHAR    4
                //#define    DBF_LONG    5
                //#define    DBF_DOUBLE  6
                // check EPICS dbr type
                PyObject * arrayValueList = PyTuple_GetItem(sublist, 13);
                PVFieldPtrArray pvfields = pvStructure->getPVFields();

                if (lVals[1][index] == 1 || lVals[1][index] == 4 || lVals[1][index] == 5){
                    // integer type
                    IntArrayData intdata;
                    PVIntArrayPtr pvintarray = static_pointer_cast<PVIntArray>(pvfields[2]);
                    if (PyList_Check(arrayValueList)) {
                        size_t array_len = (size_t)PyList_Size(arrayValueList);
                        pvintarray->setLength(array_len);
                        pvintarray->get(0,array_len,intdata);
                        IntArray & pvalue = intdata.data;
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyLong_AsLong(PyList_GetItem(arrayValueList, array_index));
                        }
                    } else if (PyTuple_Check(arrayValueList)) {
                        size_t array_len = (size_t)PyTuple_Size(arrayValueList);
                        pvintarray->setLength(array_len);
                        pvintarray->get(0,array_len,intdata);
                        IntArray & pvalue = intdata.data;
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyLong_AsLong(PyTuple_GetItem(arrayValueList, array_index));
                        }
                    }
                } else if (lVals[1][index] == 0) {
                    // string
                    StringArrayData stringdata;
                    PVStringArrayPtr pvstringarray = static_pointer_cast<PVStringArray>(pvfields[0]);
                    if (PyList_Check(arrayValueList)) {
                        size_t array_len = (size_t )PyList_Size(arrayValueList);
                        pvstringarray->setLength(array_len);
                        pvstringarray->get(0,array_len,stringdata);
                        StringArray & pvalue = stringdata.data;
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyString_AsString(PyList_GetItem(arrayValueList, array_index));
                        }
                    } else if (PyTuple_Check(arrayValueList)) {
                        size_t array_len = (size_t )PyTuple_Size(arrayValueList);
                        pvstringarray->setLength(array_len);
                        pvstringarray->get(0,array_len,stringdata);
                        StringArray & pvalue = stringdata.data;
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyString_AsString(PyTuple_GetItem(arrayValueList, array_index));
                        }
                    }
                } else if (lVals[1][index] == 2 || lVals[1][index] == 6) {
                    // float or double
                    DoubleArrayData doubledata;
                    PVDoubleArrayPtr pvdoublearray = static_pointer_cast<PVDoubleArray>(pvfields[1]);
                    if (PyList_Check(arrayValueList)) {
                        size_t array_len = (size_t )PyList_Size(arrayValueList);
                        pvdoublearray->setLength(array_len);
                        pvdoublearray->get(0,array_len,doubledata);
                        DoubleArray & pvalue = doubledata.data;
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyFloat_AsDouble(PyList_GetItem(arrayValueList, array_index));
                        }
                    } else if (PyTuple_Check(arrayValueList)) {
                        size_t array_len = (size_t )PyTuple_Size(arrayValueList);
                        pvdoublearray->setLength(array_len);
                        pvdoublearray->get(0,array_len,doubledata);
                        DoubleArray & pvalue = doubledata.data;
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyFloat_AsDouble(PyTuple_GetItem(arrayValueList, array_index));
                        }
                    }
                }
            }
        }

        // set value to each field
        PVStringArrayPtr pvStr;
        PVDoubleArrayPtr pvDVal;
        PVLongArrayPtr pvLVal;
        for (int i = 0; i < tuple_size; i ++) {
            if (i == 0 ) { // pv_name: 0
                pvStr = static_pointer_cast<PVStringArray>(ntTable->getPVField(i));
                pvStr -> put (0, numberChannels, pvNames[0], 0);
            } else if (i == 1) { // string value: 1
                pvStr = static_pointer_cast<PVStringArray>(ntTable->getPVField(i));
                pvStr -> put (0, numberChannels, pvNames[1], 0);
            } else if (i == 11 ) { // alarm message: 11
                pvStr = static_pointer_cast<PVStringArray>(ntTable->getPVField(11));
                pvStr -> put (0, numberChannels, pvNames[2], 0);
            }else if (i == 2) { // double value: 2
                pvDVal = static_pointer_cast<PVDoubleArray>(ntTable->getPVField(i));
                pvDVal -> put (0, numberChannels, dVals, 0);
            } else if (i!=13){
                // long value: 3, dbr type: 4, isConnected: 5, secondsPastEpoch: 6, nanoSeconds: 7,
                // timeStampTag: 8, alarmSeverity: 9, alarmStatus: 10, is_array: 12
                pvLVal = static_pointer_cast<PVLongArray>(ntTable->getPVField(i));
                if (i == 12)
                    pvLVal -> put (0, numberChannels, lVals[i-4], 0);
                else
                    pvLVal -> put (0, numberChannels, lVals[i-3], 0);
            } else {
            }
        }
    }

    // set time stamp
    PVTimeStamp pvTimeStamp;
    ntTable->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return ntTable;
}

static NTTablePtr retrieveServiceConfigEvents(PyObject * list, long numeric)
{
    Py_ssize_t list_len = PyList_Size(list);
    // data order in the tuple
    // for example result of service config
    // (service_config_id, service_config_name, service_config_desc, service_config_create_date,
    //  service_config_version, and service_name)
    PyObject * labelList = PyList_GetItem(list, 0);
    Py_ssize_t tuple_size = PyTuple_Size(labelList);
    if (tuple_size < numeric) {
        numeric = tuple_size; // all array are numbers
    }
    int fieldLen = list_len - 1; // length - label header

    FieldCreatePtr fieldCreate = getFieldCreate();

    // create fields
    // set label for each field
    FieldConstPtrArray fields(tuple_size);
    StringArray names(tuple_size);
    for (int i = 0; i < numeric; i ++){
        fields[i] = fieldCreate->createScalarArray(pvLong);
        names[i] = String(PyString_AsString(PyTuple_GetItem(labelList, i)));
    }
    for (int i = numeric; i < tuple_size; i ++){
        fields[i] = fieldCreate->createScalarArray(pvString);
        names[i] = String(PyString_AsString(PyTuple_GetItem(labelList, i)));
    }

    // create NTTable
    NTTablePtr ntTable(NTTable::create(
        false,true,true,names,fields));
    PVStructurePtr pvStructure = ntTable->getPVStructure();

    std::vector<std::vector<int64> > scIdVals(numeric);
    for(size_t i=0; i<scIdVals.size(); i++) {
        scIdVals[i].resize(list_len-1);
    }

    std::vector<std::vector<String> > vals (tuple_size-numeric);
    for (size_t i = 0; i < vals.size(); i++){
        vals[i].resize(fieldLen);
    }

    // Get values for each fields from list
    PyObject * sublist;
    for (int index = 1; index < list_len; index++ ){
        sublist = PyList_GetItem(list, index);
        for (int i = 0; i < tuple_size; i ++) {
            PyObject * temp = PyTuple_GetItem(sublist, i);
            if (i < numeric){
                // PyLong_Check for type check?
                scIdVals[i][index-1] = PyLong_AsLongLong(temp);
            } else {
                // PyString_Check for type check?
                if (PyString_AsString(temp) == NULL) {
                    vals[i-numeric][index-1] = "";
                } else {
                    vals[i-numeric][index-1] = PyString_AsString(temp);
                }
            }
        }
    }

    // set value to each numeric field
    PVLongArrayPtr pvSCIds;
    for (int i = 0; i < numeric; i ++) {
        pvSCIds = static_pointer_cast<PVLongArray>(ntTable->getPVField(i));
        pvSCIds -> put (0, fieldLen, scIdVals[i], 0);
    }
    // set value to each string field
    PVStringArrayPtr pvStrVal;
    for (int i = numeric; i < tuple_size; i ++) {
        pvStrVal = static_pointer_cast<PVStringArray>(ntTable->getPVField(i));
        pvStrVal -> put (0, fieldLen, vals[i-numeric], 0);
    }

    PVTimeStamp pvTimeStamp;
    ntTable->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return ntTable;
}

static NTTablePtr saveSnapshot(PyObject * list, NTTablePtr data, String message)
{
    // Get save masar event id
    // -1 means saveSnapshot failure
    int64 eid = -2;
    if (PyTuple_Check(list)){
        PyObject * plist = PyTuple_GetItem(list, 0);
        PyObject * pstatus = PyList_GetItem(plist,0);
        eid = PyLong_AsLongLong(pstatus);
    } else if(PyList_Check(list)) {
        PyObject * pstatus = PyList_GetItem(list,0);
        eid = PyLong_AsLongLong(pstatus);
    } else {
        // updateSnapshotEvent return: not a tuple, nor list.
        return noDataEnetry("Wrong format for returned data from dslPY.");
    }

    if (eid == -1) {
        return noDataEnetry("Machine preview failed. "+ message);
    } else {
        // Set alarm and severity
        PVAlarm pvAlarm;
        Alarm alarm;
        data->attachAlarm(pvAlarm);

        alarm.setMessage("Machine preview Successed. " + message);
        alarm.setSeverity(majorAlarm);
        alarm.setStatus(clientStatus);
        pvAlarm.set(alarm);

        // set time stamp
        PVTimeStamp pvTimeStamp;
        data->attachTimeStamp(pvTimeStamp);
        TimeStamp timeStamp;
        timeStamp.getCurrent();
        timeStamp.setUserTag(eid);
        pvTimeStamp.set(timeStamp);

        return data;
    }
}

static NTTablePtr updateSnapshotEvent(PyObject * list)
{
    // Get save masar event id
    // -1 means updateSnapshotEvent failure
    int64 eid = -2;
    if (PyTuple_Check(list)){
        PyObject * plist = PyTuple_GetItem(list, 0);
        PyObject * pstatus = PyList_GetItem(plist,0);
        eid = PyLong_AsLongLong(pstatus);
    } else if(PyList_Check(list)) {
        PyObject * pstatus = PyList_GetItem(list,0);
        eid = PyLong_AsLongLong(pstatus);
    } else {
        // updateSnapshotEvent return: not a tuple, nor list.
        return noDataEnetry("Wrong format for returned data from dslPY.");
    }

    FieldCreatePtr fieldCreate = getFieldCreate();
    size_t  n = 1;
    StringArray names;
    FieldConstPtrArray fields;
    names.reserve(n);
    fields.reserve(n);
    names.push_back("status");
    fields.push_back(fieldCreate->createScalarArray(pvBoolean));
    NTTablePtr ntTable(NTTable::create(
        false,true,true,names,fields));
    PVStructurePtr pvStructure = ntTable->getPVStructure();


    PVBooleanArrayPtr pvBoolVal = static_pointer_cast<PVBooleanArray>(ntTable->getPVField(0));
    BooleanArray temp(1);
    if (eid >= 0) {
        temp.push_back(true);
        pvBoolVal -> put (0, 1, temp, 0);
    } else {
        temp.push_back(false);
        pvBoolVal -> put (0, 1, temp, 0);
    }

    // Set alarm and severity
    PVAlarm pvAlarm;
    Alarm alarm;
    ntTable->attachAlarm(pvAlarm);

    if (eid >= 0) {
        alarm.setMessage("Falied to save snapshot preview.");
    } else {
        alarm.setMessage("Success to save snapshot preview.");
    }
    alarm.setSeverity(majorAlarm);
    alarm.setStatus(clientStatus);
    pvAlarm.set(alarm);

    // set time stamp
    PVTimeStamp pvTimeStamp;
    ntTable->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return ntTable;
}

static NTTablePtr createResult(
    PyObject *result, String functionName)
{
    NTTablePtr pvStructure;
    {
        PyObject *list = 0;
        if(!PyArg_ParseTuple(result,"O!:dslPY", &PyList_Type,&list))
        {
            printf("Wrong format for returned data from dslPY.\n");
            //THROW_BASE_EXCEPTION("Wrong format for returned data from dslPY.");
            return pvStructure;
        }

        if (functionName.compare("retrieveSnapshot")==0) {
            pvStructure = retrieveSnapshot(list);
        } else if (functionName.compare("retrieveServiceEvents")==0) {
            pvStructure = retrieveServiceConfigEvents(list, 2);
        } else if (functionName.compare("retrieveServiceConfigs")==0) {
            pvStructure = retrieveServiceConfigEvents(list, 1);
        } else if (functionName.compare("retrieveServiceConfigProps")==0) {
            pvStructure = retrieveServiceConfigEvents(list, 2);
        } else if (functionName.compare("updateSnapshotEvent")==0) {
            pvStructure = updateSnapshotEvent(list);
        }
    }
    return pvStructure;
}

static NTTablePtr getLiveMachine(StringArray const & channelName,
                                 int numberChannels, String * message)
{
    GatherV3DataPtr gather = GatherV3DataPtr(
        new GatherV3Data(channelName,numberChannels));

    // wait one second, which is a magic number for now.
    // The waiting time might be removed later after stability test.
    bool result = gather->connect(1.0);
    * message = gather->getMessage();
    if(!result) {
        printf("connect failed\n%s\n",gather->getMessage().c_str());
        if (gather->getConnectedChannels() == 0)
            return noDataEnetry("connect failed "+gather->getMessage());
    }
    if((*message).length() == 0) {
        *message = "All channels are connected.";
    }
    result = gather->get();

    NTTablePtr livedata = gather->getNTTable();

    return livedata;
}

PVStructurePtr DSL_RDB::request(
    String functionName,int num,StringArray const & names,StringArray const &values)
{
    if (functionName.compare("getLiveMachine")==0) {
        String message;
        NTTablePtr ntTable = getLiveMachine(values, num, &message);

//        PVStructurePtr pvStructure = ntTable->getPVStructure();
//        // Set alarm and severity
//        Alarm alarm = ntTable->getNTTableAlarm();
//        alarm.setMessage("Live machine: " + message);
//        alarm.setSeverity(majorAlarm);
//        alarm.setStatus(clientStatus);

//        // set time stamp
//        TimeStamp timeStamp = ntTable->getNTTableTimeStamp();
//        timeStamp.getCurrent();
//        timeStamp.setUserTag(0);

        // Set alarm and severity
        PVAlarm pvAlarm;
        Alarm alarm;
        ntTable->attachAlarm(pvAlarm);
        alarm.setMessage("Live machine: " + message);
        alarm.setSeverity(majorAlarm);
        alarm.setStatus(clientStatus);
        pvAlarm.set(alarm);

        // set time stamp
        PVTimeStamp pvTimeStamp;
        ntTable->attachTimeStamp(pvTimeStamp);
        TimeStamp timeStamp;
        timeStamp.getCurrent();
        timeStamp.setUserTag(0);
        pvTimeStamp.set(timeStamp);
        return ntTable->getPVStructure();
    }

    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *pyDict = PyDict_New();
    for (int i = 0; i < num; i ++) {
        PyObject *pyValue = Py_BuildValue("s",values[i].c_str());
        PyDict_SetItemString(pyDict,names[i].c_str(),pyValue);
    }
    PyObject *pyValue = Py_BuildValue("s",functionName.c_str());
    PyDict_SetItemString(pyDict,"function",pyValue);
    NTTablePtr pvReturn;
    if (functionName.compare("saveSnapshot")==0) {
        // A tuple is needed to pass to Python as parameter.
        PyObject * pyTuple = PyTuple_New(1);
        // put dictionary into the tuple
        PyTuple_SetItem(pyTuple, 0, pyDict);
        PyObject *pchannelnames = PyEval_CallObject(pgetchannames,pyTuple);
        if(pchannelnames == NULL) {
            pvReturn = noDataEnetry("Failed to retrieve channel names.");
        } else {
            Py_ssize_t list_len = PyList_Size(pchannelnames);

            StringArray channames(list_len);
            PyObject * name;
            for (ssize_t i = 0; i < list_len; i ++) {
                name = PyList_GetItem(pchannelnames, i);
                channames[i] = PyString_AsString(name);
            }
            Py_DECREF(pchannelnames);
            String message;
            NTTablePtr data = getLiveMachine(channames, list_len, &message);

            // create a tuple is needed to pass to Python as parameter.
            PyObject * pdata = PyCapsule_New(&data,"pvStructure",0);
            PyObject * pyTuple2 = PyTuple_New(2);

            // first value is the data from live machine
            PyTuple_SetItem(pyTuple2, 0, pdata);
            // second value is the dictionary
            PyTuple_SetItem(pyTuple2, 1, pyDict);
            PyObject *result = PyEval_CallObject(prequest,pyTuple2);
            if(result == NULL) {
                pvReturn = noDataEnetry("Failed to save snapshot.");
            } else {
                pvReturn = saveSnapshot(result, data, message);
                Py_DECREF(result);
            }
            Py_DECREF(pyTuple2);
        }
        Py_DECREF(pyTuple);
    } else {
        // A tuple is needed to pass to Python as parameter.
        PyObject * pyTuple = PyTuple_New(1);
        // put dictionary into the tuple
        PyTuple_SetItem(pyTuple, 0, pyDict);

        PyObject *result = PyEval_CallObject(prequest,pyTuple);
        Py_DECREF(pyTuple);
        if(result == NULL) {
            pvReturn = noDataEnetry("No data entry found in database.");
        } else {
            pvReturn = createResult(result,functionName);
            Py_DECREF(result);
        }
    }
    PyGILState_Release(gstate);
    return pvReturn->getPVStructure();
}

DSLPtr createDSL_RDB()
{
   DSL_RDBPtr dsl = DSL_RDBPtr(new DSL_RDB());
   if(!dsl->init()) return DSL_RDBPtr();
   return DSL_RDBPtr(dsl);
}

}}

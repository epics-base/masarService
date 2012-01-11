/* dsl.cpp */
/**
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>
#include <numpy/arrayobject.h>

#include <string>
#include <stdexcept>
#include <memory>
#include <pv/pvIntrospect.h>
#include <pv/pvData.h>
#include <pv/dsl.h>
#include <pv/nt.h>


namespace epics { namespace masar { 

using namespace epics::pvData;

class DSL_RDB :
    public DSL,
    public std::tr1::enable_shared_from_this<DSL_RDB>
{
public:
    POINTER_DEFINITIONS(DSL_RDB);
    DSL_RDB();
    virtual ~DSL_RDB();
    virtual void destroy();
    virtual PVStructure::shared_pointer request(
        String functionName,int num,String *names,String *values);
    bool init();
private:
    DSL_RDB::shared_pointer getPtrSelf()
    {
        return shared_from_this();
    }
    PyObject * prequest;
};

DSL_RDB::DSL_RDB()
: prequest(0)
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
    PyGILState_Release(gstate);
    PyGILState_Ensure();
    Py_Finalize();
}

bool DSL_RDB::init()
{
    PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject * module = PyImport_ImportModule("dslPY");
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
        prequest =  PyObject_GetAttrString(pinstance, "request");
        if(prequest==0) {
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

static PVStructure::shared_pointer createResult(
    PyObject *result,
    String functionName)
{
    FieldCreate *fieldCreate = getFieldCreate();
    NTField *ntField = NTField::get();
    PVNTField *pvntField = PVNTField::get();
//String builder;
//GUIBAO MUST CREATE fields based on result and functionName.
    int n = 2;
    FieldConstPtr fields[2];
    fields[0] = fieldCreate->createScalarArray("position",pvDouble);
    fields[1] = ntField->createAlarmArray("alarms");
    PVStructure::shared_pointer pvStructure = NTTable::create(
        false,true,true,n,fields);
//builder.clear();
//pvStructure->toString(&builder);
//printf("%s\n",builder.c_str());
//builder.clear();
//pvStructure->getStructure()->toString(&builder);
//printf("%s\n",builder.c_str());
    NTTable ntTable(pvStructure);
    PVDoubleArray *pvPositions
        = static_cast<PVDoubleArray *>(ntTable.getPVField(0));
    double positions[2];
    positions[0] = 1.0;
    positions[1] = 2.0;
    pvPositions->put(0,n,positions,0);
    PVStructureArray *pvAlarms
        = static_cast<PVStructureArray *>(ntTable.getPVField(1));
    PVAlarm pvAlarm;
    Alarm alarm;
    PVStructurePtr palarms[n];
    for(int i=0; i<n; i++) {
        palarms[i] = pvntField->createAlarm(0);
        pvAlarm.attach(palarms[i]);
        alarm.setMessage("test");
        alarm.setSeverity(majorAlarm);
        alarm.setStatus(clientStatus);
        pvAlarm.set(alarm);
    }
    pvAlarms->put(0,n,palarms,0);
    String labels[n];
    labels[0] = pvPositions->getField()->getFieldName();
    labels[1] = pvAlarms->getField()->getFieldName();
    PVStringArray *label = ntTable.getLabel();
    label->put(0,n,labels,0);
    ntTable.attachAlarm(pvAlarm);
    alarm.setMessage("test alarm");
    alarm.setSeverity(majorAlarm);
    alarm.setStatus(clientStatus);
    pvAlarm.set(alarm);
    PVTimeStamp pvTimeStamp;
    ntTable.attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp(1000,1000,10);
    pvTimeStamp.set(timeStamp);
//builder.clear();
//pvStructure->toString(&builder);
//printf("%s\n",builder.c_str());
    return pvStructure;
}

PVStructure::shared_pointer DSL_RDB::request(
    String functionName,int num,String *names,String *values)
{
    char * xxx = 0;
    PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject *pyDict = PyDict_New();
        for (int i = 0; i < num; i ++) {
            PyObject *pyValue = Py_BuildValue("s",values[i].c_str());
            PyDict_SetItemString(pyDict,names[i].c_str(),pyValue);
        }
        PyObject *pyValue = Py_BuildValue("s",functionName.c_str());
        PyDict_SetItemString(pyDict,"function",pyValue);
        PyObject *result = PyEval_CallObject(prequest,pyDict);
        PVStructure::shared_pointer pvReturn =
            createResult(result,functionName);
    PyGILState_Release(gstate);
    printf("DSL::request returned %s\n",xxx);
    return pvReturn;
}

DSL::shared_pointer createDSL_RDB()
{
   DSL_RDB *dsl = new DSL_RDB();
   if(!dsl->init()) {
        delete dsl;
        return DSL_RDB::shared_pointer();
        
   }
   return DSL_RDB::shared_pointer(dsl);
}

}}

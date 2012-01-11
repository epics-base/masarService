/* ntnameValuePy.cpp */
/*
 *Copyright - See the COPYRIGHT that is included with this distribution.
 *EPICS pvServiceCPP is distributed subject to a Software License Agreement found
 *in file LICENSE that is included with this distribution.
 */
/* Author:  Marty Kraimer Date: 2011.12 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>


#include <pv/nt.h>
#include <stdexcept>

using namespace epics::pvData;

namespace epics { namespace pvAccess {

class NTNameValuePvt {
public:
    NTNameValuePvt(
        NTNameValue::shared_pointer ntnameValue);
    ~NTNameValuePvt();
    void destroy();
    PyObject *get(){return pyObject;}
public:
    NTNameValue::shared_pointer ntnameValue;
    PyObject *pyObject;
};

NTNameValuePvt::NTNameValuePvt(
    NTNameValue::shared_pointer arg)
: ntnameValue(arg)
{
    pyObject = PyCapsule_New(&ntnameValue,"pvStructure",0);
    Py_INCREF(pyObject);
}

NTNameValuePvt::~NTNameValuePvt()
{
}

void NTNameValuePvt::destroy()
{
    Py_DECREF(pyObject);
    ntnameValue.reset();
}


static PyObject * _init1(PyObject *willbenull, PyObject *args)
{
    PyObject *self = 0;
    PyObject *capsule = 0;
    if(!PyArg_ParseTuple(args,"OO:ntnamevaluepy",
        &self,
        &capsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(capsule,"pvStructure");
    PVStructure::shared_pointer *pv = 
        static_cast<PVStructure::shared_pointer *>(pvoid);
    NTNameValue::shared_pointer ntnamevalue = NTNameValue::shared_pointer(
        new NTNameValue(*pv));
    NTNameValuePvt *pvt = new NTNameValuePvt(ntnamevalue);
    PyObject *pyObject = PyCapsule_New(pvt,"ntnameValuePvt",0);
    return pyObject;
}

static PyObject * _init(PyObject *willbenull, PyObject *args)
{
    PyObject *self = 0;
    const char *function = 0;
    PyObject *dict = 0;
    if(!PyArg_ParseTuple(args,"OsO!:ntnamevaluepy",
        &self,
        &function,
        &PyDict_Type,&dict))
    {
        return NULL;
    }
    Py_ssize_t n = PyDict_Size(dict);
    String names[n];
    String values[n];
    PyObject *pkey, *pvalue;
    Py_ssize_t pos = 0;
    for(Py_ssize_t i=0; i< n; i++) {
        PyDict_Next(dict,&pos, &pkey, &pvalue);
        char *key = PyString_AS_STRING(pkey);
        char *val = PyString_AS_STRING(pvalue);
        names[i] = String(key);
        values[i] = String(val);
    }
    PVStructure::shared_pointer pv
        = NTNameValue::create(true,false,false);
    NTNameValue::shared_pointer ntnamevalue = NTNameValue::shared_pointer(
        new NTNameValue(pv));
    PVString * pvfunction = ntnamevalue->getFunction();
    PVStringArray *pvnames = ntnamevalue->getNames();
    PVStringArray *pvvalues = ntnamevalue->getValues();
    pvnames->put(0,n,names,0);
    pvvalues->put(0,n,values,0);
    pvfunction->put(function);
    NTNameValuePvt *pvt = new NTNameValuePvt(ntnamevalue);
    PyObject *pyObject = PyCapsule_New(pvt,"ntnameValuePvt",0);
    return pyObject;
}

static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntnameValuePy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    pvt->destroy();
    delete pvt;
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject * _str(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntnameValuePy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    String buffer;
    pvt->ntnameValue->getPVStructure()->toString(&buffer);
    return Py_BuildValue("s",buffer.c_str());

}

static PyObject * _getNTNameValuePy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntnameValuePy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    return pvt->get();
}

static PyObject * _getTimeStamp(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *ptimeStamp = 0;
    if(!PyArg_ParseTuple(args,"OO:ntnameValuePy",
        &pcapsule,
        &ptimeStamp))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(ptimeStamp,"timeStamp");
    TimeStamp *xxx = static_cast<TimeStamp *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntnameValue->getTimeStamp();
    if(pvStructure!=0) {
        PVTimeStamp pvTimeStamp;
        pvTimeStamp.attach(pvStructure);
        pvTimeStamp.get(*xxx);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getAlarm(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *palarm = 0;
    if(!PyArg_ParseTuple(args,"OO:ntnameValuePy",
        &pcapsule,
        &palarm))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(palarm,"alarm");
    Alarm *xxx = static_cast<Alarm *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntnameValue->getAlarm();
    if(pvStructure!=0) {
        PVAlarm pvAlarm;
        pvAlarm.attach(pvStructure);
        pvAlarm.get(*xxx);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getNames(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntnameValuePy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    PVStringArray *pvNames = pvt->ntnameValue->getNames();
    StringArrayData stringArrayData;
    int num = pvNames->get(0,pvNames->getLength(),&stringArrayData);
    String *data = stringArrayData.data;
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; i++) {
        PyObject *elem = Py_BuildValue("s",data[i].c_str());
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject * _getValues(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntnameValuePy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    PVStringArray *pvValues = pvt->ntnameValue->getValues();
    StringArrayData stringArrayData;
    int num = pvValues->get(0,pvValues->getLength(),&stringArrayData);
    String *data = stringArrayData.data;
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; i++) {
        PyObject *elem = Py_BuildValue("s",data[i].c_str());
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static char _init1Doc[] = "_init1 ntnamevaluePy.";
static char _initDoc[] = "_init ntnamevaluePy.";
static char _destroyDoc[] = "_destroy ntnamevaluePy.";
static char _strDoc[] = "_str ntnamevaluePy.";
static char _getNTNameValuePyDoc[] = "_getNTNameValuePy ntnamevaluePy.";
static char _getTimeStampDoc[] = "_getTimeStamp ntnamevaluePy.";
static char _getAlarmDoc[] = "_getAlarm ntnamevaluePy.";
static char _getNamesDoc[] = "_getNames ntnamevaluePy.";
static char _getValuesDoc[] = "_getValues ntnamevaluePy.";


static PyMethodDef methods[] = {
    {"_init1",_init1,METH_VARARGS,_init1Doc},
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"__str__",_str,METH_VARARGS,_strDoc},
    {"_getNTNameValuePy",_getNTNameValuePy,METH_VARARGS,_getNTNameValuePyDoc},
    {"_getTimeStamp",_getTimeStamp,METH_VARARGS,_getTimeStampDoc},
    {"_getAlarm",_getAlarm,METH_VARARGS,_getAlarmDoc},
    {"_getNames",_getNames,METH_VARARGS,_getNamesDoc},
    {"_getValues",_getValues,METH_VARARGS,_getValuesDoc},

    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initntnameValuePy(void)
{
    PyObject * m = Py_InitModule("ntnameValuePy",methods);
    if(m==NULL) printf("initntnameValuePy failed\n");
}

}}


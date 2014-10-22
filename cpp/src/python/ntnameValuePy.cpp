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

#include <sstream>

#include <pv/nt.h>
#include <stdexcept>

namespace epics { namespace masar {

using namespace epics::pvData;
using namespace epics::nt;
using namespace std;

static FieldCreatePtr fieldCreate = getFieldCreate();

class NTNameValuePvt {
public:
    NTNameValuePvt(
        NTNameValue::shared_pointer ntnameValue,PVStructure::shared_pointer const & pvStructure);
    ~NTNameValuePvt();
    void destroy();
    PyObject *get(){return pyObject;}
public:
    NTNameValue::shared_pointer ntnameValue;
    PVStructure::shared_pointer pvStructure;
    PyObject *pyObject;
};

NTNameValuePvt::NTNameValuePvt(
    NTNameValue::shared_pointer arg,PVStructure::shared_pointer const & pv)
: ntnameValue(arg),
  pvStructure(pv),
  pyObject(0)
{
    pyObject = PyCapsule_New(&pvStructure,"pvStructure",0);
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


static PyObject * _init(PyObject *willbenull, PyObject *args)
{
    const char *function = 0;
    PyObject *dict = 0;
    if(!PyArg_ParseTuple(args,"sO!:ntnamevaluepy",
        &function,
        &PyDict_Type,&dict))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (function,dictionary)");
        return NULL;
    }
    Py_ssize_t n = PyDict_Size(dict);
    shared_vector<string> name(n);
    shared_vector<string> value(n);
    PyObject *pkey, *pvalue;
    Py_ssize_t pos = 0;
    for(Py_ssize_t i=0; i< n; i++) {
        PyDict_Next(dict,&pos, &pkey, &pvalue);
        char *key = PyString_AS_STRING(pkey);
        char *val = PyString_AS_STRING(pvalue);
        name[i] = string(key);
        value[i] = string(val);
    }
    FieldConstPtr field = fieldCreate->createScalar(pvString);
    NTNameValueBuilderPtr builder = NTNameValue::createBuilder();
    NTNameValuePtr ntnamevalue = builder ->
         value(pvString) ->
         add("function",fieldCreate->createScalar(pvString)) ->
         addDescriptor() ->
         addTimeStamp() ->
         addAlarm() ->
         create();
    PVStructurePtr pv = ntnamevalue->getPVStructure();
    PVStringArrayPtr pvname = pv->getSubField<PVStringArray>("name");
    PVStringArrayPtr pvvalue = pv->getSubField<PVStringArray>("value");
    PVStringPtr pvfunction = pv->getSubField<PVString>("function");
    pvfunction->put(function);
    shared_vector<const string> nn(freeze(name));
    pvname->replace(nn);
    shared_vector<const string> vv(freeze(value));
    pvvalue->replace(vv);
    NTNameValuePvt *pvt = new NTNameValuePvt(ntnamevalue,pv);
    return PyCapsule_New(pvt,"ntnameValuePvt",0);
}

static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntnameValuePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
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
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);

    std::stringstream buffer;
    buffer << *(pvt->ntnameValue->getPVStructure());
    return Py_BuildValue("s",buffer.str().c_str());

}

static PyObject * _getNTNameValuePy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntnameValuePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    return pvt->get();
}

static PyObject * _getPVStructure(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntnameValuePy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    pvt->pvStructure = pvt->ntnameValue->getPVStructure();
    return PyCapsule_New(&pvt->pvStructure,"pvStructure",0);
}


static PyObject * _getFunction(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntnameValuePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    PVStringPtr pvString = pvt->ntnameValue->getDescriptor();
    string message = pvString->get();
    return Py_BuildValue("s",message.c_str());
}

static PyObject * _getTimeStamp(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *ptimeStamp = 0;
    if(!PyArg_ParseTuple(args,"OO:ntnameValuePy",
        &pcapsule,
        &ptimeStamp))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(ptimeStamp,"timeStamp");
    TimeStamp *xxx = static_cast<TimeStamp *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntnameValue->getTimeStamp();
    //if(pvStructure!=0) {
    if(!pvStructure) {
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
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,palarm)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(palarm,"alarm");
    Alarm *xxx = static_cast<Alarm *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntnameValue->getAlarm();
    //if(pvStructure!=0) {
    if(!pvStructure) {
        PVAlarm pvAlarm;
        pvAlarm.attach(pvStructure);
        pvAlarm.get(*xxx);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getName(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntnameValuePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntnameValue->getPVStructure();
    PVStringArrayPtr pvName = pvStructure->getSubField<PVStringArray>("name");
    const shared_vector<const string> name(pvName->view());
    size_t num = name.size();
    PyObject *result = PyTuple_New(num);
    for(size_t i=0; i<num; i++) {
        PyObject *elem = Py_BuildValue("s",name[i].c_str());
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject * _getValue(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntnameValuePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntnameValuePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTNameValuePvt *pvt = static_cast<NTNameValuePvt *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntnameValue->getPVStructure();
    PVStringArrayPtr pvValue = pvStructure->getSubField<PVStringArray>("value");
    const shared_vector<const string> value(pvValue->view());
    size_t num = value.size();
    PyObject *result = PyTuple_New(num);
    for(size_t i=0; i<num; i++) {
        PyObject *elem = Py_BuildValue("s",value[i].c_str());
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static char _initDoc[] = "_init ntnamevaluePy.";
static char _destroyDoc[] = "_destroy ntnamevaluePy.";
static char _strDoc[] = "_str ntnamevaluePy.";
static char _getNTNameValuePyDoc[] = "_getNTNameValuePy ntnamevaluePy.";
static char _getPVStructureDoc[] = "_getPVStructure.";
static char _getFunctionDoc[] = "_getFunction ntnamevaluePy.";
static char _getTimeStampDoc[] = "_getTimeStamp ntnamevaluePy.";
static char _getAlarmDoc[] = "_getAlarm ntnamevaluePy.";
static char _getNameDoc[] = "_getName ntnamevaluePy.";
static char _getValueDoc[] = "_getValue ntnamevaluePy.";


static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_str",_str,METH_VARARGS,_strDoc},
    {"_getNTNameValuePy",_getNTNameValuePy,METH_VARARGS,_getNTNameValuePyDoc},
    {"_getPVStructure",_getPVStructure,METH_VARARGS,_getPVStructureDoc},
    {"_getFunction",_getFunction,METH_VARARGS,_getFunctionDoc},
    {"_getTimeStamp",_getTimeStamp,METH_VARARGS,_getTimeStampDoc},
    {"_getAlarm",_getAlarm,METH_VARARGS,_getAlarmDoc},
    {"_getName",_getName,METH_VARARGS,_getNameDoc},
    {"_getValue",_getValue,METH_VARARGS,_getValueDoc},

    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initntnameValuePy(void)
{
    PyObject * m = Py_InitModule("ntnameValuePy",methods);
    if(m==NULL) printf("initntnameValuePy failed\n");
}

}}


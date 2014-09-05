/* nttablePy.cpp */
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

#include <pv/convert.h>
#include <pv/nt.h>
#include <stdexcept>

namespace epics { namespace masar {

using std::tr1::static_pointer_cast;
using namespace epics::pvData;
using namespace epics::nt;
using namespace std;

class NTTablePvt {
public:
    NTTablePvt(
        NTTable::shared_pointer nttable,
        PVStructurePtr const & pvStructure);
    ~NTTablePvt();
    void destroy();
    PyObject *get(){return pyObject;}
public:
    NTTable::shared_pointer nttable;
    PVStructurePtr pvStructure;
    PyObject *pyObject;
};

NTTablePvt::NTTablePvt(
    NTTable::shared_pointer arg,
    PVStructurePtr const & pv)
: nttable(arg),
  pvStructure(pv),
  pyObject(0)
{
    pyObject = PyCapsule_New(&pvStructure,"pvStructure",0);
    Py_INCREF(pyObject);
}

NTTablePvt::~NTTablePvt()
{
}

void NTTablePvt::destroy()
{
    Py_DECREF(pyObject);
    nttable.reset();
}


static PyObject * _init(PyObject *willbenull, PyObject *args)
{
    PyObject *dict = 0;
    if(!PyArg_ParseTuple(args,"O!:ntnamevaluepy",
        &PyDict_Type,&dict))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (dictionary)");
        return NULL;
    }
    Py_ssize_t n = PyDict_Size(dict);
    shared_vector<string> names(n);
    shared_vector<string> types(n);
    PyObject *pkey, *ptype;
    Py_ssize_t pos = 0;
    for(Py_ssize_t i=0; i< n; i++) {
        PyDict_Next(dict,&pos, &pkey, &ptype);
        char *key = PyString_AS_STRING(pkey);
        char *typ = PyString_AS_STRING(ptype);
        names[i] = string(key);
        types[i] = string(typ);
    }
    shared_vector<ScalarType> scalarType(n);
    size_t nn = n;
    for(size_t i=0; i<nn; ++i) {
         string next = types[i];
         if(next.compare("boolean")==0) {
             scalarType[i] = pvBoolean;
             continue;
         }
         if(next.compare("byte")==0) {
             scalarType[i] = pvByte;
             continue;
         }
         if(next.compare("short")==0) {
             scalarType[i] = pvShort;
             continue;
         }
         if(next.compare("int")==0) {
             scalarType[i] = pvInt;
             continue;
         }
         if(next.compare("long")==0) {
             scalarType[i] = pvLong;
             continue;
         }
         if(next.compare("float")==0) {
             scalarType[i] = pvFloat;
             continue;
         }
         if(next.compare("double")==0) {
             scalarType[i] = pvDouble;
             continue;
         }
         if(next.compare("string")==0) {
             scalarType[i] = pvString;
             continue;
         }
         PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. illegal type specified");
        return NULL;
    }
    NTTableBuilderPtr builder = NTTable::createBuilder();
    for(size_t i=0; i<nn; ++i) {
        builder->add(names[i],scalarType[i]);
    }
    NTTablePtr nttable = builder ->
         addTimeStamp() ->
         addAlarm() ->
         create();
    PVStructurePtr pv = nttable->getPVStructure();
    NTTablePvt *pvt = new NTTablePvt(nttable,pv);
    return PyCapsule_New(pvt,"nttablePvt",0);
}

static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    pvt->destroy();
    delete pvt;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _str(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    std::stringstream buffer;
    buffer << *(pvt->nttable->getPVStructure());
    return Py_BuildValue("s",buffer.str().c_str());
}

static PyObject * _getNTTablePy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    return pvt->get();
}

static PyObject * _getTimeStamp(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *ptimeStamp = 0;
    if(!PyArg_ParseTuple(args,"OO:nttablePy",
        &pcapsule,
        &ptimeStamp))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,ptimeStamp)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(ptimeStamp,"timeStamp");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "second argument is not a timeStamp capsule");
        return NULL;
    }
    TimeStamp *xxx = static_cast<TimeStamp *>(pvoid);
    PVStructurePtr pvStructure = pvt->nttable->getTimeStamp();
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
    if(!PyArg_ParseTuple(args,"OO:nttablePy",
        &pcapsule,
        &palarm))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,palarm)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(palarm,"alarm");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "second argument is not an alarm capsule");
        return NULL;
    }
    Alarm *xxx = static_cast<Alarm *>(pvoid);
    PVStructurePtr pvStructure = pvt->nttable->getAlarm();
    if(pvStructure!=0) {
        PVAlarm pvAlarm;
        pvAlarm.attach(pvStructure);
        pvAlarm.get(*xxx);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getLabels(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    PVStringArrayPtr pvLabel = pvt->nttable->getLabels();
    shared_vector<const string> data(pvLabel->view());
    int num = data.size();
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; i++) {
        PyObject *elem = Py_BuildValue("s",data[i].c_str());
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject *getScalarArrayValue(PVScalarArrayPtr pvScalarArray)
{
    ScalarType scalarType = pvScalarArray->getScalarArray()->getElementType();
    switch(scalarType) {
        case pvBoolean: {
            PVBooleanArrayPtr pvArray = static_pointer_cast<PVBooleanArray>(pvScalarArray);
            shared_vector<const boolean> data(pvArray->view());
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = (data[i] ? 1 : 0);
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvByte: {
            PVByteArrayPtr pvArray = static_pointer_cast<PVByteArray>(pvScalarArray);
            shared_vector<const int8> data(pvArray->view());
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = data[i];
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvUByte: {
            PVUByteArrayPtr pvArray = static_pointer_cast<PVUByteArray>(pvScalarArray);
            shared_vector<const uint8> data(pvArray->view());
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = data[i];
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvShort: {
            PVShortArrayPtr pvArray = static_pointer_cast<PVShortArray>(pvScalarArray);
            shared_vector<const int16> data(pvArray->view());
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = data[i];
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvUShort: {
            PVUShortArrayPtr pvArray = static_pointer_cast<PVUShortArray>(pvScalarArray);
            shared_vector<const uint16> data(pvArray->view());
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = data[i];
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvInt: {
            PVIntArrayPtr pvArray = static_pointer_cast<PVIntArray>(pvScalarArray);
            shared_vector<const int32> data(pvArray->view());
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("i",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvUInt: {
            PVUIntArrayPtr pvArray = static_pointer_cast<PVUIntArray>(pvScalarArray);
            shared_vector<const uint32> data(pvArray->view());
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("i",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvLong: {
            PVLongArrayPtr pvArray = static_pointer_cast<PVLongArray>(pvScalarArray);
            shared_vector<const int64> data(pvArray->view());
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("k",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvULong: {
            PVULongArrayPtr pvArray = static_pointer_cast<PVULongArray>(pvScalarArray);
            shared_vector<const uint64> data(pvArray->view());
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("k",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvFloat: {
            PVFloatArrayPtr pvArray = static_pointer_cast<PVFloatArray>(pvScalarArray);
            shared_vector<const float> data(pvArray->view());
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("f",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvDouble: {
            PVDoubleArrayPtr pvArray = static_pointer_cast<PVDoubleArray>(pvScalarArray);
            shared_vector<const double> data(pvArray->view());
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("d",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvString: {
            PVStringArrayPtr pvArray = static_pointer_cast<PVStringArray>(pvScalarArray);
            shared_vector<const string> data(pvArray->view());
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("s",data[i].c_str());
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getColumn(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    const char *name = 0;
    if(!PyArg_ParseTuple(args,"Os:nttablePy",
        &pcapsule,
        &name))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,index)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    PVFieldPtr pvField =  pvt->nttable->getColumn(name);
    Type type = pvField->getField()->getType();
    if(type!=scalarArray) {
        PyErr_SetString(PyExc_SyntaxError,
           "logic error. Why is a column not a scalarArray?");
        return NULL;
    }
    PVScalarArrayPtr pvScalarArray = static_pointer_cast<PVScalarArray>(pvField);
    return getScalarArrayValue(pvScalarArray);
}


static char _initDoc[] = "_init nttablePy.";
static char _destroyDoc[] = "_destroy nttablePy.";
static char _strDoc[] = "_str  nttablePy.";
static char _getNTTablePyDoc[] = "_getNTTablePy nttablePy.";
static char _getTimeStampDoc[] = "_getTimeStamp nttablePy.";
static char _getAlarmDoc[] = "_getAlarm nttablePy.";
static char _getLabelsDoc[] = "_getLabels nttablePy.";
static char _getColumnDoc[] = "_getColumn nttablePy.";

static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_str",_str,METH_VARARGS,_strDoc},
    {"_getNTTablePy",_getNTTablePy,METH_VARARGS,_getNTTablePyDoc},
    {"_getTimeStamp",_getTimeStamp,METH_VARARGS,_getTimeStampDoc},
    {"_getAlarm",_getAlarm,METH_VARARGS,_getAlarmDoc},
    {"_getLabels",_getLabels,METH_VARARGS,_getLabelsDoc},
    {"_getColumn",_getColumn,METH_VARARGS,_getColumnDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initnttablePy(void)
{
    PyObject * m = Py_InitModule("nttablePy",methods);
    if(m==NULL) printf("initnttablePy failed\n");
}

}}


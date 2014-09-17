/* ntmultiChannelPy.cpp */
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

using namespace epics::pvData;
using namespace epics::nt;
using namespace std;
using std::tr1::static_pointer_cast;

class NTMultiChannelPvt {
public:
    NTMultiChannelPvt(
        NTMultiChannel::shared_pointer ntmultiChannel,
        PVStructurePtr const & pvStructure);
    ~NTMultiChannelPvt();
    void destroy();
    PyObject *get(){return pyObject;}
public:
    NTMultiChannel::shared_pointer ntmultiChannel;
    PVStructurePtr pvStructure;
    PyObject *pyObject;
};

NTMultiChannelPvt::NTMultiChannelPvt(
    NTMultiChannel::shared_pointer arg,
    PVStructurePtr const & pv)
: ntmultiChannel(arg),
  pvStructure(pv),
  pyObject(0)
{
    pyObject = PyCapsule_New(&pvStructure,"pvStructure",0);
    Py_INCREF(pyObject);
}

NTMultiChannelPvt::~NTMultiChannelPvt()
{
}

void NTMultiChannelPvt::destroy()
{
    Py_DECREF(pyObject);
    ntmultiChannel.reset();
}

static PyObject * _init(PyObject *willbenull, PyObject *args)
{
    PyObject *capsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelpy",
        &capsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvStructure)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(capsule,"pvStructure");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Must be pvStructure PyCapsule");
        return NULL;
    }
    PVStructurePtr *pv =
        static_cast<PVStructurePtr *>(pvoid);
    PVStructurePtr pvStructure = *pv;
    NTMultiChannelPtr ntmultiChannel = NTMultiChannel::narrow(pvStructure);
    NTMultiChannelPvt *pvt = new NTMultiChannelPvt(ntmultiChannel,pvStructure);
    return PyCapsule_New(pvt,"ntmultiChannelPvt",0);
}

static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    pvt->destroy();
    delete pvt;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _str(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    std::stringstream buffer;
    buffer << *(pvt->ntmultiChannel->getPVStructure());
    return Py_BuildValue("s",buffer.str().c_str());
}

static PyObject * _getNTMultiChannelPy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    return pvt->get();
}

static PyObject * _getPVStructure(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPy");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    pvt->pvStructure = pvt->ntmultiChannel->getPVStructure();
    return PyCapsule_New(&pvt->pvStructure,"pvStructure",0);
}


static PyObject * _getTimeStamp(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *ptimeStamp = 0;
    if(!PyArg_ParseTuple(args,"OO:ntmultiChannelPy",
        &pcapsule,
        &ptimeStamp))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,ptimeStamp)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(ptimeStamp,"timeStamp");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "second argument is not a timeStamp capsule");
        return NULL;
    }
    TimeStamp *xxx = static_cast<TimeStamp *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntmultiChannel->getTimeStamp();
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
    if(!PyArg_ParseTuple(args,"OO:ntmultiChannelPy",
        &pcapsule,
        &palarm))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,palarm)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(palarm,"alarm");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "second argument is not an alarm capsule");
        return NULL;
    }
    Alarm *xxx = static_cast<Alarm *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntmultiChannel->getAlarm();
    //if(pvStructure!=0) {
    if(!pvStructure) {
        PVAlarm pvAlarm;
        pvAlarm.attach(pvStructure);
        pvAlarm.get(*xxx);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getNumberChannel(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    int nchan = pvt->ntmultiChannel->getChannelName()->getLength();
    return Py_BuildValue("i",nchan);
}

static PyObject *getScalarValue(PVScalarPtr pvScalar)
{
    ConvertPtr convert = getConvert();
    ScalarType scalarType = pvScalar->getScalar()->getScalarType();
    switch(scalarType) {
        case pvBoolean: {
            PVBooleanPtr pv =  static_pointer_cast<PVBoolean>(pvScalar);
            bool value = pv->get();
            int ivalue = (value ? 1 : 0);
            return Py_BuildValue("i",ivalue);
        }
        case pvByte:
        case pvShort:
        case pvInt:
        {
            int32 value = convert->toInt(pvScalar);
            return Py_BuildValue("i",value);
        }
        case pvUByte:
        case pvUShort:
        case pvUInt:
        {
            uint32 value = convert->toUInt(pvScalar);
            return Py_BuildValue("i",value);
        }
        case pvLong: {
            int64 value = convert->toLong(pvScalar);
            return Py_BuildValue("k",value);
        }
        case pvULong: {
            uint64 value = convert->toULong(pvScalar);
            return Py_BuildValue("k",value);
        }
        case pvFloat: {
            float value = convert->toFloat(pvScalar);
            return Py_BuildValue("f",value);
        }
        case pvDouble: {
            double value = convert->toDouble(pvScalar);
            return Py_BuildValue("d",value);
        }
        case pvString: {
            string value = convert->toString(pvScalar);
            return Py_BuildValue("s",value.c_str());
        }
    }
    Py_INCREF(Py_None);
    return Py_None;
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

static PyObject * _getValue(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    PVUnionArrayPtr pvValue =
        pvt->ntmultiChannel->getPVStructure()->getSubField<PVUnionArray>("value");
    shared_vector<const PVUnionPtr> data(pvValue->view());
    int num = data.size();
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; ++i) {
        PVFieldPtr pvField = data[i]->get();
        Type type = pvField->getField()->getType();
        switch(type) {
        case scalar:
             PyTuple_SetItem(result,i,getScalarValue(static_pointer_cast<PVScalar>(pvField)));
             break;
        case scalarArray:
             PyTuple_SetItem(result,i,getScalarArrayValue(static_pointer_cast<PVScalarArray>(pvField)));
             break;
        default:
            string value("unhandled type");
            PyObject *elem = Py_BuildValue("s",value.c_str());
            PyTuple_SetItem(result, i, elem);
            break;
           
        }
    }
    return result;
}

static PyObject * _getChannelName(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    PVStringArrayPtr pvValue =
        pvt->ntmultiChannel->getPVStructure()->getSubField<PVStringArray>("channelName");
    shared_vector<const string> data(pvValue->view());
    int num = data.size();
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; ++i) {
        string value = data[i];
        PyObject *elem = Py_BuildValue("s",value.c_str());
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject * _getIsConnected(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    PVBooleanArrayPtr pvValue =
        pvt->ntmultiChannel->getPVStructure()->getSubField<PVBooleanArray>("isConnected");
    shared_vector<const boolean> data(pvValue->view());
    int num = data.size();
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; ++i) {
        boolean boolval = data[i];
        string value;
        if(boolval) {
           value = "true";
        } else {
           value = "false";
        }
        PyObject *elem = Py_BuildValue("s",value.c_str());
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject * _getSeverity(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    PVIntArrayPtr pvValue =
        pvt->ntmultiChannel->getPVStructure()->getSubField<PVIntArray>("severity");
    shared_vector<const int32> data(pvValue->view());
    int num = data.size();
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; ++i) {
        int value = data[i];
        PyObject *elem = Py_BuildValue("i",value);
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject * _getStatus(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    PVIntArrayPtr pvValue =
        pvt->ntmultiChannel->getPVStructure()->getSubField<PVIntArray>("status");
    shared_vector<const int32> data(pvValue->view());
    int num = data.size();
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; ++i) {
        int value = data[i];
        PyObject *elem = Py_BuildValue("i",value);
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject * _getMessage(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    PVStringArrayPtr pvValue =
        pvt->ntmultiChannel->getPVStructure()->getSubField<PVStringArray>("message");
    shared_vector<const string> data(pvValue->view());
    int num = data.size();
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; ++i) {
        string value = data[i];
        PyObject *elem = Py_BuildValue("s",value.c_str());
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject * _getSecondsPastEpoch(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    PVLongArrayPtr pvValue =
        pvt->ntmultiChannel->getPVStructure()->getSubField<PVLongArray>("secondsPastEpoch");
    shared_vector<const int64> data(pvValue->view());
    int num = data.size();
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; ++i) {
        int64 value = data[i];
        PyObject *elem = Py_BuildValue("l",value);
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject * _getNanoseconds(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    PVIntArrayPtr pvValue =
        pvt->ntmultiChannel->getPVStructure()->getSubField<PVIntArray>("nanoseconds");
    shared_vector<const int32> data(pvValue->view());
    int num = data.size();
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; ++i) {
        int value = data[i];
        PyObject *elem = Py_BuildValue("i",value);
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject * _getUserTag(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    PVIntArrayPtr pvValue =
        pvt->ntmultiChannel->getPVStructure()->getSubField<PVIntArray>("userTag");
    shared_vector<const int32> data(pvValue->view());
    int num = data.size();
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; ++i) {
        int value = data[i];
        PyObject *elem = Py_BuildValue("i",value);
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject * _getDescriptor(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntmultiChannelPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntmultiChannelPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTMultiChannelPvt *pvt = static_cast<NTMultiChannelPvt *>(pvoid);
    PVStringPtr pvValue =
        pvt->ntmultiChannel->getPVStructure()->getSubField<PVString>("descriptor");
    string value("");
    if(pvValue) value =  pvValue->get();
    return Py_BuildValue("s",value.c_str());
}


static char _initDoc[] = "_init ntmultiChannelPy.";
static char _destroyDoc[] = "_destroy ntmultiChannelPy.";
static char _strDoc[] = "_str  ntmultiChannelPy.";
static char _getNTMultiChannelPyDoc[] = "_getNTMultiChannelPy ntmultiChannelPy.";
static char _getPVStructureDoc[] = "_getPVStructure.";
static char _getTimeStampDoc[] = "_getTimeStamp ntmultiChannelPy.";
static char _getAlarmDoc[] = "_getAlarm ntmultiChannelPy.";
static char _getNumberChannelDoc[] = "_getNumberChannel ntmultiChannelPy.";
static char _getValueDoc[] = "_getValue ntmultiChannelPy.";
static char _getChannelNameDoc[] = "_getChannelName ntmultiChannelPy.";
static char _getIsConnectedDoc[] = "_getIsConnected ntmultiChannelPy.";
static char _getSeverityDoc[] = "_getSeverity ntmultiChannelPy.";
static char _getStatusDoc[] = "_getStatus ntmultiChannelPy.";
static char _getMessageDoc[] = "_getMessage ntmultiChannelPy.";
static char _getSecondsPastEpochDoc[] = "_getSecondsPastEpoch ntmultiChannelPy.";
static char _getNanosecondsDoc[] = "_getNanoseconds ntmultiChannelPy.";
static char _getUserTagDoc[] = "_getUserTag ntmultiChannelPy.";
static char _getDescriptorDoc[] = "_getDescriptor ntmultiChannelPy.";

static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_str",_str,METH_VARARGS,_strDoc},
    {"_getNTMultiChannelPy",_getNTMultiChannelPy,METH_VARARGS,_getNTMultiChannelPyDoc},
    {"_getPVStructure",_getPVStructure,METH_VARARGS,_getPVStructureDoc},
    {"_getTimeStamp",_getTimeStamp,METH_VARARGS,_getTimeStampDoc},
    {"_getAlarm",_getAlarm,METH_VARARGS,_getAlarmDoc},
    {"_getNumberChannel",_getNumberChannel,METH_VARARGS,_getNumberChannelDoc},
    {"_getValue",_getValue,METH_VARARGS,_getValueDoc},
    {"_getChannelName",_getChannelName,METH_VARARGS,_getChannelNameDoc},
    {"_getIsConnected",_getIsConnected,METH_VARARGS,_getIsConnectedDoc},
    {"_getSeverity",_getSeverity,METH_VARARGS,_getSeverityDoc},
    {"_getStatus",_getStatus,METH_VARARGS,_getStatusDoc},
    {"_getMessage",_getMessage,METH_VARARGS,_getMessageDoc},
    {"_getSecondsPastEpoch",_getSecondsPastEpoch,METH_VARARGS,_getSecondsPastEpochDoc},
    {"_getNanoseconds",_getNanoseconds,METH_VARARGS,_getNanosecondsDoc},
    {"_getUserTag",_getUserTag,METH_VARARGS,_getUserTagDoc},
    {"_getDescriptor",_getDescriptor,METH_VARARGS,_getDescriptorDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initntmultiChannelPy(void)
{
    PyObject * m = Py_InitModule("ntmultiChannelPy",methods);
    if(m==NULL) printf("initntmultiChannelPy failed\n");
}

}}


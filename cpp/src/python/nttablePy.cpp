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
#include <numpy/arrayobject.h>


#include <pv/convert.h>
#include <pv/nt.h>
#include <stdexcept>

using namespace epics::pvData;

namespace epics { namespace pvAccess {

class NTTablePvt {
public:
    NTTablePvt(
        NTTable::shared_pointer nttable);
    ~NTTablePvt();
    void destroy();
    PyObject *get(){return pyObject;}
public:
    NTTable::shared_pointer nttable;
    PyObject *pyObject;
};

NTTablePvt::NTTablePvt(
    NTTable::shared_pointer arg)
: nttable(arg),
  pyObject(0)
{
    pyObject = PyCapsule_New(&nttable,"nttable",0);
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
    PyObject *self = 0;
    PyObject *capsule = 0;
    if(!PyArg_ParseTuple(args,"OO:nttablepy",
        &self,
        &capsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(capsule,"pvStructure");
    PVStructure::shared_pointer *pv = 
        static_cast<PVStructure::shared_pointer *>(pvoid);
    NTTable::shared_pointer nttable = NTTable::shared_pointer(
        new NTTable(*pv));
    NTTablePvt *pvt = new NTTablePvt(nttable);
    PyObject *pyObject = PyCapsule_New(pvt,"nttablePvt",0);
    return pyObject;
}

static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
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
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    String buffer;
    pvt->nttable->getPVStructure()->toString(&buffer);
    return Py_BuildValue("s",buffer.c_str());
}

static PyObject * _getNTTablePy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
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
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(ptimeStamp,"timeStamp");
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
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(palarm,"alarm");
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

static PyObject * _getNumberValues(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    int nvalues = pvt->nttable->getNumberValues();
    return Py_BuildValue("i",nvalues);
}

static PyObject * _getLabel(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    PVStringArray *pvLabel = pvt->nttable->getLabel();
    StringArrayData stringArrayData;
    int num = pvLabel->get(0,pvLabel->getLength(),&stringArrayData);
    String *data = stringArrayData.data;
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; i++) {
        PyObject *elem = Py_BuildValue("s",data[i].c_str());
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject *getScalarValue(PVScalar *pvScalar)
{
    Convert *convert = getConvert();
    ScalarType scalarType = pvScalar->getScalar()->getScalarType();
    switch(scalarType) {
        case pvBoolean: {
            PVBoolean *pv =  static_cast<PVBoolean*>(pvScalar);
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
        case pvLong: {
            int64 value = convert->toLong(pvScalar);
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
            String value = convert->toString(pvScalar);
            return Py_BuildValue("s",value.c_str());
        }
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *getScalarArrayValue(PVScalarArray *pvScalarArray)
{
    ScalarType scalarType = pvScalarArray->getScalarArray()->getElementType();
    switch(scalarType) {
        case pvBoolean: {
            PVBooleanArray *pvArray = static_cast<PVBooleanArray *>(pvScalarArray);
            BooleanArrayData arrayData;
            int num = pvArray->get(0,pvArray->getLength(),&arrayData);
            BooleanArray data = arrayData.data;
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = (data[i] ? 1 : 0);
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvByte: {
            PVByteArray *pvArray = static_cast<PVByteArray *>(pvScalarArray);
            ByteArrayData arrayData;
            int8 num = pvArray->get(0,pvArray->getLength(),&arrayData);
            ByteArray data = arrayData.data;
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = data[i];
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvShort: {
            PVShortArray *pvArray = static_cast<PVShortArray *>(pvScalarArray);
            ShortArrayData arrayData;
            int num = pvArray->get(0,pvArray->getLength(),&arrayData);
            ShortArray data = arrayData.data;
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = data[i];
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvInt: {
            PVIntArray *pvArray = static_cast<PVIntArray *>(pvScalarArray);
            IntArrayData arrayData;
            int num = pvArray->get(0,pvArray->getLength(),&arrayData);
            IntArray data = arrayData.data;
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("i",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvLong: {
            PVLongArray *pvArray = static_cast<PVLongArray *>(pvScalarArray);
            LongArrayData arrayData;
            int num = pvArray->get(0,pvArray->getLength(),&arrayData);
            LongArray data = arrayData.data;
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("k",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvFloat: {
            PVFloatArray *pvArray = static_cast<PVFloatArray *>(pvScalarArray);
            FloatArrayData arrayData;
            int num = pvArray->get(0,pvArray->getLength(),&arrayData);
            FloatArray data = arrayData.data;
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("f",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvDouble: {
            PVDoubleArray *pvArray = static_cast<PVDoubleArray *>(pvScalarArray);
            DoubleArrayData arrayData;
            int num = pvArray->get(0,pvArray->getLength(),&arrayData);
            DoubleArray data = arrayData.data;
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("d",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvString: {
            PVStringArray *pvArray = static_cast<PVStringArray *>(pvScalarArray);
            StringArrayData arrayData;
            int num = pvArray->get(0,pvArray->getLength(),&arrayData);
            String *data = arrayData.data;
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

static PyObject *getStructureValue(PVStructure *pvStructure);
static PyObject *getStructureArrayValue(PVStructureArray *pvStructureArray)
{
    int num = pvStructureArray->getLength();
    PyObject *result = PyTuple_New(num);
    StructureArrayData structureArrayData = StructureArrayData();
    pvStructureArray->get(0, num,&structureArrayData);
    for(int i=0; i<num; i++) {
        PVStructure *pvStructure = structureArrayData.data[i];
        PVFieldPtrArray pvFields = pvStructure->getPVFields();
        StructureConstPtr structure = pvStructure->getStructure();
        int n = structure->getNumberFields();
        PyObject *fieldObj = PyTuple_New(n);
        for(int j=0; j<n; j++) {
            FieldConstPtr field = pvFields[j]->getField();
            switch(field->getType()) {
                case scalar: {
                    PVScalar *xxx =
                         static_cast<PVScalar *>(pvFields[j]);
                    PyObject *yyy = getScalarValue(xxx);
                    PyTuple_SetItem(fieldObj,j,yyy);
                    break;
                }
                case scalarArray: {
                    PVScalarArray *xxx =
                         static_cast<PVScalarArray *>(pvFields[j]);
                    PyObject *yyy = getScalarArrayValue(xxx);
                    PyTuple_SetItem(fieldObj,j,yyy);
                    break;
                }
                case epics::pvData::structure: {
                    PVStructure *xxx =
                         static_cast<PVStructure *>(pvFields[j]);
                    PyObject *yyy = getStructureValue(xxx);
                    PyTuple_SetItem(fieldObj,j,yyy);
                    break;
                }
                case structureArray: {
                    PVStructureArray *xxx =
                         static_cast<PVStructureArray *>(pvFields[j]);
                    PyObject *yyy = getStructureArrayValue(xxx);
                    PyTuple_SetItem(fieldObj,j,yyy);
                    break;
                }
            }
        }
        PyObject *xxx = Py_BuildValue("O",fieldObj);
        PyTuple_SetItem(result, i, xxx);
        
    }
    return result;
}

static PyObject *getStructureValue(PVStructure *pvStructure)
{
    PVFieldPtrArray pvFields = pvStructure->getPVFields();
    StructureConstPtr structure = pvStructure->getStructure();
    int n = structure->getNumberFields();
    PyObject *fieldObj = PyTuple_New(n);
    for(int j=0; j<n; j++) {
        FieldConstPtr field = pvFields[j]->getField();
        switch(field->getType()) {
            case scalar: {
                PVScalar *xxx =
                     static_cast<PVScalar *>(pvFields[j]);
                PyObject *yyy = getScalarValue(xxx);
                PyTuple_SetItem(fieldObj,j,yyy);
            }
            case scalarArray: {
                PVScalarArray *xxx =
                     static_cast<PVScalarArray *>(pvFields[j]);
                PyObject *yyy = getScalarArrayValue(xxx);
                PyTuple_SetItem(fieldObj,j,yyy);
            }
            case epics::pvData::structure: {
                break;
            }
            case structureArray: {
                PVStructureArray *xxx =
                     static_cast<PVStructureArray *>(pvFields[j]);
                PyObject *yyy = getStructureArrayValue(xxx);
                PyTuple_SetItem(fieldObj,j,yyy);
            }
        }
    }
    return fieldObj;
}

static PyObject * _getValue(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    int index = 0;
    if(!PyArg_ParseTuple(args,"Oi:nttablePy",
        &pcapsule,
        &index))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    PVFieldPtr pvField =  pvt->nttable->getPVField(index);
    Type type = pvField->getField()->getType();
    if(type==scalarArray) {
        PVScalarArray *pvScalarArray = static_cast<PVScalarArray *>(pvField);
        return getScalarArrayValue(pvScalarArray);
    }
    if(type==structureArray) {
        PVStructureArray *pvStructureArray = static_cast<PVStructureArray *>(pvField);
        return getStructureArrayValue(pvStructureArray);
    }
    Py_INCREF(Py_None);
    return Py_None;
}


static char _initDoc[] = "_init nttablePy.";
static char _destroyDoc[] = "_destroy nttablePy.";
static char _strDoc[] = "_str  nttablePy.";
static char _getNTTablePyDoc[] = "_getNTTablePy nttablePy.";
static char _getTimeStampDoc[] = "_getTimeStamp nttablePy.";
static char _getAlarmDoc[] = "_getAlarm nttablePy.";
static char _getNumberValuesDoc[] = "_getNumberValues nttablePy.";
static char _getLabelDoc[] = "_getLabel nttablePy.";
static char _getValueDoc[] = "_getValue nttablePy.";

static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_str",_str,METH_VARARGS,_strDoc},
    {"_getNTTablePy",_getNTTablePy,METH_VARARGS,_getNTTablePyDoc},
    {"_getTimeStamp",_getTimeStamp,METH_VARARGS,_getTimeStampDoc},
    {"_getAlarm",_getAlarm,METH_VARARGS,_getAlarmDoc},
    {"_getNumberValues",_getNumberValues,METH_VARARGS,_getNumberValuesDoc},
    {"_getLabel",_getLabel,METH_VARARGS,_getLabelDoc},
    {"_getValue",_getValue,METH_VARARGS,_getValueDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initnttablePy(void)
{
    PyObject * m = Py_InitModule("nttablePy",methods);
    if(m==NULL) printf("initnttablePy failed\n");
}

}}


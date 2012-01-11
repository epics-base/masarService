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
        PVStructure::shared_pointer ntnameValue);
    ~NTNameValuePvt();
    void destroy();
    PyObject *get(){return pyObject;}
public:
    PVStructure::shared_pointer ntnameValue;
    PyObject *pyObject;
};

NTNameValuePvt::NTNameValuePvt(
    PVStructure::shared_pointer arg)
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
    NTNameValue ntnamevalue(pvnamevalue);
    NTNameValuePvt *pvt = new NTNameValuePvt(pvnamevalue);
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
    PVStructure::shared_pointer pvnamevalue
        = NTNameValue::create(true,false,false);
    NTNameValue ntnamevalue(pvnamevalue);
    PVString * pvfunction = ntnamevalue.getFunction();
    PVStringArray *pvnames = ntnamevalue.getNames();
    PVStringArray *pvvalues = ntnamevalue.getValues();
    pvnames->put(0,n,names,0);
    pvvalues->put(0,n,values,0);
    pvfunction->put(function);
    NTNameValuePvt *pvt = new NTNameValuePvt(pvnamevalue);
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
    pvt->ntnameValue->toString(&buffer);
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

static char _init1Doc[] = "_init1 ntnamevaluePy.";
static char _initDoc[] = "_init ntnamevaluePy.";
static char _destroyDoc[] = "_destroy ntnamevaluePy.";
static char _strDoc[] = "_str ntnamevaluePy.";
static char _getNTNameValuePyDoc[] = "_getNTNameValuePy ntnamevaluePy.";

static PyMethodDef methods[] = {
    {"_init1",_init1,METH_VARARGS,_init1Doc},
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"__str__",_str,METH_VARARGS,_strDoc},
    {"_getNTNameValuePy",_getNTNameValuePy,METH_VARARGS,_getNTNameValuePyDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initntnameValuePy(void)
{
    PyObject * m = Py_InitModule("ntnameValuePy",methods);
    if(m==NULL) printf("initntnameValuePy failed\n");
}

}}


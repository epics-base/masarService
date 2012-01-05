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


#include <pv/nt.h>
#include <stdexcept>

using namespace epics::pvData;

namespace epics { namespace pvAccess {

class NTTablePvt {
public:
    NTTablePvt(
        PVStructure::shared_pointer nttable);
    ~NTTablePvt();
    void destroy();
public:
    PVStructure::shared_pointer nttable;
};

NTTablePvt::NTTablePvt(
    PVStructure::shared_pointer arg)
: nttable(arg)
{
}

NTTablePvt::~NTTablePvt()
{
}

void NTTablePvt::destroy()
{
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
    NTTablePvt *pvt = new NTTablePvt(*pv);
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
    pvt->nttable->toString(&buffer);
    return Py_BuildValue("s",buffer.c_str());
}


static char _initDoc[] = "initialize nttablePy.";
static char _destroyDoc[] = "destroy nttablePy.";
static char _strDoc[] = "str nttablePy.";

static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"__str__",_str,METH_VARARGS,_strDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initnttablePy(void)
{
    PyObject * m = Py_InitModule("nttablePy",methods);
    if(m==NULL) printf("initnttablePy failed\n");
}

}}


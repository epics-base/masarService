/*
 *Copyright - See the COPYRIGHT that is included with this distribution.
 *EPICS pvServiceCPP is distributed subject to a Software License Agreement found
 *in file LICENSE that is included with this distribution.
 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>

#include <epicsExit.h>

namespace {

PyObject* pyepicsExitCallAtExits(PyObject *unused)
{
    epicsExitCallAtExits();
    Py_RETURN_NONE;
}

void pyepicsexit()
{
    epicsExitCallAtExits();
}

PyObject* pyregisterExit(PyObject *unused)
{
    Py_AtExit(&pyepicsexit);
    Py_RETURN_NONE;
}


static PyMethodDef methods[] = {
    {"epicsExitCallAtExits", (PyCFunction)&pyepicsExitCallAtExits, METH_NOARGS, NULL},
    {"registerExit", (PyCFunction)&pyregisterExit, METH_NOARGS, NULL},
    {NULL,NULL,0,NULL}
};

} // namespace

PyMODINIT_FUNC initepicsExit(void)
{
    Py_InitModule("epicsExit",methods);
}

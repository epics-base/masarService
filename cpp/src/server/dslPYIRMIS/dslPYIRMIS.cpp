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

namespace epics { namespace masar { 

using namespace epics::pvData;

class DSL_IRMIS :
    public DSL,
    public std::tr1::enable_shared_from_this<DSL_IRMIS>
{
public:
    POINTER_DEFINITIONS(DSL_IRMIS);
    DSL_IRMIS();
    virtual ~DSL_IRMIS();
    virtual void destroy();
    virtual PVStructure::shared_pointer request(
         PVStructure::shared_pointer const & pvArgument);
    bool init();
private:
    DSL_IRMIS::shared_pointer getPtrSelf()
    {
        return shared_from_this();
    }
    PyObject * prequest;
};

DSL_IRMIS::DSL_IRMIS()
: prequest(0)
{
   PyThreadState *py_tstate = NULL;
   Py_Initialize();
   PyEval_InitThreads();
   py_tstate = PyGILState_GetThisThreadState();
   PyEval_ReleaseThread(py_tstate);
}

DSL_IRMIS::~DSL_IRMIS()
{
    PyGILState_STATE gstate = PyGILState_Ensure();
        if(prequest!=0) Py_XDECREF(prequest);
    PyGILState_Release(gstate);
    PyGILState_Ensure();
    Py_Finalize();
}

bool DSL_IRMIS::init()
{
    PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject * module = PyImport_ImportModule("dslPYIRMIS");
        if(module==0) {
            String message("dslPYIRMIS");
            message += " does not exist or is not a python module";
            printf("DSL_IRMIS::init %s\n",message.c_str());
            return false;
        }
        PyObject *pclass = PyObject_GetAttrString(module, "DSL");
        if(pclass==0) {
            String message("class DSL");
            message += " does not exist";
            printf("DSL_IRMIS::init %s\n",message.c_str());
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
            printf("DSL_IRMIS::init %s\n",message.c_str());
            Py_XDECREF(pclass);
            Py_XDECREF(module);
            return false;
        }
        prequest =  PyObject_GetAttrString(pinstance, "request");
        if(prequest==0) {
            String message("DSL::request");
            message += " could not attach to method";
            printf("DSL_IRMIS::init %s\n",message.c_str());
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

void DSL_IRMIS::destroy() {}

PVStructure::shared_pointer DSL_IRMIS::request(
             PVStructure::shared_pointer const & pvArgument)
{
    char * xxx = 0;
    const char *arg1 = "this is a test";
    PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject * arg = Py_BuildValue("(s)",arg1);
        PyObject *result = PyEval_CallObject(prequest,arg);
         Py_XDECREF(arg);
        if(result==0) {
            printf("DSL::request failed\n");
        } else {
            if (!PyArg_Parse(result, "s", &xxx)) {
                printf("DSL::request did not return string\n");
            } 
            Py_XDECREF(result);
        }
    PyGILState_Release(gstate);
    printf("DSL::request returned %s\n",xxx);
    return pvArgument;
}

DSL::shared_pointer createDSL_IRMIS()
{
   DSL_IRMIS *dsl = new DSL_IRMIS();
   if(!dsl->init()) {
        delete dsl;
        return DSL_IRMIS::shared_pointer();
        
   }
   return DSL_IRMIS::shared_pointer(dsl);
}

}}

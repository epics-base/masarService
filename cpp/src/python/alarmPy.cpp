/*alarmPy.cpp */
/*
 *Copyright - See the COPYRIGHT that is included with this distribution.
 *EPICS pvServiceCPP is distributed subject to a Software License Agreement found
 *in file LICENSE that is included with this distribution.
 */
/* Author:  Marty Kraimer Date: 2011.12 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>


#include <pv/pvData.h>
#include <pv/alarm.h>
#include <pv/pvAlarm.h>
#include <stdexcept>

namespace epics { namespace pvData {

class AlarmPvt {
public:
    AlarmPvt();
    ~AlarmPvt();
    void destroy();
    PyObject *get(){return pyObject;}
public:
    Alarm alarm;
    PyObject *pyObject;
};

AlarmPvt::AlarmPvt()
{
    pyObject = PyCapsule_New(&alarm,"alarm",0);
    Py_INCREF(pyObject);
}

AlarmPvt::~AlarmPvt()
{
}

void AlarmPvt::destroy()
{
    Py_DECREF(pyObject);
}


static PyObject * _init(PyObject *willbenull, PyObject *args)
{
    AlarmPvt *pvt = new AlarmPvt();
    PyObject *pyObject = PyCapsule_New(pvt,"alarmPvt",0);
    return pyObject;
}

static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:alarmPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"alarmPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    AlarmPvt *pvt = static_cast<AlarmPvt *>(pvoid);
    pvt->destroy();
    delete pvt;
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject * _str(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:alarmPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"alarmPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    AlarmPvt *pvt = static_cast<AlarmPvt *>(pvoid);
    char buffer[256];
    String message = pvt->alarm.getMessage();
    String severity = AlarmSeverityFunc::getSeverityNames()[pvt->alarm.getSeverity()];
    String status = AlarmStatusFunc::getStatusNames()[pvt->alarm.getStatus()];

    sprintf(buffer,"message %s severity %s status %s",
        message.c_str(),severity.c_str(),status.c_str());
    return Py_BuildValue("s",buffer);
}

static PyObject * _getAlarmPy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:alarmPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"alarmPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    AlarmPvt *pvt = static_cast<AlarmPvt *>(pvoid);
    return pvt->get();
}

static PyObject * _getMessage(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:alarmPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"alarmPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    AlarmPvt *pvt = static_cast<AlarmPvt *>(pvoid);
    return Py_BuildValue("s",pvt->alarm.getMessage().c_str());
}

static PyObject * _setMessage(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    char *buffer;
    if(!PyArg_ParseTuple(args,"Os:alarmPy",
        &pcapsule,
        &buffer))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,string)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"alarmPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    AlarmPvt *pvt = static_cast<AlarmPvt *>(pvoid);
    pvt->alarm.setMessage(buffer);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getSeverity(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:alarmPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"alarmPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    AlarmPvt *pvt = static_cast<AlarmPvt *>(pvoid);
    String severity = AlarmSeverityFunc::getSeverityNames()[pvt->alarm.getSeverity()];
    return Py_BuildValue("s",severity.c_str());
}

static PyObject * _setSeverity(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    char *buffer;
    if(!PyArg_ParseTuple(args,"Os:alarmPy",
        &pcapsule,
        &buffer))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,string)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"alarmPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    int nchoices = severityCount;
    AlarmPvt *pvt = static_cast<AlarmPvt *>(pvoid);
    for(int i=0;i<nchoices; i++) {
        String choice = AlarmSeverityFunc::getSeverityNames()[i];
        if(choice.compare(buffer)==0) {
            pvt->alarm.setSeverity(AlarmSeverityFunc::getSeverity(i));
            Py_INCREF(Py_None);
            return Py_None;
        }
    }
    PyErr_SetString(PyExc_ValueError,"unknown severity");
    return NULL;
}

static PyObject * _getStatus(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:alarmPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"alarmPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    AlarmPvt *pvt = static_cast<AlarmPvt *>(pvoid);
    String severity = AlarmStatusFunc::getStatusNames()[pvt->alarm.getStatus()];
    return Py_BuildValue("s",severity.c_str());
}

static PyObject * _setStatus(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    char *buffer;
    if(!PyArg_ParseTuple(args,"Os:alarmPy",
        &pcapsule,
        &buffer))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,string)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"alarmPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    int nchoices = statusCount;
    AlarmPvt *pvt = static_cast<AlarmPvt *>(pvoid);
    for(int i=0;i<nchoices; i++) {
        String choice = AlarmStatusFunc::getStatusNames()[i];
        if(choice.compare(buffer)==0) {
            pvt->alarm.setStatus(AlarmStatusFunc::getStatus(i));
            Py_INCREF(Py_None);
            return Py_None;
        }
    }
    PyErr_SetString(PyExc_ValueError,"unknown status");
    return NULL;
}

static PyObject * _getSeverityChoices(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:alarmPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"alarmPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    AlarmPvt *pvt = static_cast<AlarmPvt *>(pvoid);
    StringArray choices = AlarmSeverityFunc::getSeverityNames();
    if(severityCount!=5) {
        throw std::logic_error("number severity choices not 5");
    }
    String severity = AlarmSeverityFunc::getSeverityNames()[pvt->alarm.getSeverity()];
    return Py_BuildValue(
        "(s,s,s,s,s)",
        choices[0].c_str(),
        choices[1].c_str(),
        choices[2].c_str(),
        choices[3].c_str(),
        choices[4].c_str());
}

static PyObject * _getStatusChoices(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:alarmPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"alarmPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    AlarmPvt *pvt = static_cast<AlarmPvt *>(pvoid);
    StringArray choices = AlarmStatusFunc::getStatusNames();
    if(statusCount!=8) {
        throw std::logic_error("number status choices not 8");
    }
    String severity = AlarmStatusFunc::getStatusNames()[pvt->alarm.getStatus()];
    return Py_BuildValue(
        "(s,s,s,s,s,s,s,s)",
        choices[0].c_str(),
        choices[1].c_str(),
        choices[2].c_str(),
        choices[3].c_str(),
        choices[4].c_str(),
        choices[5].c_str(),
        choices[6].c_str(),
        choices[7].c_str());
}

static char _initDoc[] = "_init alarmPy.";
static char _destroyDoc[] = "_destroy alarmPy.";
static char _strDoc[] = "_str alarmPy.";
static char _getAlarmPyDoc[] = "_getAlarmPy.";
static char _getMessageDoc[] = "_getMessage alarmPy.";
static char _setMessageDoc[] = "_setMessage alarmPy.";
static char _getSeverityDoc[] = "_getSeverity alarmPy.";
static char _setSeverityDoc[] = "_setSeverity alarmPy.";
static char _getStatusDoc[] = "_getStatus alarmPy.";
static char _setStatusDoc[] = "_setStatus alarmPy.";
static char _getSeverityChoicesDoc[] = "_getSeverityChoices alarmPy.";
static char _getStatusChoicesDoc[] = "_getStatusChoices alarmPy.";

static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_str",_str,METH_VARARGS,_strDoc},
    {"_getAlarmPy",_getAlarmPy,METH_VARARGS,_getAlarmPyDoc},
    {"_getMessage",_getMessage,METH_VARARGS,_getMessageDoc},
    {"_setMessage",_setMessage,METH_VARARGS,_setMessageDoc},
    {"_getSeverity",_getSeverity,METH_VARARGS,_getSeverityDoc},
    {"_setSeverity",_setSeverity,METH_VARARGS,_setSeverityDoc},
    {"_getStatus",_getStatus,METH_VARARGS,_getStatusDoc},
    {"_setStatus",_setStatus,METH_VARARGS,_setStatusDoc},
    {"_getSeverityChoices",_getSeverityChoices,METH_VARARGS,_getSeverityChoicesDoc},
    {"_getStatusChoices",_getStatusChoices,METH_VARARGS,_getStatusChoicesDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initalarmPy(void)
{
    PyObject * m = Py_InitModule("alarmPy",methods);
    if(m==NULL) printf("initalarmPy failed\n");
}

}}


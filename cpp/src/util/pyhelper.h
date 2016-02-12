#ifndef PYHELPER_H
#define PYHELPER_H

#include <stdexcept>

#include <Python.h>

// Throw this to indicate that a python exception is active
struct python_exception : public std::runtime_error
{
    python_exception() : std::runtime_error("python") {}
    virtual ~python_exception() throw() {}
};

//! helper to indicate that the wrapped PyObject is a borrowed referenced for the caller
struct borrowed {
    PyObject *o;
    explicit borrowed(PyObject *o) :o(o) {}
};

//! Smart pointer for python objects
struct PyObj
{
    PyObject *obj;

    PyObj() :obj(NULL) {}

    //! Assumes caller already has a reference to this object
    //! if o==NULL then assume a python exception has been raised
    explicit PyObj(PyObject *o) :obj(o)
    {
        if(!obj)
            throw python_exception();
    }
    //! Assumes caller does not have a reference to this object
    //! if o==NULL then assume a python exception has been raised
    explicit PyObj(const borrowed& b) :obj(b.o)
    {
        if(!obj)
            throw python_exception();
        Py_INCREF(obj);
    }

    ~PyObj()
    {
        Py_XDECREF(obj);
    }

    //! Explicitly fetch the underlying PyObject*
    PyObject *get() {return obj;}
    //! Implicitly fetch the underlying PyObject*
    //operator PyObject*() { return obj; }

    //! Give up control of this reference (no decrement)
    PyObject *release() {
        PyObject *ret=obj;
        obj = NULL;
        return ret;
    }
    //! Switch object being pointed to.
    //! Any existing reference is decremented
    //! if o==NULL then simply clear the reference
    void reset(PyObject *o = 0)
    {
        Py_XDECREF(obj);
        obj = o;
    }

    //! if o==NULL then assume a python exception has been raised
    void reset(const borrowed& b)
    {
        if(!b.o)
            throw python_exception();
        Py_INCREF(b.o);
        Py_XDECREF(obj);
        obj = b.o;
    }

    PyObject& operator*() { return *obj; }
    PyObject* operator->() { return obj; }

private:
    PyObj(const PyObj&);
    PyObj& operator=(const PyObj&);
};

//! Scoped GIL locker
struct PyLockGIL
{
    PyGILState_STATE state;
    PyLockGIL() :state(PyGILState_Ensure()) {}
    ~PyLockGIL() {
        PyGILState_Release(state);
    }
private:
    PyLockGIL(const PyLockGIL&);
    PyLockGIL& operator=(const PyLockGIL&);
};

//! Scoped GIL unlocker
struct PyUnlockGIL
{
    PyThreadState *state;
    PyUnlockGIL() :state(PyEval_SaveThread()) {}
    ~PyUnlockGIL() { PyEval_RestoreThread(state); }
};

#define EXECTOPY(klass, PYEXC) catch(klass& e) { PyErr_SetString(PyExc_##PYEXC, e.what()); }

#endif /* PYHELPER_H */

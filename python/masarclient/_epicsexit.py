#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author : Guobao Shen   2014.09

"""
This function should only be called right before Python exit.
It will make sure epicsExitCallAtExits() be called if there is any registered.
Python will crash without this call but there is any registered.
 
epicsExit() will completely shut down the EPICS library silently. It should be called after Python
exit handler if there is any epics related stuff reqistered as Python atexit function to make
sure the right clean up order, for example is cothread. 
Otherwise, it could cause an exception if allowing normal Python exist processing after calling 
epicsExit().

Planning: it would be better to call epicsExit() function instead of epicsExitCallAtExits(). 
"""

import os
import platform
import ctypes

# Figure out the libraries that need to be loaded and the loading method.
load_library = ctypes.cdll.LoadLibrary
system = platform.system()
if system == 'Windows':
    load_library = ctypes.windll.LoadLibrary
    lib_files = ['Com.dll', 'ca.dll']
elif system == 'Darwin':
    lib_files = ['libCom.dylib']
else:
    lib_files = ['libCom.so']

epics_base = os.environ['EPICS_BASE']

system_map = {
        ('Linux',   '32bit'):   'linux-x86',
        ('Linux',   '64bit'):   'linux-x86_64',
        ('Darwin',  '32bit'):   'darwin-x86',
        ('Darwin',  '64bit'):   'darwin-x86',
        ('Windows', '32bit'):   'win32-x86',
        ('Windows', '64bit'):   'windows-x64',  # Not quite yet!
    }
bits = platform.architecture()[0]
epics_host_arch = system_map[(system, bits)]

libpath = os.path.join(epics_base, 'lib', epics_host_arch)
for lib in lib_files:
    libCom = load_library("/".join((libpath, lib)))

#libmiscIoc = ctypes.CDLL("path/to/libmiscIoc.so")
epicsExit = libCom.epicsExit
epicsExitCallAtExits = libCom.epicsExitCallAtExits

# generateSOLinks.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07
#
# This creates a xxxPy.so soft link for each xxxPy.cpp file.
# Each xxxPt.cpp file is a set of C++ python methods for a python class in a xxx.py file
import os
import sys
import subprocess,shlex

hostArch = os.getenv("EPICS_HOST_ARCH")
if not hostArch:
    print ("EPICS_HOST_ARCH is not setted.")
    if sys.version_info[:2] > (3,0):
        hostArch = input ('Please specify EPICS_HOST_ARCH:')
    else:
        hostArch = raw_input('Please specify EPICS_HOST_ARCH:')

# check synamic library format
# set Linux dynamic library as default
dylib = '.so'
if hostArch in ['darwin-x86', 'darwin-ppc', 'darwin-ppcx86']:
    dylib = '.dylib'
elif hostArch in ['win32-x86', 'win32-x86-cygwin', 'windows-x64']:
    # need to check with 'win32-x86-mingw'
    dylib = '.lib'

libDir = "../../lib/" + hostArch
fileList = os.listdir(libDir)
soLib = None
for element in fileList :
    if element.endswith("masarPy" + dylib) :
        soLib = element
        break
if soLib==None :
    raise RuntimeError("did not find dynamic library")
soLib = "../../lib/" + hostArch + "/" + soLib


fileList = os.listdir(".")

outList = ["channelRPCPy","ntnameValuePy","nttablePy","alarmPy","timeStampPy"]
soList = []
for element in outList :
    value = "/bin/ln -s " + soLib
    value += " " + element + '.so'
    soList.append(value)
for link in soList :
    args = shlex.split(link)
    result = subprocess.check_call(args)

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
import subprocess,shlex
hostArch = os.environ["EPICS_HOST_ARCH"]
libDir = "../../lib/" + hostArch
fileList = os.listdir(libDir)
soLib = None
for element in fileList :
    if element.endswith("masarPy.so") :
        soLib = element
        break
if soLib==None :
    raise RuntimeError("did not find .so library")
soLib = "../../lib/" + hostArch + "/" + soLib



fileList = os.listdir(".")

outList = ["channelRPCPy","ntnameValuePy","nttablePy"]
soList = []
for element in outList :
    value = "/bin/ln -s " + soLib
    value += " " + element + ".so"
    soList.append(value)
for link in soList :
    args = shlex.split(link)
    result = subprocess.check_call(args)

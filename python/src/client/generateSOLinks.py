# generateSOLinks.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07
#
# This creates a masarPy.so soft link for the masar.py file.
import os
import subprocess,shlex
hostArch = os.environ["EPICS_HOST_ARCH"]
value = "/bin/ln -s ../../bin/" + hostArch + "/masarServiceServer.so masarPy.so"
args = shlex.split(value)
result = subprocess.check_call(args)

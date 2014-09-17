# testControl.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07
from masarclient.control import Control as Control

control = Control()
print control
control.setLimitLow(-10.0)
control.setLimitHigh(10.0)
control.setMinStep(1.0)
print control
print "all done"


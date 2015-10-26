# testDisplay.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07
from masarclient.display import Display as Display

display = Display()
print display
display.setLimitLow(-10.0)
display.setLimitHigh(10.0)
display.setDescription("this is description")
display.setFormat("%f")
display.setUnits("volts")
print display
print "all done"


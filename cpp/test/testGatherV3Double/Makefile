TOP=../..

include $(TOP)/configure/CONFIG

PROD_HOST += gatherV3DoubleTest
gatherV3DoubleTest_SRCS += gatherV3DoubleTest.cpp
gatherV3DoubleTest_LIBS += nt pvIOC pvAccess pvData ca Com
gatherV3DoubleTest_LIBS += masarServer masarClient
gatherV3DoubleTest_LIBS += $(PYTHON)

PROD_HOST += gatherV3DoubleExample
gatherV3DoubleExample_SRCS += gatherV3DoubleExample.cpp
gatherV3DoubleExample_LIBS += nt pvIOC pvAccess pvData ca Com
gatherV3DoubleExample_LIBS += masarServer masarClient
gatherV3DoubleExample_LIBS += $(PYTHON)

$(PYTHON)_DIR = $(PYTHON_BASE)/lib/$(PYTHON)/config

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE


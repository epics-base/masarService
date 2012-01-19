TOP=../..

include $(TOP)/configure/CONFIG

PROD_HOST += gatherV3ScalarDataTest
gatherV3ScalarDataTest_SRCS += gatherV3ScalarDataTest.cpp
gatherV3ScalarDataTest_LIBS += nt pvIOC pvAccess pvData ca Com
gatherV3ScalarDataTest_LIBS += masarServer masarClient
gatherV3ScalarDataTest_LIBS += $(PYTHON)

PROD_HOST += gatherV3ScalarDataExample
gatherV3ScalarDataExample_SRCS += gatherV3ScalarDataExample.cpp
gatherV3ScalarDataExample_LIBS += nt pvIOC pvAccess pvData ca Com
gatherV3ScalarDataExample_LIBS += masarServer masarClient
gatherV3ScalarDataExample_LIBS += $(PYTHON)

$(PYTHON)_DIR = $(PYTHON_BASE)/lib/$(PYTHON)/config

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE


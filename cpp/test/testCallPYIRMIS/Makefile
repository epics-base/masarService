TOP=../..

include $(TOP)/configure/CONFIG

PROD_HOST += testCallPYIRMIS
testCallPYIRMIS_SRCS += testCallPYIRMIS.cpp
testCallPYIRMIS_LIBS += nt pvIOC pvAccess pvData Com masarServer
testCallPYIRMIS_LIBS += $(PYTHON)

$(PYTHON)_DIR = $(PYTHON_BASE)/lib/$(PYTHON)/config

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE


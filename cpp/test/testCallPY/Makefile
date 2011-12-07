TOP=../..

include $(TOP)/configure/CONFIG

PROD_HOST += testCallPY
testCallPY_SRCS += testCallPY.cpp
testCallPY_LIBS += nt pvIOC pvAccess pvData Com masarServer
testCallPY_LIBS += $(PYTHON)

$(PYTHON)_DIR = $(PYTHON_BASE)/lib/$(PYTHON)/config

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE


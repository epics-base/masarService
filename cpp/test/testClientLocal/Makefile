TOP=../..

include $(TOP)/configure/CONFIG

PROD_HOST += clientLocalTest
clientLocalTest_SRCS += clientLocalTest.cpp
clientLocalTest_LIBS += nt pvIOC pvAccess pvData Com masarServer
clientLocalTest_LIBS += $(PYTHON)

$(PYTHON)_DIR = $(PYTHON_BASE)/lib/$(PYTHON)/config

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE


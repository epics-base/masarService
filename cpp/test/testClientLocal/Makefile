TOP=../..

include $(TOP)/configure/CONFIG

PROD_HOST += clientLocalTest
clientLocalTest_SRCS += clientLocalTest.cpp
clientLocalTest_LIBS += nt pvIOC pvAccess pvData Com masarServer masarClient
clientLocalTest_LIBS += $(PYTHON)

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE


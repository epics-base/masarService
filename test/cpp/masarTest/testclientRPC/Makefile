TOP=../..

include $(TOP)/configure/CONFIG

PROD_HOST += testclientRPC
testclientRPC_SRCS += testclientRPC.cpp
testclientRPC_LIBS += gather nt pvAccess pvData Com
testclientRPC_LIBS += $(PYTHON)

PROD_HOST += testmc
testmc_SRCS += mc.cpp
testmc_LIBS += gather nt pvAccess pvData Com
testmc_LIBS += $(PYTHON)

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE


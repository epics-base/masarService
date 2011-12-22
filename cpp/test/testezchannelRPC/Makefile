TOP=../..

include $(TOP)/configure/CONFIG

PROD_HOST += testezchannelRPC
testezchannelRPC_SRCS += testezchannelRPC.cpp
testezchannelRPC_LIBS += nt pvIOC pvAccess pvData Com masarClient
testezchannelRPC_LIBS += $(PYTHON)

$(PYTHON)_DIR = $(PYTHON_BASE)/lib/$(PYTHON)/config

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE


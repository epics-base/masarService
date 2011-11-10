TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}

PYIRMIS = $(TOP)/src/dslPYIRMIS

SRC_DIRS += $(PYIRMIS)/dsl
#INC += xxx.h
#LIBSRCS += dslPy.cpp

#SRC_DIRS += $(CLIENT)/??? Must call python code
#INC += xxx.h
#LIBSRCS += maserPVA.cpp


#LIBRARY = dslPYIRMIS

dslPYIRMIS_LIBS += pvData Com

include $(TOP)/configure/RULES


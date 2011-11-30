TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}

PYIRMIS = $(TOP)/src/dslPYIRMIS

SRC_DIRS += $(PYIRMIS)/dsl
LIBSRCS += dsl.cpp

LIBRARY = dslPYIRMIS

dslPYIRMIS_LIBS += pvData Com

dslPYIRMIS_LIBS += $(PYTHON)
# Location of the python libraries
$(PYTHON)_DIR = $(PYTHON_BASE)/lib/$(PYTHON)/config

include $(TOP)/configure/RULES


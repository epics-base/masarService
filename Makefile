#Makefile at top of application tree
TOP = ./cpp
include $(TOP)/configure/CONFIG

DIRS += cpp
DIRS += test/cpp
test/cpp_DEPEND_DIRS = cpp

include $(TOP)/configure/RULES_TOP

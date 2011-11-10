#Makefile at top of application tree
TOP = .
include $(TOP)/configure/CONFIG

DIRS += configure

DIRS += src
src_DEPEND_DIRS = configure

config_DEPEND_DIRS = src

DIRS += test
test_DEPEND_DIRS = configure

include $(TOP)/configure/RULES_TOP



#Makefile at top of application tree
TOP = ..
include $(TOP)/configure/CONFIG

DIRS += util

DIRS += client

DIRS += server
server_DEPEND_DIRS = util client

DIRS += python
python_DEPEND_DIRS = client

DIRS += masarServiceRun
masarServiceRun_DEPEND_DIRS = client server

include $(TOP)/configure/RULES_DIRS



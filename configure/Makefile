TOP=..

include $(TOP)/configure/CONFIG

ifneq ($(PY_VER),)
$(error Set PYTHON= to select interpreter executable)
endif
PYTHON ?= python

TARGETS = $(CONFIG_TARGETS)

ifdef T_A
CONFIGS = CONFIG_PY RULES_PY os/CONFIG_PY.Common.$(T_A)
endif

CONFIGS += $(subst ../,,$(wildcard $(CONFIG_INSTALLS)))

include $(TOP)/configure/RULES

os/CONFIG_PY.Common.$(T_A): $(TOP)/makehelper.py Makefile
	$(PYTHON) $< $@

ifdef BASE_3_15
realclean: py_clean
else
realclean:: py_clean
endif

py_clean:
	$(RMDIR) os

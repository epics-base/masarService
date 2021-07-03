TOP = ..
include $(TOP)/configure/CONFIG
include $(TOP)/configure/CONFIG_PY

PY += masarclient/__init__.py
PY += masarclient/alarm.py
PY += masarclient/control.py
PY += masarclient/display.py
PY += masarclient/masarClient.py
PY += masarclient/ui/__init__.py
PY += masarclient/ui/authendlg.py
PY += masarclient/ui/commentdetail.py
PY += masarclient/ui/commentdlg.py
PY += masarclient/ui/finddlg.py
PY += masarclient/ui/getmasarconfig.py
PY += masarclient/ui/gradualput.py
PY += masarclient/ui/masar.py
PY += masarclient/ui/masarRC_rc.py
PY += masarclient/ui/selectrefsnapshotdlg.py
PY += masarclient/ui/showarrayvaluedlg.py
PY += masarclient/ui/ui_commentdetail.py
PY += masarclient/ui/ui_commentdiag.py
PY += masarclient/ui/ui_masar.py
PY += masarclient/ui/verifysetpoint.py

PY += minimasar/__init__.py
PY += minimasar/db.py
PY += minimasar/convert.py
PY += minimasar/ops.py
PY += minimasar/server.py
PY += minimasar/client.py
PY += minimasar/gather/__init__.py
PY += minimasar/gather/sim.py
PY += minimasar/gather/ca.py
PY += minimasar/test/__init__.py
PY += minimasar/test/test_db.py
PY += minimasar/test/test_ops.py

# generated to remove
QTCLEANS += masarclient/ui/ui_commentdetail.py
QTCLEANS += masarclient/ui/ui_commentdiag.py
QTCLEANS += masarclient/ui/ui_masar.py
QTCLEANS += masarclient/ui/masarRC_rc.py

include $(TOP)/configure/RULES
include $(TOP)/configure/RULES_PY

ifneq (,$(T_A))
nose.%:
	[ -d "$(P4P)/python$(PY_LD_VER)/$(T_A)/p4p" ]
	PYTHONPATH="${PYTHONPATH}:$(abspath $(P4P))/python$(PY_LD_VER)/$(T_A):$(abspath $(TOP))/python$(PY_LD_VER)/$(T_A)" $(PYTHON) -m nose -P -v $* $(NOSEFLAGS)
endif

ui_%.py: ui_%.ui
	$(PYTHON) -c 'import PyQt4.uic.pyuic' -o $@ --from-imports $<

# pyrcc4 is not python code...
# So there is no recipe like:  python -c '...'
%_rc.py: %.qrc Makefile
	$(PYRCC) $(PYRCCFLAGS) -o $@ $<

ifndef T_A
ifdef BASE_3_15
realclean: qt_clean
else
realclean:: qt_clean
endif

qt_clean:
	$(RM) $(QTCLEANS)
endif

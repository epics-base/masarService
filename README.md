MASAR
=====

MASAR (MAchine Snapshot, Archiving, and Retrieve)

Dependencies
------------

Required dependencies

* [EPICS Base](http://www.aps.anl.gov/epics/)
* [PVDataCPP](http://epics-pvdata.sourceforge.net/)
* [PVAccessCPP](http://epics-pvdata.sourceforge.net/)
* [NormativeTypesCPP](http://epics-pvdata.sourceforge.net/)
* [pymongo](http://api.mongodb.org/python/)

Needed by Qt client UI

* [PyQt4](http://www.riverbankcomputing.co.uk/software/pyqt/)
* [cothread](http://controls.diamond.ac.uk/downloads/python/cothread/)

Needed by Server when using MongoDB storage backend
(not need for sqlite backend)

* [mongodb](http://www.mongodb.org)

```sh
# apt-get install epics-dev epics-pvd-dev epics-pva-dev epics-nt-dev \
  python-dev python-qt4 python-cothread
```

Building
--------

Copy ```RELEASE.local.example``` as ```RELEASE.local```
and fill in the paths for all EPICS module dependencies.
If using Debian packages then copy ```RELEASE.local.deb```
instead.

```sh
$ make
```

Running the daemon (SQLITE)
---------------------------

Setting Python path

```sh
export PYTHONPATH=$PWD/python2.7/linux-x86_64
```

adapt as necessary for different python version and EPICS target.

Setup demo configuration.

```sh
# one list of fake PV names
cat <<EOF >pvs-list1.txt
examplepv1
examplepv2
examplepv3
examplepv4
EOF
# Associate the list (aka group) with a MASAR config
cat <<EOF > db_config.txt
{
"pvgroups": [{ "name": "groupname1",
             "pvlist": "pvs-list1.txt",
             "description": "Booster magnet power supply set points"
           }],
"configs": [{"config_name": "exampleconfig",
             "config_desc": "BR ramping PS daily SCR setpoint",
             "system": "BR"
           }],
"pvg2config": [{ "config_name": "exampleconfig",
                 "pvgroups": ["groupname1"]
              }]
}
EOF
# Backend config
cat <<EOF > masarservice.conf
[Common]
database = sqlite
[sqlite]
database = ${PWD}/masar.db
EOF
export MASAR_SQLITE_DB=${PWD}/masar.db
# Initialize the DB
./masarConfigTool db_config.txt
```

To run the daemon

```sh
export MASAR_SQLITE_DB=${PWD}/masar.db
./bin/linux-*/masarServiceRun masarService
```

Running the Qt client
---------------------

```sh
./masar
```

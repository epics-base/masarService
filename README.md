MASAR
=====

MASAR (MAchine Snapshot, Archiving, and Retrieve)

Dependencies
------------

Required dependencies

* [EPICS Base](http://www.aps.anl.gov/epics/)
* [PVDataCPP](http://epics-pvdata.sourceforge.net/)
* [PVAccessCPP](http://epics-pvdata.sourceforge.net/)
* [p4p](https://mdavidsaver.github.io/p4p/)

Needed by Qt client UI

* [PyQt4](http://www.riverbankcomputing.co.uk/software/pyqt/)
* [cothread](http://controls.diamond.ac.uk/downloads/python/cothread/)


```sh
# apt-get install epics-dev epics-pvd-dev epics-pva-dev \
  python-dev python-qt4 python-cothread
```

Building
--------

Copy ```RELEASE.local.example``` as ```RELEASE.local```
and fill in the paths for all EPICS module dependencies.
If using Debian packages then copy ```RELEASE.local.deb```
instead.

Only EPICS Base is needed to build.

```sh
$ make
```

Running the daemon
------------------

Setting Python path.
The 'p4p' module must appear in the search path.
If '$P4P_DIR' is the source directory then:

```sh
export PYTHONPATH=$PWD/python2.7/linux-x86_64:$P4P_DIR/python2.7/linux-x86_64
```


Run automatic tests

```sh
$ nosetests minimasar
```

Run daemon in simulated client mode with in-memory database.

```sh
$ python -m minimasar.server --name masarService -L DEBUG ':memory:' -G sim
```

Run daemon in CA client mode and store in ```masar.db```.

```sh
$ python -m minimasar.server --name masarService -L DEBUG masar.db -G ca
```

Some testing can be done with the ```eget``` utility build with the pvAccessCPP module.

```sh
## Load pre-defined configuration
## On success, a new configid is printed
$ eget -s masarService:storeTestConfig -a configname=test -a desc=testing
## Read-back configuration
$ eget -s masarService:loadServiceConfig -a configid=<configid>

$ eget -s masarService:retrieveServiceConfigs

$ eget -s masarService:saveSnapshot -a configname=test
$ eget -s masarService:updateSnapshotEvent -a eventid=<eventid> -a user=me -a desc=snap

$ eget -s masarService:retrieveServiceEvents -a configid=<configid>

$ eget -s masarService:retrieveSnapshot -a eventid=eventid>

$ eget -s masarService:dumpDB
```

See [interface.md](interface.md) for a description of supported RPC calls.

Running the Qt client
---------------------

```sh
./masar
```

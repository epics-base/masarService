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
* [cothread](http://controls.diamond.ac.uk/downloads/python/cothread/)

Needed by Qt client UI

* [PyQt4](http://www.riverbankcomputing.co.uk/software/pyqt/)


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
The database file will be created if it does not exist.

```sh
$ python -m minimasar.server --name masarService -L DEBUG masar.db -G ca
```

Some testing can be done with the `pvcall` utility provided by the pvAccessCPP module.

```sh
## Load pre-defined configuration
## On success, a new configid is printed
$ pvcall masarService:storeTestConfig configname=test desc=testing
<undefined>                
config_idx config_name config_desc    config_create_date config_version status system
         1        test     testing "2021-07-03 16:47:19"              0 active       
## Read-back configuration
$ pvcall masarService:loadServiceConfig configid=<configid>

$ pvcall masarService:retrieveServiceConfigs

$ pvcall masarService:saveSnapshot configname=test
$ pvcall masarService:updateSnapshotEvent eventid=<eventid> user=me desc=snap

$ pvcall masarService:retrieveServiceEvents configid=<configid>

$ pvcall masarService:retrieveSnapshot eventid=eventid>

$ pvcall masarService:dumpDB
```

See [interface.md](interface.md) for a description of supported RPC calls.

Running the Qt client
---------------------

```sh
./masar
```

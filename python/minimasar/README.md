MINIMASAR Server
================

```sh
$ git clone https://github.com/mdavidsaver/masarService.git
$ cd masarService
$ cat <<EOF >configure/RELEASE.local
PVACLIENT=.../pvaClient
NORMATIVETYPES=.../normativeTypes
PVACCESS=.../pvAccess
PVDATA=.../pvData
EPICS_BASE=.../epics-base
EOF
$ make
```

In addition to the EPICS dependenecies listed,
minimasar also needs
the [cothread python module](http://controls.diamond.ac.uk/downloads/python/cothread/).

Run automatic tests

```sh
$ PYTHONPATH=$PWD/python2.7/linux-x86_64 nosetests p4p minimasar
```

Run daemon in simulated client mode with in-memory database.

```sh
$ PYTHONPATH=$PWD/python2.7/linux-x86_64 python -m minimasar.server --name masarService -L DEBUG ':memory:' -G sim
```

Run daemon in CA client mode and store in ```masar.db```.

```sh
$ PYTHONPATH=$PWD/python2.7/linux-x86_64 python -m minimasar.server --name masarService -L DEBUG masar.db -G ca
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

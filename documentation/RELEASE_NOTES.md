Release release/1.1 IN DEVELOPMENT
===========

The main changes since the last release are:

* Removed the dependency on PVIOCCPP
* New semantics for enumerated records that do not have choices configured.
* Compatible with release 4.3.0 of EPICS V4 BUT needs update to pvAccessCPP.

PVIOCCPP no longer required
--------

pvAccessCPP now has support for rpcServer and rpcClient.
These replace code that in the previous release was in pvIOCCPP.
Note that rpcClient replaces ezchannelRPC.
Also the version of rpcClient that comes with the version of pvAccessCPP for release 4.3.0 of
EPICS V4 does not work.

There is a branch of pvAccessCPP named release/3.0.4 that has a version of rpcClient that works.
This is the version that masarService must use.

Incorrectly Configured enumerated records
------------

These are bi, bo, mbbi, and mbbo records that do not have the choice strings properly configured.
For example a bi record that has null strings for ZNAM and ONAM.

When gatherV3Data gets a null string as a result of a DBF_ENUM request,
it reissues a get with a DBF_LONG request.
Thus an integer value is used to get and later put the value.

Note, however, that if a client incorrectly gives a bad integer value it will be wrtten
to the record.
Thus this feature should be used carefully.

Supports release 4.3.0 of EPICS V4
-----

But must use branch release/3.0.4 of pvAccessCPP.


Release 1.0.1-BETA
==========
This was the starting point for RELEASE_NOTES

MASAR RPC interface
===================

Argument encoding
-----------------

```py
requestType = Type([
    ('function', 's'),
    ('name', 'as'),
    ('value', 'av'),
])
```

Server request handling as python pseudo-code

```py
request = ... # p4p.Value
target  = ... # handler object
args = dict(zip(request.name, request.value))
reply = getattr(target, request.function)(**args)
```

The ```getLiveMachine()``` handles arguments differently.

So a call to

```py
def method(self, key=None):
    print 'method', key
```

A call ```method(key="test")``` would be encoded as

```py
request = Value(requestType, {
    'function': method,
    'name': ['key'],
    'value': ['test'],
})
```

Reply encoding
--------------

Methods ```getLiveMachine()```, ```retrieveSnapshot()```, and ```saveSnapshot()```
return a NTMultiChannel structure with 'value' as a variant union array.

```py
multiType = Type(id="epics:nt/NTMultiChannel:1.0",
     spec=[
    ('value', 'av'),
    ('channelName', 'as'),
    ('descriptor', 's'),
    ('alarm', ('s', None, [
        ('severity', 'i'),
        ('status', 'i'),
        ('message', 's'),
    ])),
    ('timeStamp', ('s', None, [
        ('secondsPastEpoch', 'l'),
        ('nanoseconds', 'i'),
        ('userTag', 'i'),
    ])),
    ('severity', 'ai'),
    ('status', 'ai'),
    ('message', 'as'),
    ('secondsPastEpoch', 'al'),
    ('nanoseconds', 'ai'),
    ('userTag', 'ai'),
    ('isConnected', 'a?'),
    # added
    ('readonly’, 'a?'),
    ('groupName’, 'as'),
    ('tags’, 'as'),
])
```

Methods ```retrieveServiceConfigs()```, ```retrieveServiceConfigProps()```, and ```retrieveServiceEvents()```
return an NTTable structure, each with different columns.
Column names are given with each call.

Method ```updateSnapshotEvent()``` returns an NTScalar boolean.

```py
scalarBool = Type(id="epics:nt/NTScalar:1.0",
            spec=[
    ('value', '?'),
    ('alarm', ('s', None, [
        ('severity', 'i'),
        ('status', 'i'),
        ('message', 's'),
    ])),
    ('timeStamp', ('s', None, [
        ('secondsPastEpoch', 'l'),
        ('nanoseconds', 'i'),
        ('userTag', 'i'),
    ])),
])
```

Methods
-------

```py
configInfo = NTTable.buildType([
    ('config_idx','ai'),
    ('config_name','as'),
    ('config_desc','as'),
    ('config_create_date','as'),
    ('config_version','as'),
    ('status','as'),
    ('system','as'),
])

@rpc(configInfo)
def retrieveServiceConfigs(servicename=None, configname=None, configversion=None, system=None, eventid=None, status=None):
    pass
```

Query for Configurations.
Entry point call.
Pass ```configname='all'``` to return all.
Returned ```config_idx``` can be passed to ```retrieveServiceEvents()```.

The argument 'status' may be None (aka all), 'active', or 'inactive'

```py
@rpc(NTTable.buildType([
    ('config_prop_id','ai'),
    ('config_idx','ai'),
    ('system_key','as'),
    ('system_val','as'),
]))
def retrieveServiceConfigProps(propname=None, servicename=None, configname=None):
    pass
```

```py
@rpc(NTTable.buildType([
    ('event_id','ai'),
    ('config_id','ai'),
    ('comments','as'),
    ('event_time','as'),
    ('user_name','as'),
]))
def retrieveServiceEvents(configid=None, start=None, end=None, comment=None, user=None, eventid=None):
    pass
```

Call with ```config_idx``` obtained from  ```retrieveServiceConfigs()``` along with ```user='*'``` and ```comment='*'```
to obtain all events.
Returned ```event_id``` can be passed to ```retrieveSnapshot()```.


```py
@rpc(multiType)
def retrieveSnapshot(eventid=None, start=None, end=None, comment=None):
    pass
```

Call with ```event_id``` obtained from  ```retrieveServiceEvents()```.

```py
@rpc(multiType)
def saveSnapshot(servicename=None, configname=None, comment=None):
    pass
```

Pass in 'configname' and optionally 'servicename'.
Returned NTMultiChannel uses the ```.timeStamp.userTag``` to hold
the new ```eventid``, which _must_ then be passed to
```updateSnapshotEvent()``` along with a user and description string
before the event is finally stored.

```py
@rpc(scalarBool)
def updateSnapshotEvent(eventid=None, configname=None, user=None, desc=None):
    pass
```

```py
@rpc(multiType)
def getLiveMachine(**kws):
    pvs = kws.values()
    # kws.keys() is ignored, but keys must be unique.
    # recommended to provide PV name as both key and value
    #   eg kws = dict(zip(pvs, pvs))
```


```py
configTable = NTTable.buildType([
    ('channelName', 'as'),
    ('readonly', 'a?'),
    ('groupName', 'as'),
    ('tags', 'as'),
])

@rpc(configInfo)
def storeServiceConfig(configname=None, oldidx=None, desc=None, config=None, system=None):
    pass
```

Create/Replace an existing configuration.
If oldidx==0 and configname does not name an existing configuration, then a new configuration is created.
If oldidx and configname match an existing, active, configuration, then
a new configuration is created and the matched configuration becomes inactive.
If the matched configuration is not active, an error is returned.

'config' must be a table with the column 'channelName'.
Optional columns 'readonly', 'groupName', and 'tags'.

Returns the same table as ```retrieveServiceConfigs()``` with a single row.


```py
@rpc(configTable)
def loadServiceConfig(configid=None):
    pass
```

Retrieve previously stored configuration.
configid must match an existing configuration.


from p4p.rpc import rpcproxy, rpccall

from .ops import configType

@rpcproxy
class MASAR(object):
    @rpccall("%sretrieveServiceConfigs")
    def retrieveServiceConfigs(configname='s', system='s', eventid='I', status='s', servicename='s'):
        """Entry point call
        
        Returns a table with columns: ::
            NTTable([
                ('config_idx','i'),
                ('config_name','s'),
                ('config_desc','s'),
                ('config_create_date','s'),
                ('config_version','s'),
                ('status','s'),
                ('system', 's'),
            ])

        All arguments are optional and act to filter the list of returned configurations.

        If specified, 'status' should be '', 'active', or 'inactive'.

        if 'specified', 'eventid' returns the configuration used for a particlular snapshot.
        """
        pass
    @rpccall("%sretrieveServiceConfigProps")
    def retrieveServiceConfigProps(configname='s', propname='s'):
        """Legacy method to fetch the "system" name.  Now returned by retrieveServiceConfigs().
        
        The only valid 'propname' is 'system'.
        """
        pass
    @rpccall("%sretrieveServiceEvents")
    def retrieveServiceEvents(configid='I', start='s', end='s', comment='s', user='s'):
        """Retreive a list of snapshot events.

        Returns a table with columns: ::
            NTTable([
                ('event_id','i'),
                ('config_id','i'),
                ('comments','s'),
                ('event_time','s'),
                ('user_name','s'),
            ])

        All arguments are optional.
        A typical usage will pass a 'config_idx' from retrieveServiceConfigs as 'configid'.

        Either 'start' or 'end' can filter by snapshot time in the range [start, end).
        Times must be in the format "%Y-%m-%d %H:%M:%S".
        """
        pass
    @rpccall("%sretrieveSnapshot")
    def retrieveSnapshot(eventid='I'):
        """Retreive a single snapshot.  Use 'event_id' from retrieveServiceEvents()

        Returns a list of values: ::
            NTMultiChannel.buildType('av', extra=[
                ('dbrType', 'ai'),
                ('readonly', 'a?'),
                ('groupName', 'as'),
                ('tags', 'as'),
            ])

        In the returned structure 'timeStamp.userTag' holds the eventid.
        """
        pass
    @rpccall("%ssaveSnapshot")
    def saveSnapshot(configname='s', user='s', desc='s', servicename='s'):
        """Take a new snapshot.
        
        Returns the same as retrieveSnapshot().
        In the returned structure 'timeStamp.userTag' holds the newly allocated eventid.

        Unless 'user' and 'desc' are provided, this new snapshot will not be visible until
        updateSnapshotEvent() is called.
        """
        pass
    @rpccall("%supdateSnapshotEvent")
    def updateSnapshotEvent(eventid='I', user='s', desc='s'):
        """Legacy method to complete a snapshot.
        """
        pass

    @rpccall("%sgetCurrentValue")
    def getCurrentValue(names='as'):
        """Fetch current values of a list of PV names
        """
        pass

    def createServiceConfig(*args, **kws):
        'Deprecated in favor of storeServiceConfig()'
        return self.storeServiceConfig(*args, **kws)
    def replaceServiceConfig(*args, **kws):
        'Deprecated in favor of storeServiceConfig()'
        return self.storeServiceConfig(*args, **kws)

    @rpccall("%sstoreServiceConfig")
    def storeServiceConfig(configname='s', oldidx='I', desc='s', system='s', config=configType.type):
        """Create or Update a configuration.

        To create a configuration call with oldidx=None.  Will fail if provided configname
        is already in use.

        To update a configuration, first call retrieveServiceConfigs() w/ configname, and status='active'.
        The returned Value will include a single row containing a 'config_idx'.
        Pass this 'config_idx' as oldidx to this method to replace the currently active config
        with the newly provided config.  Will fail if oldidx no longer identies the active
        version.
        """
        pass

    @rpccall("%sloadServiceConfig")
    def loadServiceConfig(configid='I'):
        """Retrieve a previously stored configuration.

        Returns a table (same as argument of createServiceConfig() ).
        """
        pass

    @rpccall("%smodifyServiceConfig")
    def modifyServiceConfig(configid='I', status='s'):
        """Change the 'active'/'inactive' status of a configuration.

        Any 'active' configuration can be made 'inactive'.

        Only a configuration which has not been superceeded ((previously forced 'inactive')
        can be made 'active'.
        """
        pass

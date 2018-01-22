
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

    @rpccall("%sstoreServiceConfig")
    def createServiceConfig(configname='s', desc='s', system='s', config=configType.type):
        """Create a configuration.

        Returns the same as retrieveServiceConfigs()

        Fails if 'configname' already exists.

        'config' must be a NTTable with: ::

            configType = NTTable([
                ('channelName', 's'),
                ('readonly', '?'),
                ('groupName', 's'),
                ('tags', 's'),
            ])

        The 'channelName' column is mandatory.  The others are optional.
        """
        pass
    @rpccall("%sstoreServiceConfig")
    def replaceServiceConfig(configname='s', oldidx='I', desc='s', system='s', config=configType.type):
        """Update a configuration.

        Provided 'configname' must exist, and provided 'oldidx' must be the 'config_idx'
        of the 'active' configuration with this name.

        Otherwise the same as createServiceConfig()
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

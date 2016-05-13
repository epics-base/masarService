import sys
import unittest

from masarclient import masarClient
from masarclient.channelRPC import epicsExit

'''

Unittests for masarService/python/masarclient/masarClient.py

'''


class TestMasarClient(unittest.TestCase):

    def setUp(self):
        channel = 'masarService'
        self.mc = masarClient.client(channelname=channel)

    def testRetrieveSystemList(self):
        result = self.mc.retrieveSystemList()
        self.assertTrue(result is not None, "retrieveSystemList returned unexpected value")

    def testRetrieveServiceConfigs(self):
        params = {'system': 'LTD2'}
        result = self.mc.retrieveServiceConfigs(params)
        self.assertTrue(result is not None, "retrieveServiceConfigs returned unexpected value")

    def testRetrieveServiceEvents(self):
        params = {'configid': '1'}
        result = self.mc.retrieveServiceEvents(params)
        self.assertTrue(result is not None, "retrieveServiceEvents returned unexpected value")

    def testSaveSnapshot(self):
        params = {'configname': 'test',
                  'servicename': 'masar'}
        result = self.mc.saveSnapshot(params)
        self.assertTrue(result is not None, "saveSnapshot returned unexpected value")

    def testRetrieveSnapshot(self):
        save_params = {'configname': 'test',
                  'servicename': 'masar'}
        res1 = self.mc.saveSnapshot(save_params)
        event_id = res1[0]
        retrieve_params = {'eventid': str(event_id)}
        result = self.mc.retrieveSnapshot(retrieve_params)
        self.assertTrue(result is not None, "RetrieveSystemList returned unexpected value")

    def testApproveSnapshot(self):
        save_params = {'configname': 'test',
                       'servicename': 'masar'}

        res1 = self.mc.saveSnapshot(save_params)
        event_id = res1[0]
        approve_params = {'eventid': str(event_id),
                  'configname': 'test',
                  'user': 'test',
                  'desc': 'this is a good snapshot, and I approved it.'}
        result = self.mc.updateSnapshotEvent(approve_params)
        self.assertTrue(result is not None, "updateSnapshostEvent returned unexpected value")

    def testGetLiveMachine(self):
        pvlist = ["masarExampleCharArray",
                  "masarExampleFloatArray",
                  "masarExampleShortArray",
                  "masarExampleUCharArray"]
        for i in range(len(pvlist)):
            params = {}
            for pv in pvlist[i:]:
                params[pv] = pv
                result = self.mc.getLiveMachine(params)
                self.assertTrue(result is not None, "getLiveMachine returned unexpected value")

    def testMasarClientLifecycle(self):
        #retrieve configs
        params = {'system': 'LTD2'}
        result = self.mc.retrieveServiceConfigs(params)
        self.assertTrue(result is not None, "retrieveServiceConfigs returned unexpected value")
        #retrieve list
        result = self.mc.retrieveSystemList()
        self.assertTrue(result is not None, "retrieveSystemList returned unexpected value")
        #save snapshot
        params = {'configname': 'test',
                  'servicename': 'masar'}
        result = self.mc.saveSnapshot(params)
        self.assertTrue(result is not None, "saveSnapshot returned unexpected value")
        #approve snapshot
        save_params = {'configname': 'test',
                       'servicename': 'masar'}

        res1 = self.mc.saveSnapshot(save_params)
        event_id = res1[0]
        approve_params = {'eventid': str(event_id),
                  'configname': 'test',
                  'user': 'test',
                  'desc': 'this is a good snapshot, and I approved it.'}
        result = self.mc.updateSnapshotEvent(approve_params)
        self.assertTrue(result is not None, "updateSnapshostEvent returned unexpected value")
        #retrieve snapshot
        save_params = {'configname': 'test',
                  'servicename': 'masar'}
        res1 = self.mc.saveSnapshot(save_params)
        event_id = res1[0]
        retrieve_params = {'eventid': str(event_id)}
        result = self.mc.retrieveSnapshot(retrieve_params)
        self.assertTrue(result is not None, "RetrieveSystemList returned unexpected value")
        #retrieve events
        params = {'configid': '1'}
        result = self.mc.retrieveServiceEvents(params)
        self.assertTrue(result is not None, "retrieveServiceEvents returned unexpected value")
        #live machine
        pvlist = ["masarExampleCharArray",
                  "masarExampleFloatArray",
                  "masarExampleShortArray",
                  "masarExampleUCharArray"]
        params = {}
        for i in range(len(pvlist)):
            params[pvlist[i]] = pvlist[i]
            result = self.mc.getLiveMachine(params)
            self.assertTrue(result is not None, "getLiveMachine returned unexpected value")

    if __name__ == '__main__':
        unittest.main()

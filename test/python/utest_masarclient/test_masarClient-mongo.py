import sys
import unittest

from masarclient import masarClient
from masarclient.channelRPC import epicsExit
from pymasarmongo.db import utils
from pymasarmongo.config._config import masarconfig

from pymasarmongo.pymasarmongo.pymasar import saveconfig
from pymasarmongo.pymasarmongo.pymasar import retrieveconfig
from pymasarmongo.pymasarmongo.pymasar import updateconfig
from pymasarmongo.pymasarmongo.pymasar import saveevent
from pymasarmongo.pymasarmongo.pymasar import retrieveevents
from pymasarmongo.pymasarmongo.pymasar import updateevent
from pymasarmongo.pymasarmongo.pymasar import retrievesnapshot

'''

Unittests for masarService/python/masarclient/masarClient.py

'''


class TestMasarClient(unittest.TestCase):

    def setUp(self):
        channel = 'masarService'
        self.mc = masarClient.client(channelname=channel)
        # DB SETUP
        self.conn, collection = utils.conn(host=masarconfig.get('mongodb', 'host'), port=masarconfig.get('mongodb', 'port'),
                                      db=masarconfig.get('mongodb', 'database'))

        self.conn.drop_database(masarconfig.get('mongodb', 'database'))
        name = "SR_All_20140421"
        params = {"desc": "SR daily SCR setpoint without IS kick and septum: SR and RF",
                  "system": "SR",
                  "status": "active",
                  "version": 20140421,
                  }
        newid = saveconfig(self.conn, collection, name, **params)
        res0 = retrieveconfig(self.conn, collection, name)
        pvs = ["masarExampleDoubleArray"]
        updateconfig(self.conn, collection, name, pvlist={"names": pvs})
        res3 = retrieveconfig(self.conn, collection, name, withpvs=True)

    def tearDown(self):
        self.conn.drop_database(masarconfig.get('mongodb', 'database'))
        utils.close(self.conn)

    def testRetrieveSystemList(self):
        result = self.mc.retrieveSystemList()
        print "system list " + str(result)
        self.assertNotEqual(result, None)  # Can not be assertTrue because there is no case where it returns True
        self.assertNotEqual(result, False)  # Instead asserting both not None and not False
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'SR')

    def testRetrieveServiceConfigs(self):
        params = {'system': 'SR'}
        result = self.mc.retrieveServiceConfigs(params)
        print "result " +str(result)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        self.assertEqual(len(result), 6)

    def testRetrieveServiceEvents(self):
        params = {'configid': '1'}
        result = self.mc.retrieveServiceEvents(params)
        print "result2 " +str(result)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)

    def testSaveSnapshot(self):
        params = {"configname": "SR_All_20140421",
                  "system": "SR"}
        result = self.mc.saveSnapshot(params)
        print "save result:  " + str(result)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)

    def testRetrieveSnapshot(self):
        save_params = {'configname': 'SR_All_20140421'}
        res1 = self.mc.saveSnapshot(save_params)
        self.assertNotEqual(res1, None)
        self.assertNotEqual(res1, False)
        event_id = res1[0]
        retrieve_params = {'eventid': str(event_id)}
        result = self.mc.retrieveSnapshot(retrieve_params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)

    def testApproveSnapshot(self):
        save_params = {'configname': 'SR_All_20140421'}

        res1 = self.mc.saveSnapshot(save_params)
        self.assertNotEqual(res1, None)
        self.assertNotEqual(res1, False)  # Can not be assertTrue because there is no case where it returns True
        event_id = res1[0]
        approve_params = {'eventid': str(event_id),
                  'configname': 'SR_All_20140421',
                  'user': 'test',
                  'desc': 'this is a good snapshot, and I approved it.'}
        result = self.mc.updateSnapshotEvent(approve_params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)

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
                self.assertNotEqual(result, None)
                print "machine result " + str(result)
                #self.assertNotEqual(result, False)

    def testMasarClientLifecycle(self):
        #retrieve configs
        params = {'system': 'SR'}
        result = self.mc.retrieveServiceConfigs(params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        #retrieve list
        result = self.mc.retrieveSystemList()
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        #save snapshot
        params = {'configname': 'SR_All_20140421'}
        result = self.mc.saveSnapshot(params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        #approve snapshot
        save_params = {'configname': 'SR_All_20140421'}

        res1 = self.mc.saveSnapshot(save_params)
        event_id = res1[0]
        approve_params = {'eventid': str(event_id),
                  'configname': 'SR_All_20140421',
                  'user': 'test',
                  'desc': 'this is a good snapshot, and I approved it.'}
        result = self.mc.updateSnapshotEvent(approve_params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        #retrieve snapshot
        save_params = {'configname': 'SR_All_20140421'}
        res1 = self.mc.saveSnapshot(save_params)
        event_id = res1[0]
        retrieve_params = {'eventid': str(event_id)}
        result = self.mc.retrieveSnapshot(retrieve_params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        #retrieve events
        params = {'configid': '1'}
        result = self.mc.retrieveServiceEvents(params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        #live machine
        pvlist = ["masarExampleCharArray",
                  "masarExampleFloatArray",
                  "masarExampleShortArray",
                  "masarExampleUCharArray"]
        params = {}
        for i in range(len(pvlist)):
            params[pvlist[i]] = pvlist[i]
            result = self.mc.getLiveMachine(params)
            self.assertNotEqual(result, None)
            self.assertNotEqual(result, False)

    if __name__ == '__main__':
        unittest.main()

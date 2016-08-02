import sys
import unittest

from masarclient import masarClient
from masarclient.channelRPC import epicsExit
from pymasarmongo.db import utils
from pymasarmongo.config._config import masarconfig

from pymasarmongo.pymasarmongo.pymasar import saveconfig
from pymasarmongo.pymasarmongo.pymasar import retrieveconfig
from pymasarmongo.pymasarmongo.pymasar import updateconfig
class test_service_config(unittest.TestCase):

    def testConfiguration(self):
        channel = 'masarService'
        self.mc = masarClient.client(channelname=channel)
        # DB SETUP
        self.conn, collection = utils.conn(host=masarconfig.get('mongodb', 'host'),
                                           port=masarconfig.get('mongodb', 'port'),
                                           db=masarconfig.get('mongodb', 'database'))

        self.conn.drop_database(masarconfig.get('mongodb', 'database'))
        name = "SR_All_20140421"
        test_status = 'active'
        test_version = 20140421
        test_system = 'SR'
        test_desc = "SR daily SCR setpoint without IS kick and septum: SR and RF"
        params = {"desc": test_desc,
                  "system": test_system,
                  "status": test_status,
                  "version": test_version,
                  }
        newid = saveconfig(self.conn, collection, name, **params)
        self.assertNotEqual(None, newid)
        res0 = retrieveconfig(self.conn, collection, name)
        self.assertEqual(test_status, res0[0]['status'])
        self.assertEqual(1, res0[0]['configidx'])
        self.assertEqual(name, res0[0]['name'])
        self.assertEqual(test_system, res0[0]['system'])
        self.assertNotEqual(None, res0[0]['created_on'])
        # The following 2 tests are to confirm the date string is in the correct format
        self.assertEqual(3, len(res0[0]['created_on'].split('-')))
        self.assertEqual(3, len(res0[0]['created_on'].split(':')))
        self.assertEqual(test_version, res0[0]['version'])
        self.assertEqual(test_desc, res0[0]['desc'])
        pvs = ["masarExampleDoubleArray"]
        pvlist = {"names": pvs}
        res = updateconfig(self.conn, collection, name, pvlist=pvlist)
        self.assertEqual(True, res)
        res3 = retrieveconfig(self.conn, collection, name, withpvs=True)
        self.assertEqual(test_status, res3[0]['status'])
        self.assertEqual(1, res3[0]['configidx'])
        self.assertEqual(name, res3[0]['name'])
        self.assertEqual(test_system, res3[0]['system'])
        self.assertNotEqual(None, res3[0]['created_on'])
        # The following 2 tests are to confirm the date string is in the correct format
        self.assertEqual(3, len(res3[0]['created_on'].split('-')))
        self.assertEqual(3, len(res3[0]['created_on'].split(':')))
        self.assertEqual(test_version, res3[0]['version'])
        self.assertEqual(test_desc, res3[0]['desc'])
        self.assertEqual(pvlist, res3[0]['pvlist'])
        self.assertNotEqual(None,res3[0]['updated_on'])
        # The following 2 tests are to confirm the date string is in the correct format
        self.assertEqual(3, len(res3[0]['updated_on'].split('-')))
        self.assertEqual(3, len(res3[0]['updated_on'].split(':')))
        # drop DB
        self.conn.drop_database(masarconfig.get('mongodb', 'database'))
        utils.close(self.conn)

    if __name__ == '__main__':
        unittest.main()

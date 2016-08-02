'''
Created on Jul 28, 2014

@author: shengb
'''
import unittest
import time

from pymasarmongo.db import utils
from pymasarmongo.config._config import masarconfig

from pymasarmongo.pymasarmongo.pymasar import saveconfig
from pymasarmongo.pymasarmongo.pymasar import retrieveconfig
from pymasarmongo.pymasarmongo.pymasar import updateconfig
from pymasarmongo.pymasarmongo.pymasar import saveevent
from pymasarmongo.pymasarmongo.pymasar import retrieveevents
from pymasarmongo.pymasarmongo.pymasar import updateevent
from pymasarmongo.pymasarmongo.pymasar import retrievesnapshot


class Test(unittest.TestCase):

    def setUp(self):
        self.conn, self.collection = utils.conn(host=masarconfig.get('mongodb','host'), port=masarconfig.get('mongodb','port'), db=masarconfig.get('mongodb','database'))

    def tearDown(self):
        #print "database: ", self.conn.database_names()
        #print "collections: ", self.conn[self.collection]
        #print "collections: ", self.conn[self.collection].collection_names()
        self.conn.drop_database(masarconfig.get('mongodb', 'database'))
        utils.close(self.conn)

    def testSaveconfig(self):
        name = "SR_All_20140421"
        params = {"desc": "SR daily SCR setpoint without IS kick and septum: SR and RF",
                  "system": "SR",
                  "status": "active",
                  "version": 20140421,
                  }
        
        newid = saveconfig(self.conn, self.collection, name, **params)
        new = retrieveconfig(self.conn, self.collection, name=name)
        self.assertEqual(len(new), 1, 
                         "Should find only one entry instead of %s"%len(new))
        self.assertEqual(newid, new[0]["_id"], 
                         "Expecting id %s but got %s"%(newid, new[0]["_id"]))
        with self.assertRaises(ValueError) as context:
            saveconfig(self.conn, self.collection, name, **params)
        self.assertEqual(context.exception.message, "Configuration (%s) exists already."%name)

        name1 = 'SR-All-20140326'
        params1 = {"desc": "SR daily SCR setpoint: SR and IS PS, RF",
                  "system": "SR",
                  "status": "inactive",
                  "version": 20140326,
                  }
        newid1 = saveconfig(self.conn, self.collection, name1, **params1)
        new1 = retrieveconfig(self.conn, self.collection, name=name1)
        self.assertEqual(len(new1), 1, 
                         "Should find only one entry instead of %s"%len(new1))
        self.assertEqual(newid1, new1[0]["_id"], 
                         "Expecting id %s but got %s"%(newid1, new1[0]["_id"]))
        self.assertEqual(new1[0]["configidx"]-new[0]["configidx"], 1)
        
        name2 = 'SR-All-LTB_PS_"SRC_20131206'
        params2 = {"desc": "LTB power supply setpoints, for saving/comparing/restoring",
                  "system": "LTB",
                  "status": "active",
                  "version": 20131206,
                  }
        newid2 = saveconfig(self.conn, self.collection, name2, **params2)
        new2 = retrieveconfig(self.conn, self.collection, name=name2)
        self.assertEqual(len(new2), 1, 
                         "Should find only one entry instead of %s"%len(new2))
        self.assertEqual(newid2, new2[0]["_id"], 
                         "Expecting id %s but got %s"%(newid2, new2[0]["_id"]))
        self.assertEqual(new2[0]["configidx"]-new1[0]["configidx"], 1)
        
        name3 = 'LTB_BR_BTS_20140421'
        params3 = {"desc": "BR SCR PVs with IS kick and septum: LTB, BT, BTS, SR IS",
                  "system": "LTB, BR, BTS",
                  "status": "active",
                  "version": 20140421,
                  }
        newid3 = saveconfig(self.conn, self.collection, name3, **params3)
        new3 = retrieveconfig(self.conn, self.collection, name=name3)
        self.assertEqual(len(new3), 1, 
                         "Should find only one entry instead of %s"%len(new3))
        self.assertEqual(newid3, new3[0]["_id"], 
                         "Expecting id %s but got %s"%(newid3, new3[0]["_id"]))
        self.assertEqual(new3[0]["configidx"]-new2[0]["configidx"], 1)

        system4SR = retrieveconfig(self.conn, self.collection, system="SR")
        self.assertEqual(len(system4SR), 2)

        system4more = retrieveconfig(self.conn, self.collection, system=params3["system"])
        self.assertEqual(len(system4more), 1)
        
        system4all = retrieveconfig(self.conn, self.collection, system="*")
        self.assertEqual(len(system4all), 4)

        system4all = retrieveconfig(self.conn, self.collection, system="LTB*")
        self.assertEqual(len(system4all), 2)

        system4all = retrieveconfig(self.conn, self.collection, system="L*B*")
        self.assertEqual(len(system4all), 2)

        system4all = retrieveconfig(self.conn, self.collection, system="L*B,*")
        self.assertEqual(len(system4all), 1)

        system4all = retrieveconfig(self.conn, self.collection, system="*S*B,*")
        self.assertEqual(len(system4all), 0)

    def testRetrieveconfig(self):
        """"""
        res = retrieveconfig(self.conn, self.collection, "*", "*")
        self.assertEqual(len(res), 0,
                         "Should find zero results from an empty database")
        
    def testUpdateconfig(self):
        """"""
        name = "SR_All_20140421"
        params = {"desc": "SR daily SCR setpoint without IS kick and septum: SR and RF",
                  "system": "SR",
                  "status": "active",
                  "version": 20140421,
                  }
        with self.assertRaises(RuntimeError) as context:
            updateconfig(self.conn, self.collection, None)
        self.assertEqual(context.exception.message, "Cannot identify configuration to update.")
        time.sleep(1)
        with self.assertRaises(RuntimeError) as context:
            updateconfig(self.conn, self.collection, name)
        self.assertEqual(context.exception.message, "Wrong Mongo document for %s" % name)

        newid = saveconfig(self.conn, self.collection, name, **params)
        res0 = retrieveconfig(self.conn, self.collection, name)
        self.assertTrue(updateconfig(self.conn, self.collection, name, status="inactive"))
        res1 = retrieveconfig(self.conn, self.collection, name)
        self.assertEqual(newid, res0[0]["_id"])
        self.assertEqual(newid, res1[0]["_id"])
        self.assertEqual(res0[0]["status"], "active")
        self.assertEqual(res1[0]["status"], "inactive")
        self.assertEqual(res1[0]["created_on"], res0[0]["created_on"])
        time.sleep(1)  # delay required for below updated_on inequality test
        self.assertTrue(updateconfig(self.conn, self.collection, name, status="active"))
        res2 = retrieveconfig(self.conn, self.collection, name)
        self.assertEqual(res2[0]["status"], "active")
        self.assertNotEqual(res1[0]["updated_on"], res2[0]["updated_on"])
        self.assertEqual(res1[0]["created_on"], res2[0]["created_on"])
        self.assertEqual(res1[0]["created_on"], res0[0]["created_on"])
        pvs = ["RF{Osc:1}Freq:I",  "SR-RF{CFC:D}E:Fb-SP",  "SR-RF{CFC:D}Phs:Fb-SP",  "SR-RF{CFC:D}Tuner:PhaOff-SP",
               "SR:C01-MG{PS:BT1A}I:Sp1-SP",  "SR:C01-MG{PS:BT1A}I:Sp2-SP",  "SR:C01-MG{PS:CH1B}I:Sp1-SP",  "SR:C01-MG{PS:CH1B}I:Sp2-SP",
               "SR:C01-MG{PS:CH2B}I:Sp1-SP",  "SR:C01-MG{PS:CH2B}I:Sp2-SP",  "SR:C01-MG{PS:CL1A}I:Sp1-SP",  "SR:C01-MG{PS:CL1A}I:Sp2-SP",
               "SR:C01-MG{PS:CL2A}I:Sp1-SP",  "SR:C01-MG{PS:CL2A}I:Sp2-SP",  "SR:C01-MG{PS:CM1A}I:Sp1-SP",  "SR:C01-MG{PS:CM1A}I:Sp2-SP",
               "SR:C01-MG{PS:CM1B}I:Sp1-SP",  "SR:C01-MG{PS:CM1B}I:Sp2-SP",  "SR:C01-MG{PS:QH1B}I:Sp1-SP",  "SR:C01-MG{PS:QH2B}I:Sp1-SP",
               "SR:C01-MG{PS:QH3B}I:Sp1-SP",  "SR:C01-MG{PS:QL1A}I:Sp1-SP",  "SR:C01-MG{PS:QL2A}I:Sp1-SP",  "SR:C01-MG{PS:QL3A}I:Sp1-SP",
               "SR:C01-MG{PS:QM1A}I:Sp1-SP",  "SR:C01-MG{PS:QM1B}I:Sp1-SP",  "SR:C01-MG{PS:QM2A}I:Sp1-SP",  "SR:C01-MG{PS:QM2B}I:Sp1-SP",
               "SR:C01-MG{PS:SH4-P2}I:Sp1-SP",  "SR:C01-MG{PS:SM1A-P2}I:Sp1-SP",  "SR:C01-MG{PS:SQKM1A}I:Sp1-SP",  "SR:C02-MG{PS:BT1A}I:Sp1-SP",
               "SR:C02-MG{PS:BT1A}I:Sp2-SP",  "SR:C02-MG{PS:CH1A}I:Sp1-SP",  "SR:C02-MG{PS:CH1A}I:Sp2-SP",  "SR:C02-MG{PS:CH2A}I:Sp1-SP",
               "SR:C02-MG{PS:CH2A}I:Sp2-SP",  "SR:C02-MG{PS:CL1B}I:Sp1-SP",  "SR:C02-MG{PS:CL1B}I:Sp2-SP",  "SR:C02-MG{PS:CL2B}I:Sp1-SP",
               "SR:C02-MG{PS:CL2B}I:Sp2-SP",  "SR:C02-MG{PS:CM1A}I:Sp1-SP",  "SR:C02-MG{PS:CM1A}I:Sp2-SP",  "SR:C02-MG{PS:CM1B}I:Sp1-SP",
               "SR:C02-MG{PS:CM1B}I:Sp2-SP",  "SR:C02-MG{PS:QH1A}I:Sp1-SP",  "SR:C02-MG{PS:QH2A}I:Sp1-SP",  "SR:C02-MG{PS:QH3A}I:Sp1-SP",
               "SR:C02-MG{PS:QL1B}I:Sp1-SP",  "SR:C02-MG{PS:QL2B}I:Sp1-SP",  "SR:C02-MG{PS:QL3B}I:Sp1-SP",  "SR:C02-MG{PS:QM1A}I:Sp1-SP",
                "SR:C02-MG{PS:QM1B}I:Sp1-SP",  "SR:C02-MG{PS:QM2A}I:Sp1-SP",  "SR:C02-MG{PS:QM2B}I:Sp1-SP",  "SR:C02-MG{PS:SM1B-P2}I:Sp1-SP",
                "SR:C02-MG{PS:SM2B-P2}I:Sp1-SP",  "SR:C02-MG{PS:SQKH1A}I:Sp1-SP",  "SR:C03-MG{PS:BT1A}I:Sp1-SP",  "SR:C03-MG{PS:BT1A}I:Sp2-SP",
                "SR:C03-MG{PS:CH1B}I:Sp1-SP",  "SR:C03-MG{PS:CH1B}I:Sp2-SP",  "SR:C03-MG{PS:CH2B}I:Sp1-SP",  "SR:C03-MG{PS:CH2B}I:Sp2-SP",
                "SR:C03-MG{PS:CL1A}I:Sp1-SP",  "SR:C03-MG{PS:CL1A}I:Sp2-SP",  "SR:C03-MG{PS:CL2A}I:Sp1-SP",  "SR:C03-MG{PS:CL2A}I:Sp2-SP",
                "SR:C03-MG{PS:CM1A}I:Sp1-SP",  "SR:C03-MG{PS:CM1A}I:Sp2-SP",  "SR:C03-MG{PS:CM1B}I:Sp1-SP",  "SR:C03-MG{PS:CM1B}I:Sp2-SP",
                "SR:C03-MG{PS:D-SP}I:Sp1-SP",  "SR:C03-MG{PS:QH1B}I:Sp1-SP",  "SR:C03-MG{PS:QH2B}I:Sp1-SP",  "SR:C03-MG{PS:QH3B}I:Sp1-SP",
                "SR:C03-MG{PS:QL1A}I:Sp1-SP",  "SR:C03-MG{PS:QL2A}I:Sp1-SP",  "SR:C03-MG{PS:QL3A}I:Sp1-SP",  "SR:C03-MG{PS:QM1A}I:Sp1-SP",
                "SR:C03-MG{PS:QM1B}I:Sp1-SP",  "SR:C03-MG{PS:QM2A}I:Sp1-SP",  "SR:C03-MG{PS:QM2B}I:Sp1-SP",  "SR:C03-MG{PS:SL2-P2}I:Sp1-SP",
                "SR:C03-MG{PS:SL3-P2}I:Sp1-SP",  "SR:C03-MG{PS:SQKM1A}I:Sp1-SP",  "SR:C04-MG{PS:BT1A}I:Sp1-SP",  "SR:C04-MG{PS:BT1A}I:Sp2-SP",
                "SR:C04-MG{PS:CH1A}I:Sp1-SP",  "SR:C04-MG{PS:CH1A}I:Sp2-SP",  "SR:C04-MG{PS:CH2A}I:Sp1-SP",  "SR:C04-MG{PS:CH2A}I:Sp2-SP",
                "SR:C04-MG{PS:CL1B}I:Sp1-SP",  "SR:C04-MG{PS:CL1B}I:Sp2-SP",  "SR:C04-MG{PS:CL2B}I:Sp1-SP",  "SR:C04-MG{PS:CL2B}I:Sp2-SP",
                "SR:C04-MG{PS:CM1A}I:Sp1-SP",  "SR:C04-MG{PS:CM1A}I:Sp2-SP",  "SR:C04-MG{PS:CM1B}I:Sp1-SP",  "SR:C04-MG{PS:CM1B}I:Sp2-SP",
                "SR:C04-MG{PS:QH1A}I:Sp1-SP",  "SR:C04-MG{PS:QH2A}I:Sp1-SP",  "SR:C04-MG{PS:QH3A}I:Sp1-SP",  "SR:C04-MG{PS:QL1B}I:Sp1-SP",
                "SR:C04-MG{PS:QL2B}I:Sp1-SP",  "SR:C04-MG{PS:QL3B}I:Sp1-SP",  "SR:C04-MG{PS:QM1A}I:Sp1-SP",  "SR:C04-MG{PS:QM1B}I:Sp1-SP",
                "SR:C04-MG{PS:QM2A}I:Sp1-SP",  "SR:C04-MG{PS:QM2B}I:Sp1-SP",  "SR:C04-MG{PS:SL1-P2}I:Sp1-SP",  "SR:C04-MG{PS:SQKH1A}I:Sp1-SP",
                "SR:C05-MG{PS:BT1A}I:Sp1-SP",  "SR:C05-MG{PS:BT1A}I:Sp2-SP",  "SR:C05-MG{PS:CH1B}I:Sp1-SP",  "SR:C05-MG{PS:CH1B}I:Sp2-SP",
                "SR:C05-MG{PS:CH2B}I:Sp1-SP",  "SR:C05-MG{PS:CH2B}I:Sp2-SP",  "SR:C05-MG{PS:CL1A}I:Sp1-SP",  "SR:C05-MG{PS:CL1A}I:Sp2-SP",
                "SR:C05-MG{PS:CL2A}I:Sp1-SP",  "SR:C05-MG{PS:CL2A}I:Sp2-SP",  "SR:C05-MG{PS:CM1A}I:Sp1-SP",  "SR:C05-MG{PS:CM1A}I:Sp2-SP",
                "SR:C05-MG{PS:CM1B}I:Sp1-SP",  "SR:C05-MG{PS:CM1B}I:Sp2-SP",  "SR:C05-MG{PS:QH1B}I:Sp1-SP",  "SR:C05-MG{PS:QH2B}I:Sp1-SP",
                "SR:C05-MG{PS:QH3B}I:Sp1-SP",  "SR:C05-MG{PS:QL1A}I:Sp1-SP",  "SR:C05-MG{PS:QL2A}I:Sp1-SP",  "SR:C05-MG{PS:QL3A}I:Sp1-SP",
                "SR:C05-MG{PS:QM1A}I:Sp1-SP",  "SR:C05-MG{PS:QM1B}I:Sp1-SP",  "SR:C05-MG{PS:QM2A}I:Sp1-SP",  "SR:C05-MG{PS:QM2B}I:Sp1-SP",
                "SR:C05-MG{PS:SQKM1A}I:Sp1-SP",  "SR:C06-MG{PS:BT1A}I:Sp1-SP",  "SR:C06-MG{PS:BT1A}I:Sp2-SP",  "SR:C06-MG{PS:CH1A}I:Sp1-SP",
                "SR:C06-MG{PS:CH1A}I:Sp2-SP",  "SR:C06-MG{PS:CH2A}I:Sp1-SP",  "SR:C06-MG{PS:CH2A}I:Sp2-SP",  "SR:C06-MG{PS:CL1B}I:Sp1-SP",
                "SR:C06-MG{PS:CL1B}I:Sp2-SP",  "SR:C06-MG{PS:CL2B}I:Sp1-SP",  "SR:C06-MG{PS:CL2B}I:Sp2-SP",  "SR:C06-MG{PS:CM1A}I:Sp1-SP",
                "SR:C06-MG{PS:CM1A}I:Sp2-SP",  "SR:C06-MG{PS:CM1B}I:Sp1-SP",  "SR:C06-MG{PS:CM1B}I:Sp2-SP",  "SR:C06-MG{PS:QH1A}I:Sp1-SP",
                "SR:C06-MG{PS:QH2A}I:Sp1-SP",  "SR:C06-MG{PS:QH3A}I:Sp1-SP",  "SR:C06-MG{PS:QL1B}I:Sp1-SP",  "SR:C06-MG{PS:QL2B}I:Sp1-SP",
                "SR:C06-MG{PS:QL3B}I:Sp1-SP",  "SR:C06-MG{PS:QM1A}I:Sp1-SP",  "SR:C06-MG{PS:QM1B}I:Sp1-SP",  "SR:C06-MG{PS:QM2A}I:Sp1-SP",
                "SR:C06-MG{PS:QM2B}I:Sp1-SP",  "SR:C06-MG{PS:SH1-P3}I:Sp1-SP",  "SR:C06-MG{PS:SH3-P3}I:Sp1-SP",  "SR:C06-MG{PS:SQKH1A}I:Sp1-SP",
                "SR:C07-MG{PS:BT1A}I:Sp1-SP",  "SR:C07-MG{PS:BT1A}I:Sp2-SP",  "SR:C07-MG{PS:CH1B}I:Sp1-SP",  "SR:C07-MG{PS:CH1B}I:Sp2-SP",
                "SR:C07-MG{PS:CH2B}I:Sp1-SP",  "SR:C07-MG{PS:CH2B}I:Sp2-SP",  "SR:C07-MG{PS:CL1A}I:Sp1-SP",  "SR:C07-MG{PS:CL1A}I:Sp2-SP",
                "SR:C07-MG{PS:CL2A}I:Sp1-SP",  "SR:C07-MG{PS:CL2A}I:Sp2-SP",  "SR:C07-MG{PS:CM1A}I:Sp1-SP",  "SR:C07-MG{PS:CM1A}I:Sp2-SP",
                "SR:C07-MG{PS:CM1B}I:Sp1-SP",  "SR:C07-MG{PS:CM1B}I:Sp2-SP",  "SR:C07-MG{PS:QH1B}I:Sp1-SP",  "SR:C07-MG{PS:QH2B}I:Sp1-SP",
                "SR:C07-MG{PS:QH3B}I:Sp1-SP",  "SR:C07-MG{PS:QL1A}I:Sp1-SP",  "SR:C07-MG{PS:QL2A}I:Sp1-SP",  "SR:C07-MG{PS:QL3A}I:Sp1-SP",
                "SR:C07-MG{PS:QM1A}I:Sp1-SP",  "SR:C07-MG{PS:QM1B}I:Sp1-SP",  "SR:C07-MG{PS:QM2A}I:Sp1-SP",  "SR:C07-MG{PS:QM2B}I:Sp1-SP",
                "SR:C07-MG{PS:SH4-P3}I:Sp1-SP",  "SR:C07-MG{PS:SM1A-P3}I:Sp1-SP",  "SR:C07-MG{PS:SQKM1A}I:Sp1-SP",  "SR:C08-MG{PS:BT1A}I:Sp1-SP",
                "SR:C08-MG{PS:BT1A}I:Sp2-SP",  "SR:C08-MG{PS:CH1A}I:Sp1-SP",  "SR:C08-MG{PS:CH1A}I:Sp2-SP",  "SR:C08-MG{PS:CH2A}I:Sp1-SP",
                "SR:C08-MG{PS:CH2A}I:Sp2-SP",  "SR:C08-MG{PS:CL1B}I:Sp1-SP",  "SR:C08-MG{PS:CL1B}I:Sp2-SP",  "SR:C08-MG{PS:CL2B}I:Sp1-SP",
                "SR:C08-MG{PS:CL2B}I:Sp2-SP",  "SR:C08-MG{PS:CM1A}I:Sp1-SP",  "SR:C08-MG{PS:CM1A}I:Sp2-SP",  "SR:C08-MG{PS:CM1B}I:Sp1-SP",
                "SR:C08-MG{PS:CM1B}I:Sp2-SP",  "SR:C08-MG{PS:QH1A}I:Sp1-SP",  "SR:C08-MG{PS:QH2A}I:Sp1-SP",  "SR:C08-MG{PS:QH3A}I:Sp1-SP",
                "SR:C08-MG{PS:QL1B}I:Sp1-SP",  "SR:C08-MG{PS:QL2B}I:Sp1-SP",  "SR:C08-MG{PS:QL3B}I:Sp1-SP",  "SR:C08-MG{PS:QM1A}I:Sp1-SP",
                "SR:C08-MG{PS:QM1B}I:Sp1-SP",  "SR:C08-MG{PS:QM2A}I:Sp1-SP",  "SR:C08-MG{PS:QM2B}I:Sp1-SP",  "SR:C08-MG{PS:SH1-DW08}I:Sp1-SP",
                "SR:C08-MG{PS:SH3-DW08}I:Sp1-SP",  "SR:C08-MG{PS:SH4-DW08}I:Sp1-SP",  "SR:C08-MG{PS:SM1B-P3}I:Sp1-SP",  "SR:C08-MG{PS:SM2B-P3}I:Sp1-SP",
                "SR:C08-MG{PS:SQKH1A}I:Sp1-SP",  "SR:C09-MG{PS:BT1A}I:Sp1-SP",  "SR:C09-MG{PS:BT1A}I:Sp2-SP",  "SR:C09-MG{PS:CH1B}I:Sp1-SP",
                "SR:C09-MG{PS:CH1B}I:Sp2-SP",  "SR:C09-MG{PS:CH2B}I:Sp1-SP",  "SR:C09-MG{PS:CH2B}I:Sp2-SP",  "SR:C09-MG{PS:CL1A}I:Sp1-SP",
                "SR:C09-MG{PS:CL1A}I:Sp2-SP",  "SR:C09-MG{PS:CL2A}I:Sp1-SP",  "SR:C09-MG{PS:CL2A}I:Sp2-SP",  "SR:C09-MG{PS:CM1A}I:Sp1-SP",
                "SR:C09-MG{PS:CM1A}I:Sp2-SP",  "SR:C09-MG{PS:CM1B}I:Sp1-SP",  "SR:C09-MG{PS:CM1B}I:Sp2-SP",  "SR:C09-MG{PS:QH1B}I:Sp1-SP",
                "SR:C09-MG{PS:QH2B}I:Sp1-SP",  "SR:C09-MG{PS:QH3B}I:Sp1-SP",  "SR:C09-MG{PS:QL1A}I:Sp1-SP",  "SR:C09-MG{PS:QL2A}I:Sp1-SP",
                "SR:C09-MG{PS:QL3A}I:Sp1-SP",  "SR:C09-MG{PS:QM1A}I:Sp1-SP",  "SR:C09-MG{PS:QM1B}I:Sp1-SP",  "SR:C09-MG{PS:QM2A}I:Sp1-SP",
                "SR:C09-MG{PS:QM2B}I:Sp1-SP",  "SR:C09-MG{PS:SL2-P3}I:Sp1-SP",  "SR:C09-MG{PS:SL3-P3}I:Sp1-SP",  "SR:C09-MG{PS:SQKM1A}I:Sp1-SP",
                "SR:C10-MG{PS:BT1A}I:Sp1-SP",  "SR:C10-MG{PS:BT1A}I:Sp2-SP",  "SR:C10-MG{PS:CH1A}I:Sp1-SP",  "SR:C10-MG{PS:CH1A}I:Sp2-SP",
                "SR:C10-MG{PS:CH2A}I:Sp1-SP",  "SR:C10-MG{PS:CH2A}I:Sp2-SP",  "SR:C10-MG{PS:CL1B}I:Sp1-SP",  "SR:C10-MG{PS:CL1B}I:Sp2-SP",
                "SR:C10-MG{PS:CL2B}I:Sp1-SP",  "SR:C10-MG{PS:CL2B}I:Sp2-SP",  "SR:C10-MG{PS:CM1A}I:Sp1-SP",  "SR:C10-MG{PS:CM1A}I:Sp2-SP",
                "SR:C10-MG{PS:CM1B}I:Sp1-SP",  "SR:C10-MG{PS:CM1B}I:Sp2-SP",  "SR:C10-MG{PS:QH1A}I:Sp1-SP",  "SR:C10-MG{PS:QH2A}I:Sp1-SP",
                "SR:C10-MG{PS:QH3A}I:Sp1-SP",  "SR:C10-MG{PS:QL1B}I:Sp1-SP",  "SR:C10-MG{PS:QL2B}I:Sp1-SP",  "SR:C10-MG{PS:QL3B}I:Sp1-SP",
                "SR:C10-MG{PS:QM1A}I:Sp1-SP",  "SR:C10-MG{PS:QM1B}I:Sp1-SP",  "SR:C10-MG{PS:QM2A}I:Sp1-SP",  "SR:C10-MG{PS:QM2B}I:Sp1-SP",
                "SR:C10-MG{PS:SL1-P3}I:Sp1-SP",  "SR:C10-MG{PS:SQKH1A}I:Sp1-SP",  "SR:C11-MG{PS:BT1A}I:Sp1-SP",  "SR:C11-MG{PS:BT1A}I:Sp2-SP",
                "SR:C11-MG{PS:CH1B}I:Sp1-SP",  "SR:C11-MG{PS:CH1B}I:Sp2-SP",  "SR:C11-MG{PS:CH2B}I:Sp1-SP",  "SR:C11-MG{PS:CH2B}I:Sp2-SP",
                "SR:C11-MG{PS:CL1A}I:Sp1-SP",  "SR:C11-MG{PS:CL1A}I:Sp2-SP",  "SR:C11-MG{PS:CL2A}I:Sp1-SP",  "SR:C11-MG{PS:CL2A}I:Sp2-SP",
                "SR:C11-MG{PS:CM1A}I:Sp1-SP",  "SR:C11-MG{PS:CM1A}I:Sp2-SP",  "SR:C11-MG{PS:CM1B}I:Sp1-SP",  "SR:C11-MG{PS:CM1B}I:Sp2-SP",
                "SR:C11-MG{PS:QH1B}I:Sp1-SP",  "SR:C11-MG{PS:QH2B}I:Sp1-SP",  "SR:C11-MG{PS:QH3B}I:Sp1-SP",  "SR:C11-MG{PS:QL1A}I:Sp1-SP",
                "SR:C11-MG{PS:QL2A}I:Sp1-SP",  "SR:C11-MG{PS:QL3A}I:Sp1-SP",  "SR:C11-MG{PS:QM1A}I:Sp1-SP",  "SR:C11-MG{PS:QM1B}I:Sp1-SP",
                "SR:C11-MG{PS:QM2A}I:Sp1-SP",  "SR:C11-MG{PS:QM2B}I:Sp1-SP",  "SR:C11-MG{PS:SQKM1A}I:Sp1-SP",  "SR:C12-MG{PS:BT1A}I:Sp1-SP",
                "SR:C12-MG{PS:BT1A}I:Sp2-SP",  "SR:C12-MG{PS:CH1A}I:Sp1-SP",  "SR:C12-MG{PS:CH1A}I:Sp2-SP",  "SR:C12-MG{PS:CH2A}I:Sp1-SP",
                "SR:C12-MG{PS:CH2A}I:Sp2-SP",  "SR:C12-MG{PS:CL1B}I:Sp1-SP",  "SR:C12-MG{PS:CL1B}I:Sp2-SP",  "SR:C12-MG{PS:CL2B}I:Sp1-SP",
                "SR:C12-MG{PS:CL2B}I:Sp2-SP",  "SR:C12-MG{PS:CM1A}I:Sp1-SP",  "SR:C12-MG{PS:CM1A}I:Sp2-SP",  "SR:C12-MG{PS:CM1B}I:Sp1-SP",
                "SR:C12-MG{PS:CM1B}I:Sp2-SP",  "SR:C12-MG{PS:QH1A}I:Sp1-SP",  "SR:C12-MG{PS:QH2A}I:Sp1-SP",  "SR:C12-MG{PS:QH3A}I:Sp1-SP",
                "SR:C12-MG{PS:QL1B}I:Sp1-SP",  "SR:C12-MG{PS:QL2B}I:Sp1-SP",  "SR:C12-MG{PS:QL3B}I:Sp1-SP",  "SR:C12-MG{PS:QM1A}I:Sp1-SP",
                "SR:C12-MG{PS:QM1B}I:Sp1-SP",  "SR:C12-MG{PS:QM2A}I:Sp1-SP",  "SR:C12-MG{PS:QM2B}I:Sp1-SP",  "SR:C12-MG{PS:SH1-P4}I:Sp1-SP",
                "SR:C12-MG{PS:SH3-P4}I:Sp1-SP",  "SR:C12-MG{PS:SQKH1A}I:Sp1-SP",  "SR:C13-MG{PS:BT1A}I:Sp1-SP",  "SR:C13-MG{PS:BT1A}I:Sp2-SP",
                "SR:C13-MG{PS:CH1B}I:Sp1-SP",  "SR:C13-MG{PS:CH1B}I:Sp2-SP",  "SR:C13-MG{PS:CH2B}I:Sp1-SP",  "SR:C13-MG{PS:CH2B}I:Sp2-SP",
                "SR:C13-MG{PS:CL1A}I:Sp1-SP",  "SR:C13-MG{PS:CL1A}I:Sp2-SP",  "SR:C13-MG{PS:CL2A}I:Sp1-SP",  "SR:C13-MG{PS:CL2A}I:Sp2-SP",
                "SR:C13-MG{PS:CM1A}I:Sp1-SP",  "SR:C13-MG{PS:CM1A}I:Sp2-SP",  "SR:C13-MG{PS:CM1B}I:Sp1-SP",  "SR:C13-MG{PS:CM1B}I:Sp2-SP",
                "SR:C13-MG{PS:QH1B}I:Sp1-SP",  "SR:C13-MG{PS:QH2B}I:Sp1-SP",  "SR:C13-MG{PS:QH3B}I:Sp1-SP",  "SR:C13-MG{PS:QL1A}I:Sp1-SP",
                "SR:C13-MG{PS:QL2A}I:Sp1-SP",  "SR:C13-MG{PS:QL3A}I:Sp1-SP",  "SR:C13-MG{PS:QM1A}I:Sp1-SP",  "SR:C13-MG{PS:QM1B}I:Sp1-SP",
                "SR:C13-MG{PS:QM2A}I:Sp1-SP",  "SR:C13-MG{PS:QM2B}I:Sp1-SP",  "SR:C13-MG{PS:SH4-P4}I:Sp1-SP",  "SR:C13-MG{PS:SM1A-P4}I:Sp1-SP",
                "SR:C13-MG{PS:SQKM1A}I:Sp1-SP",  "SR:C14-MG{PS:BT1A}I:Sp1-SP",  "SR:C14-MG{PS:BT1A}I:Sp2-SP",  "SR:C14-MG{PS:CH1A}I:Sp1-SP",
                "SR:C14-MG{PS:CH1A}I:Sp2-SP",  "SR:C14-MG{PS:CH2A}I:Sp1-SP",  "SR:C14-MG{PS:CH2A}I:Sp2-SP",  "SR:C14-MG{PS:CL1B}I:Sp1-SP",
                "SR:C14-MG{PS:CL1B}I:Sp2-SP",  "SR:C14-MG{PS:CL2B}I:Sp1-SP",  "SR:C14-MG{PS:CL2B}I:Sp2-SP",  "SR:C14-MG{PS:CM1A}I:Sp1-SP",
                "SR:C14-MG{PS:CM1A}I:Sp2-SP",  "SR:C14-MG{PS:CM1B}I:Sp1-SP",  "SR:C14-MG{PS:CM1B}I:Sp2-SP",  "SR:C14-MG{PS:QH1A}I:Sp1-SP",
                "SR:C14-MG{PS:QH2A}I:Sp1-SP",  "SR:C14-MG{PS:QH3A}I:Sp1-SP",  "SR:C14-MG{PS:QL1B}I:Sp1-SP",  "SR:C14-MG{PS:QL2B}I:Sp1-SP",
                "SR:C14-MG{PS:QL3B}I:Sp1-SP",  "SR:C14-MG{PS:QM1A}I:Sp1-SP",  "SR:C14-MG{PS:QM1B}I:Sp1-SP",  "SR:C14-MG{PS:QM2A}I:Sp1-SP",
                "SR:C14-MG{PS:QM2B}I:Sp1-SP",  "SR:C14-MG{PS:SM1B-P4}I:Sp1-SP",  "SR:C14-MG{PS:SM2B-P4}I:Sp1-SP",  "SR:C14-MG{PS:SQKH1A}I:Sp1-SP",
                "SR:C15-MG{PS:BT1A}I:Sp1-SP",  "SR:C15-MG{PS:BT1A}I:Sp2-SP",  "SR:C15-MG{PS:CH1B}I:Sp1-SP",  "SR:C15-MG{PS:CH1B}I:Sp2-SP",
                "SR:C15-MG{PS:CH2B}I:Sp1-SP",  "SR:C15-MG{PS:CH2B}I:Sp2-SP",  "SR:C15-MG{PS:CL1A}I:Sp1-SP",  "SR:C15-MG{PS:CL1A}I:Sp2-SP",
                "SR:C15-MG{PS:CL2A}I:Sp1-SP",  "SR:C15-MG{PS:CL2A}I:Sp2-SP",  "SR:C15-MG{PS:CM1A}I:Sp1-SP",  "SR:C15-MG{PS:CM1A}I:Sp2-SP",
                "SR:C15-MG{PS:CM1B}I:Sp1-SP",  "SR:C15-MG{PS:CM1B}I:Sp2-SP",  "SR:C15-MG{PS:QH1B}I:Sp1-SP",  "SR:C15-MG{PS:QH2B}I:Sp1-SP",
                "SR:C15-MG{PS:QH3B}I:Sp1-SP",  "SR:C15-MG{PS:QL1A}I:Sp1-SP",  "SR:C15-MG{PS:QL2A}I:Sp1-SP",  "SR:C15-MG{PS:QL3A}I:Sp1-SP",
                "SR:C15-MG{PS:QM1A}I:Sp1-SP",  "SR:C15-MG{PS:QM1B}I:Sp1-SP",  "SR:C15-MG{PS:QM2A}I:Sp1-SP",  "SR:C15-MG{PS:QM2B}I:Sp1-SP",
                "SR:C15-MG{PS:SL2-P4}I:Sp1-SP",  "SR:C15-MG{PS:SL3-P4}I:Sp1-SP",  "SR:C15-MG{PS:SQKM1A}I:Sp1-SP",  "SR:C16-MG{PS:BT1A}I:Sp1-SP",
                "SR:C16-MG{PS:BT1A}I:Sp2-SP",  "SR:C16-MG{PS:CH1A}I:Sp1-SP",  "SR:C16-MG{PS:CH1A}I:Sp2-SP",  "SR:C16-MG{PS:CH2A}I:Sp1-SP",
                "SR:C16-MG{PS:CH2A}I:Sp2-SP",  "SR:C16-MG{PS:CL1B}I:Sp1-SP",  "SR:C16-MG{PS:CL1B}I:Sp2-SP",  "SR:C16-MG{PS:CL2B}I:Sp1-SP",
                "SR:C16-MG{PS:CL2B}I:Sp2-SP",  "SR:C16-MG{PS:CM1A}I:Sp1-SP",  "SR:C16-MG{PS:CM1A}I:Sp2-SP",  "SR:C16-MG{PS:CM1B}I:Sp1-SP",
                "SR:C16-MG{PS:CM1B}I:Sp2-SP",  "SR:C16-MG{PS:QH1A}I:Sp1-SP",  "SR:C16-MG{PS:QH2A}I:Sp1-SP",  "SR:C16-MG{PS:QH3A}I:Sp1-SP",
                "SR:C16-MG{PS:QL1B}I:Sp1-SP",  "SR:C16-MG{PS:QL2B}I:Sp1-SP",  "SR:C16-MG{PS:QL3B}I:Sp1-SP",  "SR:C16-MG{PS:QM1A}I:Sp1-SP",
                "SR:C16-MG{PS:QM1B}I:Sp1-SP",  "SR:C16-MG{PS:QM2A}I:Sp1-SP",  "SR:C16-MG{PS:QM2B}I:Sp1-SP",  "SR:C16-MG{PS:SL1-P4}I:Sp1-SP",
                "SR:C16-MG{PS:SQKH1A}I:Sp1-SP",  "SR:C17-MG{PS:BT1A}I:Sp1-SP",  "SR:C17-MG{PS:BT1A}I:Sp2-SP",  "SR:C17-MG{PS:CH1B}I:Sp1-SP",
                "SR:C17-MG{PS:CH1B}I:Sp2-SP",  "SR:C17-MG{PS:CH2B}I:Sp1-SP",  "SR:C17-MG{PS:CH2B}I:Sp2-SP",  "SR:C17-MG{PS:CL1A}I:Sp1-SP",
                "SR:C17-MG{PS:CL1A}I:Sp2-SP",  "SR:C17-MG{PS:CL2A}I:Sp1-SP",  "SR:C17-MG{PS:CL2A}I:Sp2-SP",  "SR:C17-MG{PS:CM1A}I:Sp1-SP",
                "SR:C17-MG{PS:CM1A}I:Sp2-SP",  "SR:C17-MG{PS:CM1B}I:Sp1-SP",  "SR:C17-MG{PS:CM1B}I:Sp2-SP",  "SR:C17-MG{PS:QH1B}I:Sp1-SP",
                "SR:C17-MG{PS:QH2B}I:Sp1-SP",  "SR:C17-MG{PS:QH3B}I:Sp1-SP",  "SR:C17-MG{PS:QL1A}I:Sp1-SP",  "SR:C17-MG{PS:QL2A}I:Sp1-SP",
                "SR:C17-MG{PS:QL3A}I:Sp1-SP",  "SR:C17-MG{PS:QM1A}I:Sp1-SP",  "SR:C17-MG{PS:QM1B}I:Sp1-SP",  "SR:C17-MG{PS:QM2A}I:Sp1-SP",
                "SR:C17-MG{PS:QM2B}I:Sp1-SP",  "SR:C17-MG{PS:SQKM1A}I:Sp1-SP",  "SR:C18-MG{PS:BT1A}I:Sp1-SP",  "SR:C18-MG{PS:BT1A}I:Sp2-SP",
                "SR:C18-MG{PS:CH1A}I:Sp1-SP",  "SR:C18-MG{PS:CH1A}I:Sp2-SP",  "SR:C18-MG{PS:CH2A}I:Sp1-SP",  "SR:C18-MG{PS:CH2A}I:Sp2-SP",
                "SR:C18-MG{PS:CL1B}I:Sp1-SP",  "SR:C18-MG{PS:CL1B}I:Sp2-SP",  "SR:C18-MG{PS:CL2B}I:Sp1-SP",  "SR:C18-MG{PS:CL2B}I:Sp2-SP",
                "SR:C18-MG{PS:CM1A}I:Sp1-SP",  "SR:C18-MG{PS:CM1A}I:Sp2-SP",  "SR:C18-MG{PS:CM1B}I:Sp1-SP",  "SR:C18-MG{PS:CM1B}I:Sp2-SP",
                "SR:C18-MG{PS:QH1A}I:Sp1-SP",  "SR:C18-MG{PS:QH2A}I:Sp1-SP",  "SR:C18-MG{PS:QH3A}I:Sp1-SP",  "SR:C18-MG{PS:QL1B}I:Sp1-SP",
                "SR:C18-MG{PS:QL2B}I:Sp1-SP",  "SR:C18-MG{PS:QL3B}I:Sp1-SP",  "SR:C18-MG{PS:QM1A}I:Sp1-SP",  "SR:C18-MG{PS:QM1B}I:Sp1-SP",
                "SR:C18-MG{PS:QM2A}I:Sp1-SP",  "SR:C18-MG{PS:QM2B}I:Sp1-SP",  "SR:C18-MG{PS:SH1-DW18}I:Sp1-SP",  "SR:C18-MG{PS:SH1-P5}I:Sp1-SP",
                "SR:C18-MG{PS:SH3-DW18}I:Sp1-SP",  "SR:C18-MG{PS:SH3-P5}I:Sp1-SP",  "SR:C18-MG{PS:SH4-DW18}I:Sp1-SP",  "SR:C18-MG{PS:SQKH1A}I:Sp1-SP",
                "SR:C19-MG{PS:BT1A}I:Sp1-SP",  "SR:C19-MG{PS:BT1A}I:Sp2-SP",  "SR:C19-MG{PS:CH1B}I:Sp1-SP",  "SR:C19-MG{PS:CH1B}I:Sp2-SP",
                "SR:C19-MG{PS:CH2B}I:Sp1-SP",  "SR:C19-MG{PS:CH2B}I:Sp2-SP",  "SR:C19-MG{PS:CL1A}I:Sp1-SP",  "SR:C19-MG{PS:CL1A}I:Sp2-SP",
                "SR:C19-MG{PS:CL2A}I:Sp1-SP",  "SR:C19-MG{PS:CL2A}I:Sp2-SP",  "SR:C19-MG{PS:CM1A}I:Sp1-SP",  "SR:C19-MG{PS:CM1A}I:Sp2-SP",
                "SR:C19-MG{PS:CM1B}I:Sp1-SP",  "SR:C19-MG{PS:CM1B}I:Sp2-SP",  "SR:C19-MG{PS:QH1B}I:Sp1-SP",  "SR:C19-MG{PS:QH2B}I:Sp1-SP",
                "SR:C19-MG{PS:QH3B}I:Sp1-SP",  "SR:C19-MG{PS:QL1A}I:Sp1-SP",  "SR:C19-MG{PS:QL2A}I:Sp1-SP",  "SR:C19-MG{PS:QL3A}I:Sp1-SP",
                "SR:C19-MG{PS:QM1A}I:Sp1-SP",  "SR:C19-MG{PS:QM1B}I:Sp1-SP",  "SR:C19-MG{PS:QM2A}I:Sp1-SP",  "SR:C19-MG{PS:QM2B}I:Sp1-SP",
                "SR:C19-MG{PS:SH4-P5}I:Sp1-SP",  "SR:C19-MG{PS:SM1A-P5}I:Sp1-SP",  "SR:C19-MG{PS:SQKM1A}I:Sp1-SP",  "SR:C20-MG{PS:BT1A}I:Sp1-SP",
                "SR:C20-MG{PS:BT1A}I:Sp2-SP",  "SR:C20-MG{PS:CH1A}I:Sp1-SP",  "SR:C20-MG{PS:CH1A}I:Sp2-SP",  "SR:C20-MG{PS:CH2A}I:Sp1-SP",
                "SR:C20-MG{PS:CH2A}I:Sp2-SP",  "SR:C20-MG{PS:CL1B}I:Sp1-SP",  "SR:C20-MG{PS:CL1B}I:Sp2-SP",  "SR:C20-MG{PS:CL2B}I:Sp1-SP",
                "SR:C20-MG{PS:CL2B}I:Sp2-SP",  "SR:C20-MG{PS:CM1A}I:Sp1-SP",  "SR:C20-MG{PS:CM1A}I:Sp2-SP",  "SR:C20-MG{PS:CM1B}I:Sp1-SP",
                "SR:C20-MG{PS:CM1B}I:Sp2-SP",  "SR:C20-MG{PS:QH1A}I:Sp1-SP",  "SR:C20-MG{PS:QH2A}I:Sp1-SP",  "SR:C20-MG{PS:QH3A}I:Sp1-SP",
                "SR:C20-MG{PS:QL1B}I:Sp1-SP",  "SR:C20-MG{PS:QL2B}I:Sp1-SP",  "SR:C20-MG{PS:QL3B}I:Sp1-SP",  "SR:C20-MG{PS:QM1A}I:Sp1-SP",
                "SR:C20-MG{PS:QM1B}I:Sp1-SP",  "SR:C20-MG{PS:QM2A}I:Sp1-SP",  "SR:C20-MG{PS:QM2B}I:Sp1-SP",  "SR:C20-MG{PS:SM1B-P5}I:Sp1-SP",
                "SR:C20-MG{PS:SM2B-P5}I:Sp1-SP",  "SR:C20-MG{PS:SQKH1A}I:Sp1-SP",  "SR:C21-MG{PS:BT1A}I:Sp1-SP",  "SR:C21-MG{PS:BT1A}I:Sp2-SP",
                "SR:C21-MG{PS:CH1B}I:Sp1-SP",  "SR:C21-MG{PS:CH1B}I:Sp2-SP",  "SR:C21-MG{PS:CH2B}I:Sp1-SP",  "SR:C21-MG{PS:CH2B}I:Sp2-SP",
                "SR:C21-MG{PS:CL1A}I:Sp1-SP",  "SR:C21-MG{PS:CL1A}I:Sp2-SP",  "SR:C21-MG{PS:CL2A}I:Sp1-SP",  "SR:C21-MG{PS:CL2A}I:Sp2-SP",
                "SR:C21-MG{PS:CM1A}I:Sp1-SP",  "SR:C21-MG{PS:CM1A}I:Sp2-SP",  "SR:C21-MG{PS:CM1B}I:Sp1-SP",  "SR:C21-MG{PS:CM1B}I:Sp2-SP",
                "SR:C21-MG{PS:QH1B}I:Sp1-SP",  "SR:C21-MG{PS:QH2B}I:Sp1-SP",  "SR:C21-MG{PS:QH3B}I:Sp1-SP",  "SR:C21-MG{PS:QL1A}I:Sp1-SP",
                "SR:C21-MG{PS:QL2A}I:Sp1-SP",  "SR:C21-MG{PS:QL3A}I:Sp1-SP",  "SR:C21-MG{PS:QM1A}I:Sp1-SP",  "SR:C21-MG{PS:QM1B}I:Sp1-SP",
                "SR:C21-MG{PS:QM2A}I:Sp1-SP",  "SR:C21-MG{PS:QM2B}I:Sp1-SP",  "SR:C21-MG{PS:SL2-P5}I:Sp1-SP",  "SR:C21-MG{PS:SL3-P5}I:Sp1-SP",
                "SR:C21-MG{PS:SQKM1A}I:Sp1-SP",  "SR:C22-MG{PS:BT1A}I:Sp1-SP",  "SR:C22-MG{PS:BT1A}I:Sp2-SP",  "SR:C22-MG{PS:CH1A}I:Sp1-SP",
                "SR:C22-MG{PS:CH1A}I:Sp2-SP",  "SR:C22-MG{PS:CH2A}I:Sp1-SP",  "SR:C22-MG{PS:CH2A}I:Sp2-SP",  "SR:C22-MG{PS:CL1B}I:Sp1-SP",
                "SR:C22-MG{PS:CL1B}I:Sp2-SP",  "SR:C22-MG{PS:CL2B}I:Sp1-SP",  "SR:C22-MG{PS:CL2B}I:Sp2-SP",  "SR:C22-MG{PS:CM1A}I:Sp1-SP",
                "SR:C22-MG{PS:CM1A}I:Sp2-SP",  "SR:C22-MG{PS:CM1B}I:Sp1-SP",  "SR:C22-MG{PS:CM1B}I:Sp2-SP",  "SR:C22-MG{PS:QH1A}I:Sp1-SP",
                "SR:C22-MG{PS:QH2A}I:Sp1-SP",  "SR:C22-MG{PS:QH3A}I:Sp1-SP",  "SR:C22-MG{PS:QL1B}I:Sp1-SP",  "SR:C22-MG{PS:QL2B}I:Sp1-SP",
                "SR:C22-MG{PS:QL3B}I:Sp1-SP",  "SR:C22-MG{PS:QM1A}I:Sp1-SP",  "SR:C22-MG{PS:QM1B}I:Sp1-SP",  "SR:C22-MG{PS:QM2A}I:Sp1-SP",
                "SR:C22-MG{PS:QM2B}I:Sp1-SP",  "SR:C22-MG{PS:SL1-P5}I:Sp1-SP",  "SR:C22-MG{PS:SQKH1A}I:Sp1-SP",  "SR:C23-MG{PS:BT1A}I:Sp1-SP",
                "SR:C23-MG{PS:BT1A}I:Sp2-SP",  "SR:C23-MG{PS:CH1B}I:Sp1-SP",  "SR:C23-MG{PS:CH1B}I:Sp2-SP",  "SR:C23-MG{PS:CH2B}I:Sp1-SP",
                "SR:C23-MG{PS:CH2B}I:Sp2-SP",  "SR:C23-MG{PS:CL1A}I:Sp1-SP",  "SR:C23-MG{PS:CL1A}I:Sp2-SP",  "SR:C23-MG{PS:CL2A}I:Sp1-SP",
                "SR:C23-MG{PS:CL2A}I:Sp2-SP",  "SR:C23-MG{PS:CM1A}I:Sp1-SP",  "SR:C23-MG{PS:CM1A}I:Sp2-SP",  "SR:C23-MG{PS:CM1B}I:Sp1-SP",
                "SR:C23-MG{PS:CM1B}I:Sp2-SP",  "SR:C23-MG{PS:QH1B}I:Sp1-SP",  "SR:C23-MG{PS:QH2B}I:Sp1-SP",  "SR:C23-MG{PS:QH3B}I:Sp1-SP",
                "SR:C23-MG{PS:QL1A}I:Sp1-SP",  "SR:C23-MG{PS:QL2A}I:Sp1-SP",  "SR:C23-MG{PS:QL3A}I:Sp1-SP",  "SR:C23-MG{PS:QM1A}I:Sp1-SP",
                "SR:C23-MG{PS:QM1B}I:Sp1-SP",  "SR:C23-MG{PS:QM2A}I:Sp1-SP",  "SR:C23-MG{PS:QM2B}I:Sp1-SP",  "SR:C23-MG{PS:SQKM1A}I:Sp1-SP",
                "SR:C24-MG{PS:BT1A}I:Sp1-SP",  "SR:C24-MG{PS:BT1A}I:Sp2-SP",  "SR:C24-MG{PS:CH1A}I:Sp1-SP",  "SR:C24-MG{PS:CH1A}I:Sp2-SP",
                "SR:C24-MG{PS:CH2A}I:Sp1-SP",  "SR:C24-MG{PS:CH2A}I:Sp2-SP",  "SR:C24-MG{PS:CL1B}I:Sp1-SP",  "SR:C24-MG{PS:CL1B}I:Sp2-SP",
                "SR:C24-MG{PS:CL2B}I:Sp1-SP",  "SR:C24-MG{PS:CL2B}I:Sp2-SP",  "SR:C24-MG{PS:CM1A}I:Sp1-SP",  "SR:C24-MG{PS:CM1A}I:Sp2-SP",
                "SR:C24-MG{PS:CM1B}I:Sp1-SP",  "SR:C24-MG{PS:CM1B}I:Sp2-SP",  "SR:C24-MG{PS:QH1A}I:Sp1-SP",  "SR:C24-MG{PS:QH2A}I:Sp1-SP",
                "SR:C24-MG{PS:QH3A}I:Sp1-SP",  "SR:C24-MG{PS:QL1B}I:Sp1-SP",  "SR:C24-MG{PS:QL2B}I:Sp1-SP",  "SR:C24-MG{PS:QL3B}I:Sp1-SP",
                "SR:C24-MG{PS:QM1A}I:Sp1-SP",  "SR:C24-MG{PS:QM1B}I:Sp1-SP",  "SR:C24-MG{PS:QM2A}I:Sp1-SP",  "SR:C24-MG{PS:QM2B}I:Sp1-SP",
                "SR:C24-MG{PS:SH1-P1}I:Sp1-SP",  "SR:C24-MG{PS:SH3-P1}I:Sp1-SP",  "SR:C24-MG{PS:SQKH1A}I:Sp1-SP",  "SR:C25-MG{PS:BT1A}I:Sp1-SP",
                "SR:C25-MG{PS:BT1A}I:Sp2-SP",  "SR:C25-MG{PS:CH1B}I:Sp1-SP",  "SR:C25-MG{PS:CH1B}I:Sp2-SP",  "SR:C25-MG{PS:CH2B}I:Sp1-SP",
                "SR:C25-MG{PS:CH2B}I:Sp2-SP",  "SR:C25-MG{PS:CL1A}I:Sp1-SP",  "SR:C25-MG{PS:CL1A}I:Sp2-SP",  "SR:C25-MG{PS:CL2A}I:Sp1-SP",
                "SR:C25-MG{PS:CL2A}I:Sp2-SP",  "SR:C25-MG{PS:CM1A}I:Sp1-SP",  "SR:C25-MG{PS:CM1A}I:Sp2-SP",  "SR:C25-MG{PS:CM1B}I:Sp1-SP",
                "SR:C25-MG{PS:CM1B}I:Sp2-SP",  "SR:C25-MG{PS:QH1B}I:Sp1-SP",  "SR:C25-MG{PS:QH2B}I:Sp1-SP",  "SR:C25-MG{PS:QH3B}I:Sp1-SP",
                "SR:C25-MG{PS:QL1A}I:Sp1-SP",  "SR:C25-MG{PS:QL2A}I:Sp1-SP",  "SR:C25-MG{PS:QL3A}I:Sp1-SP",  "SR:C25-MG{PS:QM1A}I:Sp1-SP",
                "SR:C25-MG{PS:QM1B}I:Sp1-SP",  "SR:C25-MG{PS:QM2A}I:Sp1-SP",  "SR:C25-MG{PS:QM2B}I:Sp1-SP",  "SR:C25-MG{PS:SH4-P1}I:Sp1-SP",
                "SR:C25-MG{PS:SM1A-P1}I:Sp1-SP",  "SR:C25-MG{PS:SQKM1A}I:Sp1-SP",  "SR:C26-MG{PS:BT1A}I:Sp1-SP",  "SR:C26-MG{PS:BT1A}I:Sp2-SP",
                "SR:C26-MG{PS:CH1A}I:Sp1-SP",  "SR:C26-MG{PS:CH1A}I:Sp2-SP",  "SR:C26-MG{PS:CH2A}I:Sp1-SP",  "SR:C26-MG{PS:CH2A}I:Sp2-SP",
                "SR:C26-MG{PS:CL1B}I:Sp1-SP",  "SR:C26-MG{PS:CL1B}I:Sp2-SP",  "SR:C26-MG{PS:CL2B}I:Sp1-SP",  "SR:C26-MG{PS:CL2B}I:Sp2-SP",
                "SR:C26-MG{PS:CM1A}I:Sp1-SP",  "SR:C26-MG{PS:CM1A}I:Sp2-SP",  "SR:C26-MG{PS:CM1B}I:Sp1-SP",  "SR:C26-MG{PS:CM1B}I:Sp2-SP",
                "SR:C26-MG{PS:QH1A}I:Sp1-SP",  "SR:C26-MG{PS:QH2A}I:Sp1-SP",  "SR:C26-MG{PS:QH3A}I:Sp1-SP",  "SR:C26-MG{PS:QL1B}I:Sp1-SP",
                "SR:C26-MG{PS:QL2B}I:Sp1-SP",  "SR:C26-MG{PS:QL3B}I:Sp1-SP",  "SR:C26-MG{PS:QM1A}I:Sp1-SP",  "SR:C26-MG{PS:QM1B}I:Sp1-SP",
                "SR:C26-MG{PS:QM2A}I:Sp1-SP",  "SR:C26-MG{PS:QM2B}I:Sp1-SP",  "SR:C26-MG{PS:SM1B-P1}I:Sp1-SP",  "SR:C26-MG{PS:SM2B-P1}I:Sp1-SP",
                "SR:C26-MG{PS:SQKH1A}I:Sp1-SP",  "SR:C27-MG{PS:BT1A}I:Sp1-SP",  "SR:C27-MG{PS:BT1A}I:Sp2-SP",  "SR:C27-MG{PS:CH1B}I:Sp1-SP",
                "SR:C27-MG{PS:CH1B}I:Sp2-SP",  "SR:C27-MG{PS:CH2B}I:Sp1-SP",  "SR:C27-MG{PS:CH2B}I:Sp2-SP",  "SR:C27-MG{PS:CL1A}I:Sp1-SP",
                "SR:C27-MG{PS:CL1A}I:Sp2-SP",  "SR:C27-MG{PS:CL2A}I:Sp1-SP",  "SR:C27-MG{PS:CL2A}I:Sp2-SP",  "SR:C27-MG{PS:CM1A}I:Sp1-SP",
                "SR:C27-MG{PS:CM1A}I:Sp2-SP",  "SR:C27-MG{PS:CM1B}I:Sp1-SP",  "SR:C27-MG{PS:CM1B}I:Sp2-SP",  "SR:C27-MG{PS:QH1B}I:Sp1-SP",
                "SR:C27-MG{PS:QH2B}I:Sp1-SP",  "SR:C27-MG{PS:QH3B}I:Sp1-SP",  "SR:C27-MG{PS:QL1A}I:Sp1-SP",  "SR:C27-MG{PS:QL2A}I:Sp1-SP",
                "SR:C27-MG{PS:QL3A}I:Sp1-SP",  "SR:C27-MG{PS:QM1A}I:Sp1-SP",  "SR:C27-MG{PS:QM1B}I:Sp1-SP",  "SR:C27-MG{PS:QM2A}I:Sp1-SP",
                "SR:C27-MG{PS:QM2B}I:Sp1-SP",  "SR:C27-MG{PS:SL2-P1}I:Sp1-SP",  "SR:C27-MG{PS:SL3-P1}I:Sp1-SP",  "SR:C27-MG{PS:SQKM1A}I:Sp1-SP",
                "SR:C28-MG{PS:BT1A}I:Sp1-SP",  "SR:C28-MG{PS:BT1A}I:Sp2-SP",  "SR:C28-MG{PS:CH1A}I:Sp1-SP",  "SR:C28-MG{PS:CH1A}I:Sp2-SP",
                "SR:C28-MG{PS:CH2A}I:Sp1-SP",  "SR:C28-MG{PS:CH2A}I:Sp2-SP",  "SR:C28-MG{PS:CL1B}I:Sp1-SP",  "SR:C28-MG{PS:CL1B}I:Sp2-SP",
                "SR:C28-MG{PS:CL2B}I:Sp1-SP",  "SR:C28-MG{PS:CL2B}I:Sp2-SP",  "SR:C28-MG{PS:CM1A}I:Sp1-SP",  "SR:C28-MG{PS:CM1A}I:Sp2-SP",
                "SR:C28-MG{PS:CM1B}I:Sp1-SP",  "SR:C28-MG{PS:CM1B}I:Sp2-SP",  "SR:C28-MG{PS:QH1A}I:Sp1-SP",  "SR:C28-MG{PS:QH2A}I:Sp1-SP",
                "SR:C28-MG{PS:QH3A}I:Sp1-SP",  "SR:C28-MG{PS:QL1B}I:Sp1-SP",  "SR:C28-MG{PS:QL2B}I:Sp1-SP",  "SR:C28-MG{PS:QL3B}I:Sp1-SP",
                "SR:C28-MG{PS:QM1A}I:Sp1-SP",  "SR:C28-MG{PS:QM1B}I:Sp1-SP",  "SR:C28-MG{PS:QM2A}I:Sp1-SP",  "SR:C28-MG{PS:QM2B}I:Sp1-SP",
                "SR:C28-MG{PS:SH1-DW28}I:Sp1-SP",  "SR:C28-MG{PS:SH3-DW28}I:Sp1-SP",  "SR:C28-MG{PS:SH4-DW28}I:Sp1-SP",  "SR:C28-MG{PS:SL1-P1}I:Sp1-SP",
                "SR:C28-MG{PS:SQKH1A}I:Sp1-SP",  "SR:C29-MG{PS:BT1A}I:Sp1-SP",  "SR:C29-MG{PS:BT1A}I:Sp2-SP",  "SR:C29-MG{PS:CH1B}I:Sp1-SP",
                "SR:C29-MG{PS:CH1B}I:Sp2-SP",  "SR:C29-MG{PS:CH2B}I:Sp1-SP",  "SR:C29-MG{PS:CH2B}I:Sp2-SP",  "SR:C29-MG{PS:CL1A}I:Sp1-SP",
                "SR:C29-MG{PS:CL1A}I:Sp2-SP",  "SR:C29-MG{PS:CL2A}I:Sp1-SP",  "SR:C29-MG{PS:CL2A}I:Sp2-SP",  "SR:C29-MG{PS:CM1A}I:Sp1-SP",
                "SR:C29-MG{PS:CM1A}I:Sp2-SP",  "SR:C29-MG{PS:CM1B}I:Sp1-SP",  "SR:C29-MG{PS:CM1B}I:Sp2-SP",  "SR:C29-MG{PS:QH1B}I:Sp1-SP",
                "SR:C29-MG{PS:QH2B}I:Sp1-SP",  "SR:C29-MG{PS:QH3B}I:Sp1-SP",  "SR:C29-MG{PS:QL1A}I:Sp1-SP",  "SR:C29-MG{PS:QL2A}I:Sp1-SP",
                "SR:C29-MG{PS:QL3A}I:Sp1-SP",  "SR:C29-MG{PS:QM1A}I:Sp1-SP",  "SR:C29-MG{PS:QM1B}I:Sp1-SP",  "SR:C29-MG{PS:QM2A}I:Sp1-SP",
                "SR:C29-MG{PS:QM2B}I:Sp1-SP",  "SR:C29-MG{PS:SQKM1A}I:Sp1-SP",  "SR:C30-MG{PS:BT1A}I:Sp1-SP",  "SR:C30-MG{PS:BT1A}I:Sp2-SP",
                "SR:C30-MG{PS:CH1A}I:Sp1-SP",  "SR:C30-MG{PS:CH1A}I:Sp2-SP",  "SR:C30-MG{PS:CH2A}I:Sp1-SP",  "SR:C30-MG{PS:CH2A}I:Sp2-SP",
                "SR:C30-MG{PS:CL1B}I:Sp1-SP",  "SR:C30-MG{PS:CL1B}I:Sp2-SP",  "SR:C30-MG{PS:CL2B}I:Sp1-SP",  "SR:C30-MG{PS:CL2B}I:Sp2-SP",
                "SR:C30-MG{PS:CM1A}I:Sp1-SP",  "SR:C30-MG{PS:CM1A}I:Sp2-SP",  "SR:C30-MG{PS:CM1B}I:Sp1-SP",  "SR:C30-MG{PS:CM1B}I:Sp2-SP",
                "SR:C30-MG{PS:QH1A}I:Sp1-SP",  "SR:C30-MG{PS:QH2A}I:Sp1-SP",  "SR:C30-MG{PS:QH3A}I:Sp1-SP",  "SR:C30-MG{PS:QL1B}I:Sp1-SP",
                "SR:C30-MG{PS:QL2B}I:Sp1-SP",  "SR:C30-MG{PS:QL3B}I:Sp1-SP",  "SR:C30-MG{PS:QM1A}I:Sp1-SP",  "SR:C30-MG{PS:QM1B}I:Sp1-SP",
                "SR:C30-MG{PS:QM2A}I:Sp1-SP",  "SR:C30-MG{PS:QM2B}I:Sp1-SP",  "SR:C30-MG{PS:SH1-P2}I:Sp1-SP",  "SR:C30-MG{PS:SH3-P2}I:Sp1-SP",
                "SR:C30-MG{PS:SQKH1A}I:Sp1-SP"]
        pvs0 =['SR:C01-MG{PS:SM1A-P2}I:Sp1-SP', 'SR:C02-MG{PS:SM1B-P2}I:Sp1-SP',
               'SR:C02-MG{PS:SM2B-P2}I:Sp1-SP', 'SR:C07-MG{PS:SM1A-P3}I:Sp1-SP',
               'SR:C08-MG{PS:SM1B-P3}I:Sp1-SP', 'SR:C08-MG{PS:SM2B-P3}I:Sp1-SP',
               'SR:C13-MG{PS:SM1A-P4}I:Sp1-SP', 'SR:C14-MG{PS:SM1B-P4}I:Sp1-SP',
               'SR:C14-MG{PS:SM2B-P4}I:Sp1-SP', 'SR:C19-MG{PS:SM1A-P5}I:Sp1-SP',
               'SR:C20-MG{PS:SM1B-P5}I:Sp1-SP', 'SR:C20-MG{PS:SM2B-P5}I:Sp1-SP',
               'SR:C25-MG{PS:SM1A-P1}I:Sp1-SP', 'SR:C26-MG{PS:SM1B-P1}I:Sp1-SP',
               'SR:C26-MG{PS:SM2B-P1}I:Sp1-SP']
        
        with self.assertRaises(KeyError) as context:
            updateconfig(self.conn, self.collection, name, pvlist={"name": pvs0})
        self.assertEqual(context.exception.message, 'Cannot find key ("names") for pv names.')
        
        self.assertTrue(updateconfig(self.conn, self.collection, name, pvlist={"names": pvs}))
        res3 = retrieveconfig(self.conn, self.collection, name, withpvs=True)
        self.assertEqual(res3[0]["status"], "active")
        self.assertNotEqual(res1[0]["updated_on"], res2[0]["updated_on"])
        self.assertEqual(res3[0]["created_on"], res0[0]["created_on"])
        self.assertEqual(res3[0]["pvlist"]["names"], pvs)
        with self.assertRaises(RuntimeError) as context:
            updateconfig(self.conn, self.collection, name, pvlist={"names": pvs0})
        self.assertEqual(context.exception.message, "PV collection list exists already, and should not be changed.")
        
        #print res3, 
        #print "server: ", res3[0]['_id'].generation_time 
        #print "client: ", res3[0]['created_on']

    def testSaveEvents(self):
        name = 'SR-All-20140326'
        params = {"desc": "SR daily SCR setpoint: SR and IS PS, RF",
                  "system": "SR",
                  "status": "inactive",
                  "version": 20140326,
                  }
        newid = saveconfig(self.conn, self.collection, name, **params)
        new = retrieveconfig(self.conn, self.collection, name=name)
        self.assertEqual(len(new), 1,
                         "Should find only one entry instead of %s"%len(new))
        configidx = new[0]["configidx"]

        with self.assertRaises(RuntimeError) as context:
            eventid = saveevent(self.conn,
                                self.collection,
                                configidx=configidx,
                                comment="good snapshot",
                                approval=True,
                                masar_data=None,
                                username="name")
        self.assertEqual(context.exception.message, "Data set can not be empty.")

        with self.assertRaises(RuntimeError) as context:
            eventid = saveevent(self.conn,
                                self.collection,
                                configidx=None,
                                comment="good snapshot",
                                approval=True,
                                masar_data=["element"],
                                username="name")
        self.assertEqual(context.exception.message, "Cannot identify configuration index number.")

        with self.assertRaises(ValueError) as context:
            eventid = saveevent(self.conn,
                                self.collection,
                                configidx=-1,
                                comment="good snapshot",
                                approval=True,
                                masar_data=["element"],
                                username="name")
        self.assertEqual(context.exception.message, "Unknown configuration index number (%s)" % str(-1))

        eventid = saveevent(self.conn,
                            self.collection,
                            configidx=configidx,
                            comment="good snapshot",
                            approval=True,
                            masar_data=["element"],
                            username="name")
        self.assertNotEqual(eventid, None)

    def testRetrieveEvents(self):
        name = 'SR-All-20140326'
        test_comment = "test"
        test_approval = True
        test_username = "name"
        test_masar_data = [0]
        params = {"desc": "SR daily SCR setpoint: SR and IS PS, RF",
                  "system": "SR",
                  "status": "inactive",
                  "version": 20140326,
                  }
        newid = saveconfig(self.conn, self.collection, name, **params)
        new = retrieveconfig(self.conn, self.collection, name=name)
        self.assertEqual(len(new), 1,
                         "Should find only one entry instead of %s" % len(new))
        configidx = new[0]["configidx"]
        eventid = saveevent(self.conn,
                            self.collection,
                            configidx=configidx,
                            comment=test_comment,
                            approval=test_approval,
                            masar_data=test_masar_data,
                            username=test_username)
        self.assertNotEqual(eventid, None)
        result = retrieveevents(self.conn,
                                self.collection,
                                configidx=configidx,
                                eventidx=eventid,
                                approval=test_approval,
                                comment=test_comment,
                                username=test_username)
        self.assertEqual(result[0]["eventidx"], eventid)
        self.assertEqual(result[0]["configidx"], configidx)
        self.assertEqual(result[0]["comment"], test_comment)
        self.assertEqual(result[0]["approval"], test_approval)
        self.assertEqual(result[0]["username"], test_username)

    def testUpdateEvents(self):
        name = 'SR-All-20140326'
        test_comment = "test"
        updated_comment = "updated"
        test_approval = True
        updated_approval = False
        test_username = "name"
        updated_username = "newname"
        test_masar_data = [0]
        params = {"desc": "SR daily SCR setpoint: SR and IS PS, RF",
                  "system": "SR",
                  "status": "inactive",
                  "version": 20140326,
                  }
        newid = saveconfig(self.conn, self.collection, name, **params)
        new = retrieveconfig(self.conn, self.collection, name=name)
        self.assertEqual(len(new), 1,
                         "Should find only one entry instead of %s" % len(new))
        configidx = new[0]["configidx"]
        eventid = saveevent(self.conn,
                            self.collection,
                            configidx=configidx,
                            comment=test_comment,
                            approval=test_approval,
                            masar_data=test_masar_data,
                            username=test_username)
        self.assertNotEqual(eventid, None)
        with self.assertRaises(RuntimeError) as context:
            result = updateevent(self.conn,
                                 self.collection,
                                 configidx=None,
                                 comment=updated_comment,
                                 approval=updated_approval,
                                 username=updated_username)
        self.assertEqual(context.exception.message, "Unknown MASAR event to update.")
        with self.assertRaises(RuntimeError) as context:
            result = updateevent(self.conn,
                                 self.collection,
                                 eventidx=eventid)
        self.assertEqual(context.exception.message, "No fields to update.")
        result = updateevent(self.conn,
                             self.collection,
                             eventidx=eventid,
                             comment=updated_comment,
                             approval=updated_approval,
                             username=updated_username)
        self.assertTrue(result)

    def testRetrieveSnapshot(self):
        name = 'SR-All-20140326'
        test_comment = "test"
        test_approval = True
        test_username = "name"
        test_masar_data = [0]
        params = {"desc": "SR daily SCR setpoint: SR and IS PS, RF",
                  "system": "SR",
                  "status": "inactive",
                  "version": 20140326,
                  }
        newid = saveconfig(self.conn, self.collection, name, **params)
        new = retrieveconfig(self.conn, self.collection, name=name)
        self.assertEqual(len(new), 1,
                         "Should find only one entry instead of %s" % len(new))
        configidx = new[0]["configidx"]
        eventid = saveevent(self.conn,
                            self.collection,
                            configidx=configidx,
                            comment=test_comment,
                            approval=test_approval,
                            masar_data=test_masar_data,
                            username=test_username)
        self.assertNotEqual(eventid, None)
        result = retrievesnapshot(self.conn,
                                  self.collection,
                                  eventidx=eventid)
        self.assertEqual(result["eventidx"], eventid)
        self.assertEqual(result["configidx"], configidx)
        self.assertEqual(result["comment"], test_comment)
        self.assertEqual(result["approval"], test_approval)
        self.assertEqual(result["username"], test_username)
        self.assertEqual(result["masar_data"], test_masar_data)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

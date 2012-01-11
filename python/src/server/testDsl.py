import dslPY as dsl
import datetime

test = dsl.DSL();

def testSaveMasar():
    func = 'saveMasar'
    params = {'servicename': 'masar',
              'configname': 'test',
              'comment': 'this is a comment'
              }
    
    result = test.request(func, params)
    print "result: ", result

def testRetrieveMasar():
    func = 'retrieveMasar'
    params = {'eventid': 1}
    result = test.request(func, params)
    print "result: ", result

def testRetrieveServiceEvents():
    func = 'retrieveServiceEvents'
    params = {'configid': 0,
              'start': datetime.datetime.utcnow(),
              'end': datetime.datetime.utcnow()
              }
    result = test.request(func, params)
    print "result: ", result

def testRetrieveServiceConfigs():
    func = 'retrieveServiceConfigs'
    params = {'configname': 'sr', 
              'system': 'sr'
              }
    result = test.request(func, params)
    print "result: ", result

def testRetrieveServiceConfigProps():
    func = 'retrieveServiceConfigProps'
    params = {'propname': 'system', 
              'configname': 'sr_qs'
              }
    result = test.request(func, params)
    print "result: ", result

if __name__ == '__main__':
    testSaveMasar()
    testRetrieveMasar()
    testRetrieveServiceEvents()
    testRetrieveServiceConfigs()
    testRetrieveServiceConfigProps()

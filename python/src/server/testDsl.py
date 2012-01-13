import dslPY as dsl
import datetime

test = dsl.DSL();

def testSaveMasar():
    params = {'function': 'saveMasar',
              'servicename': 'masar',
              'configname': 'test',
              'comment': 'this is a comment'
              }
    
    result = test.request(params)
    print "saveMasar: ", result

def testRetrieveMasar():
    params = {'function': 'retrieveMasar',
              'eventid': '56'}
#              'eventid': '35'}

    result = test.request(params)
    print "retrieveMasar: ", len(result), len(result[0]), len(result[0][0]), result
    print "retrieveMasar: ", type(result[0]), result[0]
    print "retrieveMasar: ", type(result[0][0]), result[0][0]
    print "retrieveMasar: ", type(result[0][0][0]), result[0][0][0]
    
def testRetrieveServiceEvents():
    params = {'function': 'retrieveServiceEvents',
              'configid': '1'
              }
    result = test.request(params)
    print "retrieveServiceEvents: ", result

def testRetrieveServiceConfigs():
    params = {'function': 'retrieveServiceConfigs',
              'system': 'sr'
              }
    result = test.request(params)
    print "retrieveServiceConfigs: ", len(result[0]), result

def testRetrieveServiceConfigProps():
    params = {'function': 'retrieveServiceConfigProps',
              'propname': 'system', 
              'configname': 'sr_qs'
              }
    result = test.request(params)
    print "retrieveServiceConfigProps: ", result

if __name__ == '__main__':
#    testSaveMasar()
#    testRetrieveMasar()
    testRetrieveServiceEvents()
    testRetrieveServiceConfigs()
    testRetrieveServiceConfigProps()

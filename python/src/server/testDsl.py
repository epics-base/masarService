import dslPY as dsl

test = dsl.DSL();

def testSaveSnapshot():
    params = {'function': 'saveSnapshot',
              'servicename': 'masar',
              'configname': 'test',
              'comment': 'this is a comment'
              }
    
    result = test.request(params)
    print "saveSnapshot: ", result

def testRetrieveSnapshot(**kws):
    params = {'function': 'retrieveSnapshot'}
    params.update(kws)
    results = test.request(params)
#    print "retrieveSnapshot: ", len(results), len(results[0]), len(results[0][0]), results
#    print "retrieveSnapshot: ", type(results[0]), results[0]
#    print "retrieveSnapshot: ", type(results[0][0]), results[0][0]
#    print "retrieveSnapshot: ", type(results[0][0][0]), results[0][0][0]
    for result in results[0][1]:
        print result
    
def testRetrieveServiceEvents():
    params = {'function': 'retrieveServiceEvents',
              'configid': '1'
              }
    results = test.request(params)
    print "retrieveServiceEvents: " , len(results[0])
    for result in results[0]:
        print result

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

def testRetrieveServiceConfigPVs():
    params = {'function': 'retrieveServiceConfigPVs',
              'configname': 'sr_bpm',
              'servicename': 'masar'
              }
    result = test.retrieveChannelNames(params)
    print "retrieveServiceConfigProps: "
    print len(result)
    print result

if __name__ == '__main__':
#    testRetrieveServiceConfigs()
#    testRetrieveServiceConfigProps()
#    testRetrieveServiceEvents()
#    testRetrieveSnapshot(eventid='365')
    testRetrieveServiceConfigPVs()
#    testRetrieveSnapshot(eventid='35')
#    testRetrieveSnapshot(eventid='10')
#
#    testSaveSnapshot()

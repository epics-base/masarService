import logging
logging.basicConfig(level=logging.DEBUG)

from p4p.nt import NTTable
from p4p.client.thread import Context
from minimasar.client import MASAR, configType

ctxt = Context('pva')
M = MASAR(ctxt, 'masarService:')

conf = configType.wrap([
	{'channelName':'foo1'},
	{'channelName':'foo2'},
])

oldidx = None

for row in NTTable.unwrap(M.retrieveServiceConfigs(configname='example', status='active')):
    # result has at most one row
    print('oldidx', oldidx, row)
    assert oldidx is None, oldidx
    oldidx = row['config_idx']

print 'Create/Update config example'
newConf = M.storeServiceConfig(configname='example', oldidx=oldidx, config=conf)

idx = newConf.value.config_idx[0]

print M.loadServiceConfig(configid=idx)

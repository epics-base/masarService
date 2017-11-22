
from random import random, randint, choice

import numpy

from ..ops import multiType
from p4p.wrapper import Value

def rand_str():
    N = randint(0, 10) # inclusive
    return ''.join([choice('abcdefghijklmnopqrstufwxyz') for n in range(N)])

def rand_int():
    return randint(-10, 10)

def rand_flt():
    return random()*10.0-5.0

#define DBF_STRING  0
#define DBF_INT     1
#define DBF_SHORT   1
#define DBF_FLOAT   2
#define DBF_ENUM    3
#define DBF_CHAR    4
#define DBF_LONG    5
#define DBF_DOUBLE  6

_randval = {
    0:rand_str,
    1:rand_int,
    2:rand_flt,
    3:rand_int,
    4:rand_int,
    5:rand_int,
    6:rand_flt,
}

_constval = {
    0:lambda: "hello world",
    1:lambda: 42,
    2:lambda: 4.2,
    3:lambda: 42,
    4:lambda: 42,
    5:lambda: 42,
    6:lambda: 4.2,
}

_kinds = [
    (':str:', 0),
    (':i16:', 1),
    (':f32:', 2),
    (':e16:', 3),
    (':u8:' , 4),
    (':i32:', 5),
    (':f64:', 6),
]

class Gatherer(object):
    def __init__(self, queue=None):
        pass
    def gather(self, pvs):
        ret = {
            'value':[],
            'channelName':pvs,
            'severity': [],
            'status': [],
            'message': ['']*len(pvs),
            'secondsPastEpoch': [12345678]*len(pvs),
            'nanoseconds': [0]*len(pvs),
            'userTag': [0]*len(pvs),
            'isConnected': [],
            'dbrType': [],
            'readonly': [False]*len(pvs),
            'groupName': ['']*len(pvs),
            'tags': ['']*len(pvs),
        }
        for pv in pvs:
            done=False
            for S,K in _kinds:
                if pv.find(S)==-1:
                    continue
                M = _constval if pv.find(':c:')!=-1 else _randval
                fn = M[K]
                done = True

                #TODO Union handling in p4p means that field types don't match dbrType (eg. double for DBF_FLOAT)

                if pv.find(':a:')==-1:
                    ret['value'].append(fn())
                else:
                    N = randint(0, 10)
                    ret['value'].append(numpy.asarray([fn() for n in range(N)]))

                ret['severity'].append(0)
                ret['status'].append(0)
                ret['dbrType'].append(K)
                ret['isConnected'].append(True)
                break

            if not done:
                ret['value'].append(0)
                ret['severity'].append(4)
                ret['status'].append(0)
                ret['dbrType'].append(7)
                ret['isConnected'].append(False)

        return Value(multiType, ret)

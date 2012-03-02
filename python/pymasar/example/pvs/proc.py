import os
from cothread.catools import *
import random

f = open('example.txt', 'r')
lines1 = f.readlines()
f.close()

f = open('exampleWf.txt', 'r')
lines2 = f.readlines()
f.close()

def initpv(pvlists):
    pvs = []
    values = []
    for pv in pvlists:
        pvs.append(pv+'.PROC')
        values.append(1)
    caput(pvs, values)

scalarpvs = []
wfpvs = []
for line in lines1:
    scalarpvs.append(line[:-1])
for line in lines2:
    wfpvs.append(line[:-1])

initpv(scalarpvs)
initpv(wfpvs)

bigarray = ['masarExampleBigArray01', 
    'masarExampleBigArray02',
    'masarExampleBigArray03',
    'masarExampleBigArray04',
    'masarExampleBigArray05',
    'masarExampleBigArray06',
    'masarExampleBigArray07',
    'masarExampleBigArray08',
    'masarExampleBigArray09',
    'masarExampleBigArray10',
    'masarExampleDoubleArray']
arrayval = []
for pv in bigarray:
    nelm = (int) (caget(pv+'.NELM'))
    array = []
    for i in range(nelm):
        array.append(random.uniform(-5.0, 5.0))
    arrayval.append(array)

caput(bigarray, arrayval)

smallarray = ['masarExampleCharArray',
    'masarExampleLongArray',
    'masarExampleStringArray']

#'abcdefghijkl', 
sarrayval = [[97,98,99,100,101,102,103,104,105,106,107,108,109,110],
             [1000,2000,3000,4000,5000,6000,7000,8000,9000,9999],
             ['aaaaa','bbbbb','ccccc','ddddd','eeeee','fffff','ggggg','hhhhh','iiiii','jjjjj']]
caput(smallarray, sarrayval)


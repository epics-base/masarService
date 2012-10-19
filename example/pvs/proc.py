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

# double, float 
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
    'masarExampleFloatArray',
    'masarExampleDoubleArray']
arrayval = []
for pv in bigarray:
    nelm = (int) (caget(pv+'.NELM'))
    array = []
    for i in range(nelm):
        array.append(random.uniform(-5.0, 5.0))
    arrayval.append(array)
caput(bigarray, arrayval)

# char, short, int, and long
intarraypv = ['masarExampleCharArray',
    'masarExampleShortArray',
    'masarExampleLongArray']
chararray = []
nelm=(int) (caget(intarraypv[0]+'.NELM'))
for i in range(nelm):
    chararray.append(random.randrange(-128,128))
nelm = (int) (caget(intarraypv[1]+'.NELM'))
intarray = []
for i in range(nelm):
    intarray.append(random.randrange(-32768, 32768))
nelm = (int) (caget(intarraypv[2]+'.NELM'))
longarray = []
for i in range(nelm):
    longarray.append(random.randrange(-2147483648, 2147483648))
array=[]
array.append(chararray)
array.append(intarray)
array.append(longarray)
caput(intarraypv, array)

# unsigned char, short, int, and long
uintarraypv = ['masarExampleUCharArray',
    'masarExampleUShortArray',
    'masarExampleULongArray']
uchararray = []
nelm=(int) (caget(uintarraypv[0]+'.NELM'))
for i in range(nelm):
    uchararray.append(random.randrange(0,256))
nelm = (int) (caget(uintarraypv[1]+'.NELM'))
uintarray = []
for i in range(nelm):
    uintarray.append(random.randrange(0, 65536))
nelm = (int) (caget(uintarraypv[2]+'.NELM'))
ulongarray = []
for i in range(nelm):
    ulongarray.append(random.randrange(0, 4294967296))
uarray=[]
uarray.append(uchararray)
uarray.append(uintarray)
uarray.append(ulongarray)
caput(uintarraypv, uarray)

# string
stringpv = 'masarExampleStringArray'
strpvval = ['aaaaa','bbbbb','ccccc','ddddd','eeeee','fffff','ggggg','hhhhh','iiiii','jjjjj']
caput(stringpv, strpvval)

pvscalar = [
    'masarExample0000',
    'masarExample0001',
    'masarExample0002',
    'masarExample0003',
    'masarExample0004',
    'masarExample0005']
pvscalarval = [12, 'another value', 'one', 'zero', 3.8, 0.5]
caput(pvscalar, pvscalarval)

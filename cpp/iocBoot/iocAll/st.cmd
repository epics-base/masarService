#!../../bin/linux-x86/example

## You may have to change example to something else
## everywhere it appears in this file

< envPaths

epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES","450000")

cd ${TOP}

## Register all support components
dbLoadDatabase "dbd/example.dbd"
example_registerRecordDeviceDriver pdbbase

## Load record instances
dbLoadRecords "db/masarExamplePart1.db"
dbLoadRecords "db/masarExamplePart2.db"
dbLoadRecords "db/largeWf.db"

## Run this to trace the stages of iocInit
#traceIocInit

cd ${TOP}/iocBoot/${IOC}
iocInit

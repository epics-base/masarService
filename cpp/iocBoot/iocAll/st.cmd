#!../../bin/linux-x86/example

## You may have to change example to something else
## everywhere it appears in this file

< envPaths

cd ${TOP}

## Register all support components
dbLoadDatabase "dbd/example.dbd"
example_registerRecordDeviceDriver pdbbase

## Load record instances
dbLoadRecords "db/masarExamplePart1.db"
dbLoadRecords "db/masarExamplePart2.db"


## Run this to trace the stages of iocInit
#traceIocInit

cd ${TOP}/iocBoot/${IOC}
iocInit

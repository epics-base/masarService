
epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES","450000")

## Load record instances
## dbLoadRecords "db/masarExamplePart1.db"
## dbLoadRecords "db/masarExamplePart2.db"
## dbLoadRecords "db/masarExamplePart3.db"
## dbLoadRecords "db/largeWf.db"
dbLoadRecords "test_db/masarTestDB.db"

iocInit

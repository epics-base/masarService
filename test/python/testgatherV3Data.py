from masarclient.gatherV3Data import GatherV3Data as GatherV3Data

if __name__ == '__main__':
    names = (
        'masarExample0000',
        'masarExample0001',
        'masarExample0002',
        'masarExample0004',
        'masarExampleCharArray',
        'masarExampleStringArray',
        'masarExampleLongArray',
        'masarExampleDoubleArray',
        )
    gatherV3Data = GatherV3Data(names)
    nttable = gatherV3Data.getNTTable()
    gatherV3Data.connect(2.0)
    gatherV3Data.get()
    print nttable
    

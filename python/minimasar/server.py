
import logging
_log = logging.getLogger(__name__)

from importlib import import_module

from p4p.server import Server, installProvider
from p4p.rpc import WorkQueue, MASARDispatcher, NTURIDispatcher

def getargs():
    from argparse import ArgumentParser
    P = ArgumentParser()
    # db argument is ignored when specifying dbengine to postgres. 
    P.add_argument('db', help='File name of sqlite .db file (or ":memory:")')
    P.add_argument('--dbengine', default='sqlite', help='DB engine type [sqlite|postgres]')
    P.add_argument('--name', default='masarService', help='Service name')
    P.add_argument('-L', '--log-level', default='INFO', help='Level name (eg. ERROR, WARN, INFO, DEBUG)')
    P.add_argument('-G', '--gather', default='ca', help='PV value gathering backend')
    return P.parse_args()

def main(args):      
    
    lvl = logging.getLevelName(args.log_level)
    if isinstance(lvl, str):
        raise ValueError("Bad level name, must be eg. ERROR, WARN, INFO, DEBUG")

    logging.basicConfig(level=lvl)

    Q = WorkQueue(maxsize=5)
    
    if args.dbengine == "sqlite":
        moduleSuffix = '';
    elif args.dbengine == "postgres":
        moduleSuffix = '_postgres';
    else:
        raise RuntimeError('Unsupported DB type specified')
    
    _log.debug('Loading DB module "%s"', 'minimasar.db' + moduleSuffix )
    dbModule = import_module('minimasar.db' + moduleSuffix)
    _log.debug('Loading ops module "%s"', 'minimasar.ops' + moduleSuffix )
    opsModule = import_module('minimasar.ops' + moduleSuffix)
    
    # This repeats above if clauses, but is backwards compatible with respect to the
    # command used to start the server.
    if args.dbengine == "sqlite":
        db = dbModule.connect(args.db)
    elif args.dbengine == "postgres":
        db = dbModule.connect();

    GM = 'minimasar.gather.'+args.gather
    _log.debug('Import gatherer "%s"', GM)
    GM = import_module(GM)
    gather = GM.Gatherer(queue=Q)

    _log.info("Install provider")
    M = opsModule.Service(db, gather=gather.gather)
    # provide MASAR style calls through a single PV (args.name)
    installProvider("masar", MASARDispatcher(Q, target=M, channels=[args.name]))
    # provide NTRUI style calls, one PV per method, with a common prefix (args.name+':')
    installProvider("masarnturi", NTURIDispatcher(Q, target=M, prefix=args.name+':'))

    _log.info("Prepare server")
    S = Server(providers="masar masarnturi")

    _log.info("Run server")
    #S.start()
    _log.info("Started")

    try:
        Q.handle()
    except KeyboardInterrupt:
        pass

    _log.info("Stop")
    S.stop()
    _log.info("Done")

    db.close()

if __name__=='__main__':
    main(getargs())

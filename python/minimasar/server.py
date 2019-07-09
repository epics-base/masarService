
import logging
_log = logging.getLogger(__name__)

from importlib import import_module
from threading import Event

from .ops import Service
from .db import connect

from p4p.server import Server, installProvider
from p4p.rpc import WorkQueue, MASARDispatcher, NTURIDispatcher

def getargs():
    from argparse import ArgumentParser
    P = ArgumentParser()
    P.add_argument('db', help='File name of sqlite .db file (or ":memory:")')
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

    GM = 'minimasar.gather.'+args.gather
    _log.debug('Import gatherer "%s"', GM)
    GM = import_module(GM)
    gather = GM.Gatherer(queue=Q)

    _log.debug('Open DB "%s"', args.db)
    db = connect(args.db)

    _log.info("Install provider")
    M = Service(db, gather=gather.gather)

    _log.info("Prepare server")
    S = Server(providers=[
        # provide MASAR style calls through a single PV (args.name)
        MASARDispatcher(Q, target=M, name='masar', channels=[args.name]),
        # provide NTRUI style calls, one PV per method, with a common prefix (args.name+':')
        NTURIDispatcher(Q, target=M, name='masaruri', prefix=args.name+':'),
    ])

    with S:
        _log.info("Run server")

        try:
            Q.handle()
        except KeyboardInterrupt:
            pass

        _log.info("Stop")
    _log.info("Done")

    db.close()

if __name__=='__main__':
    main(getargs())

import os
import threading
import sys
import time
import signal
conf = "../../python/masarserver/masarservice.conf"
if os.environ["EPICS_BASE"]!=None:
    iocexecutable = os.environ["EPICS_BASE"] + "/bin/" + os.environ["EPICS_HOST_ARCH"] + "/softIoc"
else:
    iocexecutable = "/usr/lib/epics/bin/" + os.environ["EPICS_HOST_ARCH"] + "/softIoc"
executable = "../../cpp/bin/" + os.environ["EPICS_HOST_ARCH"] + "/masarServiceRun"

def setConfMongo():
    f = open(conf, "rw+")
    f.write("[Common]\nowner=null\nmachine=null\ndatabase=mongodb\n#database=sqlite")
    f.close()

def setConfSQLite():
    f = open(conf, "rw+")
    f.write("[Common]\nowner=null\nmachine=null\n#database=mongodb\ndatabase=sqlite")
    f.close()

def startSQLiteService():
    setConfSQLite()
    pid, fd = os.forkpty()
    if pid == 0:
        os.execv(executable, ['masarServiceRun', 'sqliteMasarTestService'])
    return pid, fd

def startMongoService():
    #conf needs to be set
    setConfMongo()
    pid, fd = os.forkpty()
    if pid == 0:
        os.execv(executable, ['masarServiceRun', 'mongoMasarTestService'])
    return pid, fd

def startIOC():
    # conf needs to be set
    pid, fd = os.forkpty()
    if pid == 0:
        os.chdir("../v3IOC/")
        os.execv(iocexecutable, ['softIoc', '../v3IOC/st.cmd'])
    return pid, fd

def readfd(fd):
    while 1:
        print str(os.read(fd, 16384).strip("\n"))

def handler(signum, frame):
    global pids
    for pid in pids:
        os.kill(pid, signal.SIGKILL)
    sys.exit()

def main():
    global pids
    signal.signal(signal.SIGTERM, handler)
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))  # Uses a filename, not good, also only works on linux?
    iocpid, iocfd = startIOC()
    pids = [iocpid]
    iocthread = threading.Thread(group=None, target=readfd, args=(iocfd,), name="iocthread", kwargs={})
    iocthread.start()

    sqlpid, sqlfd = startSQLiteService()
    pids = [sqlpid, iocpid]  # repopulating list to force order
    sqlthread = threading.Thread(group=None, target=readfd, args=(sqlfd,), name="sqlthread", kwargs={})
    sqlthread.start()
    time.sleep(3)
    mongopid, mongofd = startMongoService()
    mongothread = threading.Thread(group=None, target=readfd, args=(mongofd,), name="mongothread", kwargs={})
    mongothread.start()
    pids = [mongopid, sqlpid, iocpid]
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        os.kill(sqlpid, signal.SIGKILL)
        os.kill(mongopid, signal.SIGKILL)
        os.kill(iocpid, signal.SIGKILL)
        sys.exit()

if __name__ == '__main__':
    main()

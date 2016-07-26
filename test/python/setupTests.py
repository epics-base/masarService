import os
import threading
import sys
import time
global kill, conf_lock
conf = "../../python/masarserver/masarservice.conf"
iocexecutable = "/usr/lib/epics/bin/" + os.environ["EPICS_HOST_ARCH"] + "/softIoc"
executable = "../../cpp/bin/" + os.environ["EPICS_HOST_ARCH"] + "/masarServiceRun"
kill = 0
conf_lock = threading.Lock()


def setConfMongo():
    copy_flag = False
    #f = open(conf, "rw+")
   # for line in f:
     #   print line
       # if "#database=mongodb" in line:
           # f.tell()
   # f.close()


    f = open(conf, "rw+")

    f.write("[Common]\nowner=null\nmachine=null\ndatabase=mongodb\n#database=sqlite")

    f.close()

def setConfSQLite():
    f = open(conf, "rw+")

    f.write("[Common]\nowner=null\nmachine=null\n#database=mongodb\ndatabase=sqlite")

    f.close()


def startSQLiteService():
    conf_lock.acquire()
    setConfSQLite()
    pid, fd = os.forkpty()
    if pid == 0:
        os.execv(executable, ['masarServiceRun', 'sqliteMasarTestService'])
    conf_lock.release()
    return fd


def startMongoService():
    #conf needs to be set
    conf_lock.acquire()
    setConfMongo()
    pid, fd = os.forkpty()
    if pid == 0:
        os.execv(executable, ['masarServiceRun', 'mongoMasarTestService'])
    conf_lock.release()
    return fd


def startIOC():
    # conf needs to be set
    pid, fd = os.forkpty()
    conf_lock.acquire()
    if pid == 0:
        os.chdir("../v3IOC/")
        os.execv(iocexecutable, ['softIoc', '../v3IOC/st.cmd'])
    conf_lock.release()
    return fd


def readfd(fd):
    while kill == 0:
        print str(os.read(fd, 1024).strip("\n"))
    print "done"


def main():
    global kill
    kill = 0
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))  # Uses a filename, not good, also only works on linux?
    iocfd = startIOC()
    iocthread = threading.Thread(group=None, target=readfd, args=(iocfd,), name="iocthread", kwargs={})
    iocthread.start()

    sqlfd = startSQLiteService()
    sqlthread = threading.Thread(group=None, target=readfd, args=(sqlfd,), name="sqlthread", kwargs={})
    sqlthread.start()
    time.sleep(3)
    mongofd = startMongoService()
    mongothread = threading.Thread(group=None, target=readfd, args=(mongofd,), name="mongothread", kwargs={})
    mongothread.start()

    # wait?
    # run tests?

    #sys.exit()


if __name__ == '__main__':
    main()

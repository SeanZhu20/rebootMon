#!/usr/bin/env python
#coding=utf-8
import zerorpc
import time
import os
from crypt import *
import gipc
import sys, time
from daemon import Daemon
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from collector.agent import startTh 

TEST = True

class MyDaemon(Daemon):
    def run(self):
        e = gipc.start_process(target=Executor, args=('Executor',))
        #c = gipc.start_process(target=Collector, args=('Collector',))
        e.join()
        #c.join()

def Collector(name):
    print 'hello', name
    startTh()

def Executor(name):
    print 'hello', name
#    if sys.platform == 'linux2':
#        import ctypes
#        libc = ctypes.cdll.LoadLibrary('libc.so.6')
#        libc.prctl(15, 'My Simple App', 0, 0, 0)
    s = zerorpc.Server(HelloRPC())
    s.bind("tcp://0.0.0.0:4242")
    s.run()

class HelloRPC(object):
    def hello(self, name):
        print   "exec %s  %s" %(name,time.strftime('%Y-%m-%d %H-%m-%S',time.localtime(time.time())))
        ret = os.popen(name).read()
        ret_str = "Result %s\n %s" % (time.strftime('%Y-%m-%d %H-%m-%S',time.localtime(time.time())), ret)
        return encrypt(ret_str)

    def deploy(self, pkg, path):
        print pkg, path
        return encrypt('OK')

if __name__ == "__main__":
        
    daemon = MyDaemon('/tmp/daemon-example.pid')
    if TEST:
        daemon.run()
    else:
        if len(sys.argv) == 2:
            if 'start' == sys.argv[1]:
                daemon.start()
            elif 'stop' == sys.argv[1]:
                daemon.stop()
            elif 'restart' == sys.argv[1]:
                daemon.restart()
            else:
                print "Unknown command"
                sys.exit(2)
            sys.exit(0)
        else:
            print "usage: %s start|stop|restart" % sys.argv[0]
            sys.exit(2)

    


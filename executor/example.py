import zerorpc
import time
import os
from crypt import *
import gipc
import sys, time
from daemon import Daemon

def Executor(name):
    #print 'hello', name
    s = zerorpc.Server(HelloRPC())
    s.bind("tcp://0.0.0.0:4242")
    s.run()

class HelloRPC():
    def hello(self, name):
        print   "exec %s  %s" %(name,time.strftime('%Y-%m-%d %H-%m-%S',time.localtime(time.time())))
        ret = os.popen(name).read()
        ret_str = "Result %s\n %s" % (time.strftime('%Y-%m-%d %H-%m-%S',time.localtime(time.time())), ret)
        #return ret_str
        return encrypt(ret_str)

if __name__ == "__main__":
    Executor("a")

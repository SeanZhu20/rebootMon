#!/usr/bin/env python
import inspect
import os,time,socket

class mon:
    def __init__(self):
        self.data = {}
    def getHost(self):
        return socket.gethostname()
    def getTime(self):
        return int(time.time())
    def runAllGet(self):
        for fun in inspect.getmembers(self, predicate=inspect.ismethod):
            if fun[0][:3] == 'get':
                self.data[fun[0][3:]] = fun[1]()
        return self.data

if __name__ == "__main__":
    print mon().runAllGet()

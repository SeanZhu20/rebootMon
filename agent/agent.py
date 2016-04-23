#!/usr/bin/python
import Queue
import threading
import time
import json
import urllib2
import socket
import commands
import pdb
import logging
from moniItems import mon

import sys, os

def readn(sock, n):
    res = ""
    while True:
        s = sock.recv(n)
        if len(s) == 0:
            return res
        res += s
        n -= len(s)
        if n == 0:
            return res

class porterThread (threading.Thread):
    def __init__(self, name, trans, q, interval=None):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.interval = interval
        self.sock = None
        self.trans = trans

    def run(self):
        if self.name == 'collect':
            self.collectLoop()
        elif self.name == 'sendjson':
            self.sendLoop()

    def collectLoop(self):
        m = mon()
        atime=int(time.time())
        while True:
            data = m.runAllGet()
            self.q.put(data)
            btime=int(time.time())
            time.sleep(self.interval-((btime-atime)%self.interval))
            
    def sendLoop(self):
        while True:
            if not self.q.empty():
                data = self.q.get()
                logging.debug("data:%s", data)
                self.sendData(json.dumps(data))
            time.sleep(self.interval)

    def connect(self, addr):
        i = 0.1
        while True:
            try:
                self.sock = socket.create_connection(addr)
                return
            except Exception, e:
                logging.error("connect error:%s, try again", e)
                time.sleep(i)
                i = i * 2
                if i > 30:
                    i = 30

    def sendData(self, data):
        if self.sock == None:
            self.connect(self.trans)

        cnt = 0
        while cnt < 3:
            try:
                self.sock.send('%010d%s'%(len(data), data))
                head = readn(self.sock, 10)
                body = readn(self.sock, int(head))
                logging.debug("body:%s", body)
                return
            except Exception,e:
                logging.error("send error:%s", e)
                self.sock.close()
                self.connect(self.trans)
                cnt += 1
             

def main():
    trans = ('127.0.0.1', 9001)
    q = Queue.Queue(10)
    collect = porterThread('collect', trans, q, interval=10)
    collect.setDaemon(True)
    collect.start()
    logging.info("collect thread start")

    time.sleep(0.5)
    sendjson = porterThread('sendjson', trans, q, interval=3)
    sendjson.setDaemon(True)
    sendjson.start()
    logging.info("send thread start")

    collect.join()
    sendjson.join()

if __name__ == "__main__":
    FORMAT = "%(asctime)-15s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    main()

#!/user/bin/python
#encoding:utf8

import socket
import logging
import sys
import select
import os
import threading
import Queue
import json
import conf

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

def readMsg(sock):
    head = readn(sock, 10)
    if len(head) != 10:
        return ""
    body = readn(sock, int(head))
    return body

class Loop:
    def __init__(self, pipe, q, name='ioloop'):
        self.name = name
        self.pipe = pipe
        self.efd = select.epoll()
        self.m = {}
        self.q = q
        self.alarmMap = {}

        self.efd.register(pipe.fileno(), select.POLLIN)

    def loop(self):
        while True:
            for fd, event in self.efd.poll():
                if fd == self.pipe.fileno():
                    newfd = int(self.pipe.recv(4))
                    logging.info('%s receive new fd %d', self.name, newfd)
                    self.m[newfd] = socket.fromfd(newfd, socket.AF_INET, socket.SOCK_STREAM)
                    self.efd.register(newfd, select.POLLIN)
                else:
                    conn = self.m[fd]

                    msg = readMsg(conn)
                    logging.debug('msg:%s', msg)
                    if len(msg) == 0:
                        self.closeConn(fd)
                        continue

                    try:
                        self.judge(json.loads(msg))
                        conn.send('%010d%s'%(2, 'OK'))
                    except Exception, e:
                        logging.error("ff error:%s", e)
                        conn.send('%010d%s'%(5, 'ERROR'))
                        self.closeConn(fd)

    def closeConn(self, fd):
        conn = self.m[fd]
        self.efd.unregister(fd)
        del self.m[fd]
        conn.shutdown(socket.SHUT_WR)
        conn.close()


    def getconf(self):
        reload(conf)
        return conf.ffconf

    def judge(self, msg):
        for conf in self.getconf():
            name, op, value, mail = conf
            expr = str(msg[name]) + op + str(value)
            logging.debug("expr:%s", expr)
            res = eval(expr)
            logging.debug("res:%s", res)

            key = msg["Host"] + "_" + name
            if res:
                count = self.alarmMap.get(key, 0)
                if count < 3:
                    m = {
                        "action":"alarm",
                        "name":name,
                        "host":msg["Host"]
                        "expr":expr,
                        "value":msg[name],
                        "mail":mail,
                    }
                    self.q.put(m)
                    count += 1
                    self.alarmMap[key] = count

            else:
                count = self.alarmMap.get(key, 0)
                if count > 1:
                    m = {
                        "action":"recovery",
                        "name":name,
                        "host":msg["Host"],
                        "expr":expr,
                        "value":msg[name],
                        "mail":mail,
                    }

                    self.q.put(m)
                    self.alarmMap[key] = 0


class Alarm():
    def __init__(self, q):
        self.q = q

    def run(self):
        logging.info("alarm running.")
        while True:
            item = self.q.get()
            logging.debug("alarm:%s", item)
            title = '%s-%s'%(item["host"], item["name"])
            body = 'action:%s host:%s name:%s alarm:%s, current:%s'%(
                item['action'], item['host'], item['name'], item['expr'], item['value'])
            os.system('echo "%s" | mail -s "%s" "%s"'%(body, title, item['mail']))

def main():
    if len(sys.argv) < 2:
        print 'usage python ff.py port'
        return
    FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    alarmQ = Queue.Queue(10)

    alarm = Alarm(alarmQ)
    threading.Thread(target=alarm.run).start()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', int(sys.argv[1])))
    s.listen(1)
    logging.info('listening on 0.0.0.0:%s', sys.argv[1])

    pipes = []
    for i in range(4):
        pipe = socket.socketpair(socket.AF_UNIX)
        loop = Loop(pipe[1], alarmQ, 'loop' + str(i))
        pipes.append(pipe[0])
        thread = threading.Thread(target=loop.loop)
        thread.setDaemon(True)
        thread.start()

    i = 0
    while True:
        conn, addr = s.accept()
        pipe = pipes[i]
        i = (i + 1)%len(pipes)
        sfd = '%04d' %(os.dup(conn.fileno()))
        pipe.send(sfd)
        conn.close()
        conn = None

if __name__ == '__main__':
    main()

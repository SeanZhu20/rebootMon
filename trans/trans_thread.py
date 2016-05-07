import socket
import logging
import sys
import threading
import time

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


class Transfer:
    def __init__(self, listen, addrList):
        self.listen = listen
        self.addrList = addrList

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(self.listen)
        s.listen(3)
        logging.info('listening on %s', self.listen)
        while True:
            conn, addr = s.accept()
            logging.info('accept from %s', addr)
            agent = AgentConnection(conn, self.addrList)
            t = threading.Thread(target=agent.run)
            t.start()


class AgentConnection:
    def __init__(self, conn, sendList):
        self.conn = conn
        self.sendList = sendList
        self.connList = None

    def connect(self, addr):
        i = 0.1
        while True:
            try:
                sock = socket.create_connection(addr)
                return sock
            except Exception, e:
                logging.error("connect error:%s, try again", e)
                time.sleep(i)
                i = i * 2
                if i > 30:
                    i = 30

    def connectAll(self):
        self.connList = []
        for addr in self.sendList:
            conn = self.connect(addr)
            self.connList.append(conn)

    def closeAll(self):
        for conn in self.connList:
            conn.close()
        self.connList = None

    def sendAll(self, msg):
        if self.connList == None:
            self.connectAll()
        for conn in self.connList:
            conn.send(msg)
            readMsg(conn)

    def run(self):
        conn = self.conn
        msg = ""
        while True:
            try:
                msg = readMsg(conn)
                if len(msg) == 0:
                    break
                self.sendAll('%010d%s'%(len(msg), msg))
                conn.send('%010d%s'%(2, 'OK'))
            except Exception, e:
                logging.error("read error:%s", e)
                break

        conn.close()
        self.closeAll()
        logging.info('connection from %s closed', conn.getpeername())

def main():
    if len(sys.argv) < 2:
        print 'usage python trans.py port'
        return
    FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    sendList = [('127.0.0.1', 9000)]
    trans = Transfer(('0.0.0.0', int(sys.argv[1])), sendList)
    trans.start()

if __name__ == '__main__':
    main()

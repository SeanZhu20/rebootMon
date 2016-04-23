import socket
import logging
import sys
import threading
import subprocess
import pty
import store

globalLock = threading.Lock()

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

def handleconn(conn):
    addr = conn.getpeername()
    logging.info('accept from %s', addr)
    while True:
        msg = readMsg(conn)
        logging.debug('msg:%s', msg)
        if len(msg) == 0:
            break
        try:
            globalLock.acquire()
            store.insertMonData(msg)
            globalLock.release()
        except Exception, e:
            globalLock.release()
            logging.error("insert error:%s", e)
            conn.send('%010d%s'%(5, 'ERROR'))
            break
        conn.send('%010d%s'%(2, 'OK'))

    conn.close()
    logging.info('connection from %s closed', addr)

def main():
    if len(sys.argv) < 2:
        print 'usage python echo.py port'
        return
    FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', int(sys.argv[1])))
    s.listen(3)
    logging.info('listening on 0.0.0.0:%s', sys.argv[1])
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handleconn, args=(conn,))
        t.start()


if __name__ == '__main__':
    main()

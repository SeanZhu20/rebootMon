#!/usr/bin/env python
# coding: utf-8

from daemon import Daemon
import socket
import select
import time

__all__ = ["nbNet", "sendData_mh"]
DEBUG = False

def dbgPrint(msg):
    if DEBUG:
        print(msg)

import signal,functools
class TimeoutError(Exception): pass
def timeout(seconds, error_message = 'Function call timed out'):
    def decorated(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return functools.wraps(func)(wrapper)
    return decorated

@timeout(5)
def connect_timeout(socket, host_port):
    return socket.connect(host_port)

def sendData_mh(sock_l, host_l, data, single_host_retry = 3):
    """
    saver_l = ["localhost:50001","127.0.0.1:50001"]
    sock_l = [some_socket]
    sendData_mh(sock_l,saver_l,"this is data to send")
    """
    done = False
    for host_port in host_l:
        if done:
            break
        host,port =host_port.split(':')
        port = int(port)
        print "iter", host, port
        print "sock_l", sock_l
        retry = 0
        while retry < single_host_retry:
            try:
                if sock_l[0] == None:
                    sock_l[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print "connecting", host, port
                    #connect_timeout(sock_l[0], (host, port))
                    sock_l[0].settimeout(5)
                    sock_l[0].connect((host, port))
                d = data
                sock_l[0].sendall("%010d%s"%(len(d), d))
                print "%010d%s"%(len(d), d)
                count = sock_l[0].recv(10)
                if not count:
                    print 'count', count
                    raise Exception("recv error", "recv error")
                count = int(count)
                buf = sock_l[0].recv(count)
                print buf
                if buf[:2] == "OK":
                    retry = 0
                    done = True
                    return True
            except (socket.error, ValueError), msg:
                print msg.errno
                sock_l[0].close()
                sock_l[0] = None
                retry += 1

def sendData(sock_l, host, port, data):
    retry = 0 
    while retry < 3:
        try:
            if sock_l[0] == None:
                sock_l[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock_l[0].connect((host, port))
                print "connecting"
            d = data
            sock_l[0].sendall("%010d%s"%(len(d), d)) 
            print "%010d%s"%(len(d), d)
            count = sock_l[0].recv(10)
            if not count:
                raise Exception("recv error", "recv error")
            count = int(count)
            buf = sock_l[0].recv(count)
            print buf 
            if buf[:2] == "OK":
                retry = 0 
                break
        except:
            sock_l[0].close()
            sock_l[0] = None
            retry += 1



# initial status for state machine
class _STATE:
    def __init__(self):
        self.state = "accept"
        self.have_read = 0
        self.need_read = 10
        self.have_write = 0
        self.need_write = 0
        self.buff_write = ""
        self.buff_read = ""
        # sock_obj is a object
        self.sock_obj = ""

    def printState(self):
        if DEBUG:
            dbgPrint('\n - current state of fd: %d' % self.sock_obj.fileno())
            dbgPrint(" - - state: %s" % self.state)
            dbgPrint(" - - have_read: %s" % self.have_read)
            dbgPrint(" - - need_read: %s" % self.need_read)
            dbgPrint(" - - have_write: %s" % self.have_write)
            dbgPrint(" - - need_write: %s" % self.need_write)
            dbgPrint(" - - buff_write: %s" % self.buff_write)
            dbgPrint(" - - buff_read:  %s" % self.buff_read)
            dbgPrint(" - - sock_obj:   %s" % self.sock_obj)


class nbNet:
    '''non-blocking Net'''
    def __init__(self, addr, port,logic):
        dbgPrint('\n__init__: start!')
        self.conn_state = {}
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_sock.bind((addr, port))
        self.listen_sock.listen(10)
        self.setFd(self.listen_sock)
        self.epoll_sock = select.epoll()
        # LT for default, ET add ' | select.EPOLLET '
        self.epoll_sock.register(self.listen_sock.fileno(), select.EPOLLIN )
        self.logic = logic
        self.sm = {
            "accept" : self.accept,
            "read"   : self.read,
            "write"  : self.write,
            "process": self.process,
            "closing": self.close,
        }
        dbgPrint('\n__init__: end, register no: %s' % self.listen_sock.fileno() )


    def setFd(self, sock):
        """sock is class object of socket"""
        dbgPrint("\n -- setFd start!")
        tmp_state = _STATE()
        tmp_state.sock_obj = sock
        self.conn_state[sock.fileno()] = tmp_state
        self.conn_state[sock.fileno()].printState()
        dbgPrint("\n -- setFd end!")

    def accept(self, fd):
        """fd is fileno() of socket"""
        dbgPrint("\n -- accept start!")
        sock_state = self.conn_state[fd]
        sock = sock_state.sock_obj
        conn, addr = sock.accept()
        # set to non-blocking: 0
        conn.setblocking(0)             
        self.epoll_sock.register(conn.fileno(), select.EPOLLIN)
        # new client connection fd be initilized 
        self.setFd(conn)
        self.conn_state[conn.fileno()].state = "read"
        # now end of accept, but the main process still on 'accept' status
        # waiting for new client to connect it.
        dbgPrint("\n -- accept end!")

    def close(self, fd):
        """fd is fileno() of socket"""
        try:
            # cancel of listen to event
            sock = self.conn_state[fd].sock_obj
            sock.close()
            self.epoll_sock.unregister(fd)
            self.conn_state.pop(fd)
        except:
            dbgPrint("Close fd: %s abnormal" % fd)
            pass

    def read(self, fd):
        """fd is fileno() of socket"""
        try:
            sock_state = self.conn_state[fd]
            conn = sock_state.sock_obj
            if sock_state.need_read <= 0:
                self.conn_state[fd].state = 'closing'
                self.state_machine(fd)

            one_read = conn.recv(sock_state.need_read)
            dbgPrint("\tread func fd: %d, one_read: %s, need_read: %d" % (fd, one_read, sock_state.need_read))
            if len(one_read) == 0:
                return
            # process received data
            sock_state.buff_read += one_read
            sock_state.have_read += len(one_read)
            sock_state.need_read -= len(one_read)
            sock_state.printState()

            # read protocol header
            if sock_state.have_read == 10:
                header_said_need_read = int(sock_state.buff_read)
                if header_said_need_read <= 0:
                    raise socket.error
                sock_state.need_read += header_said_need_read
                sock_state.buff_read = ''
                # call state machine, current state is read. 
                # after protocol header haven readed, read the real cmd content, 
                # call machine instead of call read() it self in common.
                sock_state.printState()
            elif sock_state.need_read == 0:
                # recv complete, change state to process it
                sock_state.state = "process"
                self.process(fd)
        except (socket.error, ValueError), msg:
            self.conn_state[fd].state = 'closing'
            if msg.errno == 11:
                return
            # closing directly when error.
            dbgPrint(msg)
            self.state_machine(fd)


    def write(self, fd):
        sock_state = self.conn_state[fd]
        conn = sock_state.sock_obj
        last_have_send = sock_state.have_write
        try:
            # to send some Bytes, but have_send is the return num of .send()
            have_send = conn.send(sock_state.buff_write[last_have_send:])
            sock_state.have_write += have_send
            sock_state.need_write -= have_send
            if sock_state.need_write == 0 and sock_state.have_write != 0:
                # send complete, re init status, and listen re-read
                sock_state.printState()
                dbgPrint('\n write data completed!')
                self.setFd(conn)
                self.conn_state[fd].state = "read"
                self.epoll_sock.modify(fd, select.EPOLLIN)
        except socket.error, msg:
            sock_state.state = "closing"
            dbgPrint(msg)
        self.state_machine(fd)

    def process(self, fd):
        sock_state = self.conn_state[fd]
        response = self.logic(sock_state.buff_read)
        sock_state.buff_write = "%010d%s" % (len(response), response)
        sock_state.need_write = len(sock_state.buff_write)
        sock_state.state = "write"
        self.epoll_sock.modify(fd, select.EPOLLOUT)
        sock_state.printState()
        #self.state_machine(fd)

    def run(self):
        while True:
            dbgPrint("\nrun func loop:")
            # print conn_state
            for i in self.conn_state.iterkeys():
                dbgPrint("\n - state of fd: %d" % i)
                self.conn_state[i].printState()

            epoll_list = self.epoll_sock.poll()
            for fd, events in epoll_list:
                dbgPrint('\n-- run epoll return fd: %d. event: %s' % (fd, events))
                sock_state = self.conn_state[fd]
                if select.EPOLLHUP & events:
                    dbgPrint("EPOLLHUP")
                    sock_state.state = "closing"
                elif select.EPOLLERR & events:
                    dbgPrint("EPOLLERR")
                    sock_state.state = "closing"
                self.state_machine(fd)

    def state_machine(self, fd):
        #time.sleep(0.1)
        dbgPrint("\n - state machine: fd: %d, status: %s" % (fd, self.conn_state[fd].state))
        sock_state = self.conn_state[fd]
        self.sm[sock_state.state](fd)



if __name__ == '__main__':
    def logic(d_in):
        return(d_in[::-1])

    reverseD = nbNet('0.0.0.0', 9076, logic)
    reverseD.run()

#!/usr/bin/env python
# coding=utf-8

import sys, os 
import subprocess
import fcntl

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from nbNet.nbNetFramework import nbNet

if __name__ == '__main__':
    def logic(coming_sock_fd ,d_in):
        #return os.popen(d_in).read()
        subprocess.Popen(d_in , shell= True, stdout=coming_sock_fd, stderr=coming_sock_fd)
        #out = os.popen4(d_in)[1]
        return None

    reverseD = nbNet('0.0.0.0', 9079, logic)
    reverseD.run()



#!/usr/bin/env python
# coding=utf-8

import sys, os 
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from simpleNet.nbNetFramework import nbNet

if __name__ == '__main__':
    def logic(d_in):
        return(d_in[::-1])

    reverseD = nbNet('0.0.0.0', 9079, logic)
    reverseD.run()



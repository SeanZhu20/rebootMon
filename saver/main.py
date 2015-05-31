#!/usr/bin/env python
# coding=utf-8

import sys, os 
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from simpleNet.nbNetFramework import nbNet

if __name__ == '__main__':
    def logic(d_in):
        print d_in
        return("OK")

    saverD = nbNet('0.0.0.0', 50001, logic)
    saverD.run()



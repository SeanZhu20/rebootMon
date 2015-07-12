import zerorpc
import os,sys
from crypt import *

from multiprocessing import Pool

def rpc_call(host):
    c = zerorpc.Client()
    c.connect("tcp://%s"%(host))
    get_str = c.hello('hostname')
    print decrypt(get_str) 

if __name__ == "__main__":
    p = Pool(5)
    p.map(rpc_call, ['127.0.0.1:4242', '127.0.0.1:4242'])

#!/usr/bin/env python
#coding=utf-8
import zerorpc
import os,sys
from crypt import *

from multiprocessing import Pool

pkg = sys.argv[1]
deploy_path = sys.argv[2]

# agent_ctl.py 模块名 部署路径 机器列表（逗号分隔）
# 发送json到机器列表里的agent {"pkg_name":"package_name", "path":"deploy_path"}
def deploy_call(host):
    c = zerorpc.Client()
    c.connect("tcp://%s"%(host))
    get_str = c.deploy(pkg, deploy_path)
    #print get_str
    print decrypt(get_str) 

def rpc_call(host):
    c = zerorpc.Client()
    c.connect("tcp://%s"%(host))
    get_str = c.hello('hostname')
    #print get_str
    print decrypt(get_str) 

if __name__ == "__main__":
    p = Pool(5)
    p.map(deploy_call, ['127.0.0.1:4242'])

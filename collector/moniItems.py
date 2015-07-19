#!/usr/bin/env python
import inspect
import os,time,socket
import urllib
import json

class mon:
    def __init__(self):
        self.data = {}

    def getLoadAvg(self):
        with open('/proc/loadavg') as load_open:
            a = load_open.read().split()[:3]
            #return "%s %s %s" % (a[0],a[1],a[2])
            return   float(a[0])
    
    def getMemTotal(self):
        with open('/proc/meminfo') as mem_open:
            a = int(mem_open.readline().split()[1])
            return a / 1024
    
    def getMemUsage(self, noBufferCache=True):
        if noBufferCache:
            with open('/proc/meminfo') as mem_open:
                T = int(mem_open.readline().split()[1]) #Total
                F = int(mem_open.readline().split()[1]) #Free
                B = int(mem_open.readline().split()[1]) #Buffer
                C = int(mem_open.readline().split()[1]) #Cache
                return (T-F-B-C)/1024
        else:
            with open('/proc/meminfo') as mem_open:
                a = int(mem_open.readline().split()[1]) - int(mem_open.readline().split()[1])
                return a / 1024
    
    def getMemFree(self, noBufferCache=True):
        if noBufferCache:
            with open('/proc/meminfo') as mem_open:
                T = int(mem_open.readline().split()[1])
                F = int(mem_open.readline().split()[1])
                B = int(mem_open.readline().split()[1])
                C = int(mem_open.readline().split()[1])
                return (F+B+C)/1024
        else:
            with open('/proc/meminfo') as mem_open:
                mem_open.readline()
                a = int(mem_open.readline().split()[1])
                return a / 1024
     
    def getHost(self):
        return ['host1', 'host2', 'host3', 'host4', 'host5'][int(time.time() * 1000.0) % 5] 
        #return socket.gethostname()
    def getTime(self):
        return int(time.time())
    
    def userDefineMon(self):
        """
        5min -> GET webapi 获取自定义监控项列表
            {"url":"脚本url","md5":"43214321","name":'eth_all'}
        -> check md5
            /home/work/agent/mon/user/$name/xxx.tgz
        -> xxx.tgz -> main -> chmod +x -> ./main
        -> output
            eth1:10
            eth2:20
            eth3:32
        -> return
            {"eth1":10,"eth2":20,"eth3":32}
        
        """
		# get the api
		try:
			result = urllib.urlopen("http://180.153.191.128:50004/userdefine_listitem").read()
		except Exception :
			return "get url fail"
		res = json.loads(result)
		url = res["url"]
		name = res["name"]
		md5 = res["md5"]
        data = {}
		# check md5
		# 脚本路径规范 /home/work/agent/mon/user/脚本名/脚本名.tgz"  
		path = "/home/work/agent/mon/user/%s/" % (name)
		check_md5 =  os.system("cd %s && md5sum %s.tgz|awk '{print $1}'" % (path,name))
		if md5 != check_md5:
			return "%s is change" % name
		else:
			#action
			s = os.popen("cd %s && tar xvf %s.tgz >>/dev/null && chmod +x main && ./main"% (path,name)).read()
		#return
	    for i in s.split("\n"):
			  k,v= i.split(":")
			  data[k] = v
		return data



			
		
        return 

    def runAllGet(self):
        for fun in inspect.getmembers(self, predicate=inspect.ismethod):
            if fun[0] == "userDefineMon":
                self.data.update(fun[1]())
            elif fun[0][:3] == 'get':
                self.data[fun[0][3:]] = fun[1]()
        return self.data

if __name__ == "__main__":
    print mon().runAllGet()

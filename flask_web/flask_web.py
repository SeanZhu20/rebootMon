#!/usr/bin/env python
#encoding:utf8
import json
import time,random
import datetime
import MySQLdb as mysql
from flask import Flask, request
from flask import render_template
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
#from controller.client import *
#from nbNet.nbNet import sendData

app = Flask(__name__)
db = mysql.connect(user="reboot", passwd="reboot123", \
        db="falcon", charset="utf8")
db.autocommit(True)
c = db.cursor()

monTables = [
    'stat_0',
    'stat_1',
    'stat_2',
    'stat_3',
]

def fnvhash(string):
    ret = 97
    for i in string:
        ret = ret ^ ord(i) * 13
    return ret 

"""
CREATE TABLE `stat_0` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `host` varchar(256) DEFAULT NULL,
  `mem_free` int(11) DEFAULT NULL,
  `mem_usage` int(11) DEFAULT NULL,
  `mem_total` int(11) DEFAULT NULL,
  `load_avg` varchar(128) DEFAULT NULL,
  `time` bigint(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `host` (`host`(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8

"""

@app.route("/listhost", methods=["GET"])
def listhost():
    hostl = set()
    for t in monTables:
        sql = "SELECT distinct(`host`) FROM `%s`;" % (t)
        c.execute(sql)
        ones = c.fetchall()
        for one in ones:
            hostl.add(one[0])
    return json.dumps(list(set(hostl)))

@app.route("/", methods=["GET"])
def index():
    hostname = request.args.get("host")
    item = request.args.get("item")
  #  mIteml = []
    sql = "show columns from stat_2;"
    print sql
    c.execute(sql)
    columns = c.fetchall()
    columns = list(columns)
    columns = [i[0] for i in columns]
    columns.remove('id')
    columns.remove('host')
    columns.remove('time')
    print columns 
    hostl = set()
    for t in monTables:
        sql = "SELECT distinct(`host`) FROM `%s`;" % (t)
        c.execute(sql)
        ones = c.fetchall()
        for one in ones:
            hostl.add(one[0])
    return render_template("index.html", hosts = hostl, selected_host = hostname,items = columns,selected_item = item)

@app.route("/getdata", methods=["GET", "POST"])
def getdata():
    """
    /getdata?host=host5&item=mem_total&from=1434079888&to=1434079888&callback=jQuery18304293112317100167_1435477201089
    
    return:
    jQuery183045716429501771927_1435477247087(
    [
        [1147651200000,67.79],
        [1147737600000,64.98],
        [1147824000000,65.26],
        [1147910400000,63.18]
    ]);
    """
    host = request.args.get('host')
    item = request.args.get('item')
    t = int(time.time())
    f = t - 3600
    timetemplate = "%Y-%m-%d %H:%M:%S"
    try:
        t = time.mktime(datetime.datetime.strptime(request.args.get('to'), timetemplate).timetuple())
        f = time.mktime(datetime.datetime.strptime(request.args.get('from'), timetemplate).timetuple())
    except:
        pass
    print t, f 
    start_time = f
    end_time   = t
    callback   = request.args.get('callback')

    print start_time, end_time, callback
    mTable = monTables[fnvhash(host) % len(monTables)]
    sql = "SELECT `time`*1000,`%s` FROM `%s` WHERE host = '%s' AND `time` BETWEEN '%d' AND '%d';" % (item,mTable,host,int(start_time),int(end_time))
    print sql 
    c.execute(sql)
    data = c.fetchall()
    data = [[d[0], float(d[1])] for d in data]
    data = json.dumps(data)
    return_data = '%s(%s);' % (callback,data)
    return return_data 


@app.route("/show", methods=["GET", "POST"])
def show():
    host = request.args.get("host")
    item = request.args.get("item")
    t = int(time.time())
    f = t - 3600
    timetemplate = "%Y-%m-%d %H:%M:%S"
    try:
        t = time.mktime(datetime.datetime.strptime(request.args.get('to'), timetemplate).timetuple())
        f = time.mktime(datetime.datetime.strptime(request.args.get('from'), timetemplate).timetuple())
    except:
        pass
    print t, f 
    
    #mTable = monTables[fnvhash(host) % len(monTables)]
    #sql = "SELECT `%s` FROM `%s` WHERE host = '%s' AND `time` BETWEEN '%d' AND '%d';" % (item,mTable,host,f,t)
    #print sql
    #c.execute(sql)
    #ones = c.fetchall()

    return render_template("sysstatus.html", host = host, item = item, f = int(f), t = int(t) )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50004, debug=True)



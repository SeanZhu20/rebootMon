#!/usr/bin/env python
#encoding:utf8
import json
import time,random
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


@app.route("/show", methods=["GET", "POST"])
def show():
    host = request.args.get("host")
    item = request.args.get("item")
    mTable = monTables[fnvhash(host) % len(monTables)]
    sql = "SELECT `%s` FROM `%s` WHERE host = '%s';" % (item,mTable,host)
    print sql
    c.execute(sql)
    ones = c.fetchall()

    return render_template("sysstatus.html", data=ones, sql = sql)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50004, debug=True)



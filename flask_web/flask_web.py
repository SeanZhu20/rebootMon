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
    return render_template("index.html")


@app.route("/show", methods=["GET", "POST"])
def show():
    hostname = request.args.get("hostname")
    mTable = monTables[fnvhash(hostname) % len(monTables)]
    sql = "SELECT `load_avg` FROM `%s` WHERE host = '%s' limit 10;" % (mTable, hostname)
    c.execute(sql)
    ones = c.fetchall()

    return render_template("sysstatus.html", data=ones, sql = sql)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50004, debug=True)



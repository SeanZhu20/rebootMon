#!/usr/bin/env python
# coding=utf-8

import sys, os 
import MySQLdb as mysql
import json
import hashlib

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from simpleNet.nbNetFramework import nbNet

monTables = [
    'stat_0',
    'stat_1',
    'stat_2',
    'stat_3',
]

db = mysql.connect(user="reboot", passwd="reboot123", \
        db="falcon", charset="utf8")
db.autocommit(True)
c = db.cursor()

def fnvhash(string):
    ret = 97
    for i in string:
        ret = ret ^ ord(i) * 13
    return ret

def insertMonData(d_in):
    try:
        j = {}
        data = json.loads(d_in)
        print data
        dTime = int(data['Time'])
        hostIndex = monTables[fnvhash(data['Host']) % len(monTables)]
        for ud in data:
            if ud.startswith('UD_'):
                j[ud] = data[ud]
        ud_data = json.dumps(j)
        sql = "INSERT INTO `%s` (`host`,`mem_free`,`mem_usage`,`mem_total`,`load_avg`,`time`,`user_define`) VALUES('%s', '%d', '%d', '%d', '%s', '%d','%s')" % \
            (hostIndex, data['Host'], data['MemFree'], data['MemUsage'], data['MemTotal'], data['LoadAvg'], dTime,ud_data)
        ret = c.execute(sql)
        str=""
        for i in data:
            if UD_ in i:
               str += "i:"+data[i]
        if str != "":
            sql = "INSERT INTO %s (user_define) VALUES('%s')" % (hostIndex,str)
            ret = c.execute(sql)

        ## 把UD_开头的监控项数据json插入到user_define数据表中
        ## master modify
        print ret
        #xxxxx
        #lr 2222
        ## 冲突
        # 李冉做了一点修改
        # 解决了哈哈哈
    except mysql.IntegrityError:
        pass
    

if __name__ == '__main__':
    def logic(d_in):
        insertMonData(d_in)
#        print d_in
        return("OK")

    saverD = nbNet('0.0.0.0', 50001, logic)
    saverD.run()



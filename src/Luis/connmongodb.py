#!/usr/bin/env python
#_*_ coding: utf-8_*_
'''
Created on 2015-8-31

@author: luis
'''
import pymongo
from Luis.Wconn import Wconn

class connmongodb(object):
    
    def __init__(self, params):
        client = pymongo.MongoClient('127.0.0.1', 27017);
        db = client.test;
        #查看test数据库中集合信息
        print (db.collection_names());
        #连接到my_collection集合
        print (db.my_collection);
        #清空my_collection集合文档信息
        db.my_collection.remove();
        #显示my_collection集合中文档数目
        print (db.my_collection.find().count());
        #插入1000000条文档信息
        for i in  range(10000):
            db.my_collection.insert({"test":"tnt","index":i});
        print db.my_collection.find_one();
        for itemt in db.my_collection.find({"index":{"$gt":9990}}):
            print itemt["index"];
        #显示my_collection集合中文档数目
        print  ('插入完毕，当前文档数目：');
        print (db.my_collection.find().count());
        cx= Wconn()
        print dir(cx)
if __name__ == '__main__':
    dbconn=connmongodb('ll');
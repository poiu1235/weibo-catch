#!/usr/bin/env python
#_*_ coding: utf-8_*_
'''
Created on 2015-8-8

@author: luis
'''
import MySQLdb

class connexample(object):

    def __init__(self):
        self.conn=MySQLdb.Connect(host='127.0.0.1',user='root',passwd='111111');
        #选择数据库     
        self.conn.select_db('python');
    def createdb(self):
        #获取操作游标     
        cursor = self.conn.cursor()    
        #执行SQL,创建一个数据库.     
        cursor.execute("""create database python """)    
        #关闭连接，释放资源     
        cursor.close();
    def createtable(self):
        #获取操作游标     
        cursor = self.conn.cursor()    
        #执行SQL,创建一个数据库.     
        cursor.execute("""create database if not exists python""")    
        #执行SQL,创建一个数据表.     
        cursor.execute("""create table test(
                            id int, 
                            info varchar(100)) """)    
        #关闭连接，释放资源     
        cursor.close();
    def inserttable(self):
        #获取操作游标     
        cursor = self.conn.cursor() 
        value = [1,"inserted ?"];    
        #插入一条记录     
        cursor.execute("insert into test values(%s,%s)",value);    
        values=[]    
        #生成插入参数值     
        for i in range(20):    
            values.append((i,'Hello mysqldb, I am recoder ' + str(i)))    
        #插入多条记录     
        cursor.executemany("""insert into test values(%s,%s) """,values);   
        self.conn.commit()# 一定要要漏了，不然不会执行的
        #关闭连接，释放资源     
        cursor.close();  
    def selectdb(self):
        cursor = self.conn.cursor()    
        count = cursor.execute('select * from test')    
        print '总共有 %s 条记录' % count  
        #获取一条记录,每条记录做为一个元组返回     
        print "只获取一条记录:"   
        result = cursor.fetchone();    
        print result    
        #print 'ID: %s   info: %s' % (result[0],result[1])     
        print ('ID: %s   info: %s' % result )    
        #获取5条记录，注意由于之前执行有了fetchone()，所以游标已经指到第二条记录了，也就是从第二条开始的所有记录     
        print "只获取5条记录:"   
        results = cursor.fetchmany(5)    
        for r in results:    
            print r    
        print "获取所有结果:"   
        #重置游标位置，0,为偏移量，mode＝absolute | relative,默认为relative,     
        cursor.scroll(0,mode='absolute')    
        #获取所有结果
        #默认从数据库里取出的整型数字都会被转成长整型，所以带上了L     
        results = cursor.fetchall()    
        for r in results:    
            print r    
        self.conn.close()
if __name__ == '__main__':
    #connexample().createtable()
    #connexample().inserttable()
    connexample().selectdb()
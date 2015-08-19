#!/usr/bin/env python
#_*_ coding: utf-8_*_
'''
Created on 2015-8-8

@author: luis
'''
import MySQLdb
import hashlib

from Luis.Picreg import Picreg
from Luis.Wconn import Wconn
from Luis.WeiboTransfer import WeiboTransfer
from Luis.WeiboContent import WeiboContent
from Luis.Wuser import Wuser
from Luis.Relation import Relation


class ConnSQL(object):
    
    def __init__(self):
        pass
    def inition(self):
        self.conn=MySQLdb.Connect(host='127.0.0.1',user='root',passwd='111111',charset='utf8')
        #选择数据库     
        self.conn.select_db('weibocatch');
        self.md5=hashlib.md5()
    def insertuser(self,wuser,relation):
        if(isinstance(wuser, Wuser)):
            if(isinstance(relation, Relation)):
                self.inition()
                cursor=self.conn.cursor()
                try:
                    cursor.execute("""INSERT INTO weibocatch.w_user
                                    (wid,wname,recon,color,flag)
                                    VALUES
                                    (%s,%s,%s,%s,%s);
                                    """,(wuser.id,wuser.name,
                                         wuser.recon,wuser.color,0))
                    cursor.execute("""INSERT INTO weibocatch.w_relation
                                    (wid,wfriendid)
                                    VALUES
                                    (%s,%s);
                                    """,(relation.id,relation.friendid))
                    self.conn.commit()
                    print "用户和关注存入成功！"
                except Exception as err:
                    self.conn.rollback()
                    print err
                finally:
                    #关闭连接，释放资源     
                    cursor.close();
                    self.conn.close()   
    def insertcont(self,weibocontent,picid,wconn):
        if(isinstance(weibocontent, WeiboContent)):
            self.inition()
            self.md5.update(weibocontent.id.encode('utf8')+weibocontent.intime.encode('utf8')
                            +weibocontent.content.encode('utf8'))
            cursor=self.conn.cursor()
            try:
                if(picid==''):
                    picid=0
                cursor.execute("""INSERT INTO weibocatch.w_content
                                (weiboid,wid,content,url,map,label,intime,picid,wfrom)
                                VALUES
                                (%s,%s,%s,%s,%s,%s,%s,%s,%s);
                                """,(self.md5.hexdigest(),weibocontent.id,
                                     weibocontent.content.encode('utf8'),weibocontent.url,weibocontent.map.encode('utf8'),
                                     weibocontent.label.encode('utf8'),weibocontent.intime.encode('utf8'),int(picid),
                                     weibocontent.wfrom.encode('utf8')))
                if(isinstance(wconn, Wconn)):
                    if(wconn.tag.strip()):#判断字符串不为空
                        cursor.execute("""INSERT INTO weibocatch.w_conn
                                        (weiboid,tag,atid,atname)
                                        VALUES
                                        (%s,%s,%s,%s);""",(self.md5.hexdigest(),wconn.tag,
                                                           wconn.atid,wconn.atname.encode('utf8')))
                        #tag表示微博是来自原创还是转发，1是转发，0是原创
                self.conn.commit()# 一定不要漏了，不然不会执行的
                print "%s原创微博存入成功" % weibocontent.id.encode('utf8')
            except Exception as err:
                self.conn.rollback()
                print err
            finally:
                #关闭连接，释放资源     
                cursor.close();
                self.conn.close() 
    def inserttran(self,weibotran,picid,wconn):
        if(isinstance(weibotran, WeiboTransfer)):
            self.inition()#因为mysql 连接很容易超时就断开了，默认10s，所以索性每次都用的时候在申明
            self.md5.update(weibotran.id.encode('utf8')+weibotran.intime.encode('utf8')
                            +weibotran.remark.encode('utf8')+weibotran.content.encode('utf8'))
            #获取操作游标     
            cursor = self.conn.cursor()
            try: 
                if(picid==''):
                    picid=0
                #插入一条记录 全部用%s作占位符号，即使是数字也不要用%d 
                #因为这个插件程序会帮你转换的，字符串会自动给你加''，如果数字不会加
                cursor.execute("""INSERT INTO weibocatch.w_transfer
                                (weiboid,wid,transferid,content,remark,label,url,
                                intime,picid,wfrom)
                                VALUES
                                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                                """,(self.md5.hexdigest(),weibotran.id,weibotran.tranferid,
                                     weibotran.content.encode('utf8'),weibotran.remark.encode('utf8'),weibotran.label.encode('utf8'),
                                     weibotran.url,weibotran.intime.encode('utf8'),int(picid),weibotran.wfrom.encode('utf8')));
                if(isinstance(wconn, Wconn)):
                    if(wconn.tag==1 or wconn.tag==0):#判断字符串不为空
                        cursor.execute("""INSERT INTO weibocatch.w_conn
                                        (weiboid,tag,atid,atname)
                                        VALUES
                                        (%s,%s,%s,%s);""",(self.md5.hexdigest(),wconn.tag,
                                                           wconn.atid,wconn.atname.encode('utf8')))
                self.conn.commit()# 一定不要漏了，不然不会执行的
                print "%s转发微博存入成功" % weibotran.id.encode('utf8')
            except Exception as err:
                self.conn.rollback()
                print err
            finally:
                #关闭连接，释放资源     
                cursor.close();
                self.conn.close() 
    def insertpic(self,picreg):
        if(isinstance(picreg,Picreg)):
            self.inition()
            #获取操作游标     
            cursor = self.conn.cursor()
            try:
                cursor.execute("""INSERT INTO weibocatch.pic_reg
                            (path) VALUES (%s);""",picreg.picpath)
                self.conn.commit()
                #使用这函数向一个给定Connection对象返回的值是该Connection对象产生
                #对影响AUTO_INCREMENT列的最新语句第一个AUTO_INCREMENT值的。
                #这个值不能被其它Connection对象的影响，即它们产生它们自己的AUTO_INCREMENT值。
                #第二、LAST_INSERT_ID 是与table无关的，
                #如果向表a插入数据后，再向表b插入数据，LAST_INSERT_ID返回表b中的Id值。
                cursor.execute("SELECT LAST_INSERT_ID()")
                #"只获取一条记录:"   
                result = cursor.fetchone();#这个返回的是一个tuple,一个元素的元组后面都会跟一个”，“。没实际意义
                print "图片存入成功"
                return result[0]
            except Exception as err:
                self.conn.rollback()
                print err
            finally:
                #关闭连接，释放资源     
                cursor.close(); 
                self.conn.close()
    def getuserid(self):
        self.inition()
        #获取操作游标     
        cursor = self.conn.cursor()  
        try:
            cursor.execute("SELECT * FROM weibocatch.w_user where flag=0 order by inserttime limit 1")
            #"只获取一条记录:"   
            result = cursor.fetchone();#这个返回的是一个tuple
            return result
        except Exception as err:
            self.conn.rollback()
            print err
        finally:
            #关闭连接，释放资源     
            cursor.close(); 
            self.conn.close()
    def setcompleteid(self,userid):
        self.inition()
        #获取操作游标     
        cursor = self.conn.cursor()  
        try:
            cursor.execute("UPDATE weibocatch.w_user SET flag = 1 WHERE wid = %s",(userid,))
            #"只获取一条记录:"   
            self.conn.commit()
        except Exception as err:
            self.conn.rollback()
            print err
        finally:
            #关闭连接，释放资源     
            cursor.close(); 
            self.conn.close()
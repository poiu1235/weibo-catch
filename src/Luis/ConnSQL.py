#!/usr/bin/env python
#_*_ coding: utf-8_*_
'''
Created on 2015-8-8

@author: luis
'''
import ConfigParser
import MySQLdb
import hashlib
import os
import pymongo
import time

from Luis.Picreg import Picreg
from Luis.Relation import Relation
from Luis.Wconn import Wconn
from Luis.WeiboContent import WeiboContent
from Luis.WeiboTransfer import WeiboTransfer
from Luis.Werror import Werror
from Luis.Wuser import Wuser


class ConnSQL(object):
    
    def __init__(self):
        self.client=None
        pass
    def getconfig(self):
        try:
            config=ConfigParser.ConfigParser()
            with open('localconfig','r') as cfgfile:
                config.readfp(cfgfile)
                DBUSERNAME=config.get('db','dbuser')
                DBPASSWD=config.get('db','dbpwd')
                DBSITE=config.get('db','dbsite')
                return (DBUSERNAME,DBPASSWD,DBSITE)
        except:
            print "no config"
            os._exit()
    def inition(self):
        config=self.getconfig()
        self.conn=MySQLdb.Connect(host=config[2],user=config[0],passwd=config[1])#,charset='utf8'
        #选择数据库     
        self.conn.select_db('weibocatch');
        self.md5=hashlib.md5()
    def initionMo(self):
        config=self.getconfig()
        self.client = pymongo.MongoClient(config[2], 27017);
        self.db = self.client.weibocatch
        
    def class_to_dict(self,obj):
        '''把对象(支持单个对象、list、set)转换成字典'''
        is_list = obj.__class__ == [].__class__
        is_set = obj.__class__ == set().__class__
         
        if is_list or is_set:
            obj_arr = []
            for o in obj:
                #把Object对象转换成Dict对象
                dic = {}
                dic.update(o.__dict__)
                obj_arr.append(dic)
            return obj_arr
        else:
            dic = {}
            dic.update(obj.__dict__)
            return dic
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
                    self.conn.commit()
                    #1 生成的json不能输出汉字，只输出utf8原始编码，形如 u\x55..格式，
                    #需要在 json.dumps(xxxx,ensure_ascii=false,indent=1)参数列表指定 ensure_ascii=false
                    #2 indent =1 单行输出不换行， indent=2 多行输出如下
                    #insert_one 可以接受传入字典类型并存为json ，还有虽然字典里中文会编码，
                    #但是默认在mongodb里默认是utf8编码，字典里内容会自动转为明码标示。
                    wuserjson=self.class_to_dict(wuser)
                    self.initionMo()
                    table1=self.db.wuser
                    table1.insert_one(wuserjson)
                    print time.strftime('%H-%M-%S')+":"+"用户存入成功！"
                except Exception as err:
                    self.conn.rollback()
                    print time.strftime('%H-%M-%S')+":"+str(err)
                    if(err[0]!=1062):#判断不是主键重复错误
                        werror=Werror()
                        werror.id=wuser.id
                        werror.error=str(err)
                        self.seterror(werror)
                finally:
                    #关闭连接，释放资源     
                    cursor.close();
                    if(self.conn.open==1):
                        self.conn.close();
                    if(self.client!=None):
                        self.client.close()
            self.inition()
            cursor=self.conn.cursor()
            try:
                cursor.execute("""INSERT INTO weibocatch.w_relation
                                (wid,wfriendid)
                                VALUES
                                (%s,%s);
                                """,(relation.id,relation.friendid))
                self.conn.commit()
                #1 生成的json不能输出汉字，只输出utf8原始编码，形如 u\x55..格式，
                #需要在 json.dumps(xxxx,ensure_ascii=false,indent=1)参数列表指定 ensure_ascii=false
                #2 indent =1 单行输出不换行， indent=2 多行输出如下
                #insert_one 可以接受传入字典类型并存为json ，还有虽然字典里中文会编码，
                #但是默认在mongodb里默认是utf8编码，字典里内容会自动转为明码标示。
                relationjson=self.class_to_dict(relation)
                self.initionMo()
                table2=self.db.relation
                table2.insert_one(relationjson)
                print time.strftime('%H-%M-%S')+":"+"关注存入成功！"
            except Exception as err:
                self.conn.rollback()
                print time.strftime('%H-%M-%S')+":"+str(err)
                werror=Werror()
                werror.id=wuser.id
                werror.error=str(err)
                self.seterror(werror)
            finally:
                #关闭连接，释放资源     
                cursor.close();
                if(self.conn.open==1):
                    self.conn.close();
                if(self.client!=None):
                    self.client.close()
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
                weibocontentjson=self.class_to_dict(weibocontent)
                self.initionMo()
                table1=self.db.weibocontent
                table1.insert_one(weibocontentjson)
                if(isinstance(wconn, Wconn)):
                    if(wconn.tag==1 or wconn.tag==0):#判断字符串不为空
                        cursor.execute("""INSERT INTO weibocatch.w_conn
                                        (weiboid,tag,atid,atname)
                                        VALUES
                                        (%s,%s,%s,%s);""",(self.md5.hexdigest(),wconn.tag,
                                                           wconn.atid,wconn.atname))
                        #tag表示微博是来自原创还是转发，1是转发，0是原创
                        wconnjson=self.class_to_dict(wconn)
                        table2=self.db.wconn
                        table2.insert_one(wconnjson)
                self.conn.commit()# 一定不要漏了，不然不会执行的
                print time.strftime('%H-%M-%S')+":"+"%s原创微博存入成功" % weibocontent.id.encode('utf8')
            except Exception as err:
                self.conn.rollback()
                print time.strftime('%H-%M-%S')+":"+str(err)
                if(err[0]!=1062):
                    werror=Werror()
                    werror.id=weibocontent.id
                    werror.error=str(err)
                    self.seterror(werror)
            finally:
                #关闭连接，释放资源     
                cursor.close();
                if(self.conn.open==1):
                    self.conn.close() 
                if(self.client!=None):
                    self.client.close()
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
                weibotranjson=self.class_to_dict(weibotran)
                self.initionMo()
                table1=self.db.weibotran
                table1.insert_one(weibotranjson)
                if(isinstance(wconn, Wconn)):
                    if(wconn.tag==1 or wconn.tag==0):#判断字符串不为空
                        cursor.execute("""INSERT INTO weibocatch.w_conn
                                        (weiboid,tag,atid,atname)
                                        VALUES
                                        (%s,%s,%s,%s);""",(self.md5.hexdigest(),wconn.tag,
                                                           wconn.atid,wconn.atname))
                        wconnjson=self.class_to_dict(wconn)
                        table2=self.db.wconn
                        table2.insert_one(wconnjson)
                self.conn.commit()# 一定不要漏了，不然不会执行的
                print time.strftime('%H-%M-%S')+":"+"%s转发微博存入成功" % weibotran.id.encode('utf8')
            except Exception as err:
                self.conn.rollback()
                print time.strftime('%H-%M-%S')+":"+str(err)
                if(err[0]!=1062):
                    werror=Werror()
                    werror.id=weibotran.id
                    werror.error=str(err)
                    self.seterror(werror)
            finally:
                #关闭连接，释放资源     
                cursor.close();
                if(self.conn.open==1):
                    self.conn.close() 
                if(self.client!=None):
                    self.client.close()
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
                print time.strftime('%H-%M-%S')+":"+"图片存入成功"
                return result[0]
            except Exception as err:
                self.conn.rollback()
                print time.strftime('%H-%M-%S')+":"+str(err)
                werror=Werror()
                werror.id='00000'#图片路径存储异常
                werror.error=str(err)
                self.seterror(werror)
            finally:
                #关闭连接，释放资源     
                cursor.close();
                if(self.conn.open==1):
                    self.conn.close()
    def getuserid(self):
        self.inition()
        #获取操作游标     
        cursor = self.conn.cursor()  
        try:
            #注意一下啊，flag=0 未扒取任何内容，flag=1 扒取了用户关系，flag=2 扒取了微博信息
            #爬取用户信息用flag=0
            #爬取微博信息用flag=1
            cursor.execute("SELECT * FROM weibocatch.w_user where (recon=0 or (recon=1 and color=0)) and flag=1 order by inserttime limit 1")
            #"只获取一条记录:"   
            result = cursor.fetchone();#这个返回的是一个tuple
            return result
        except Exception as err:
            self.conn.rollback()
            print time.strftime('%H-%M-%S')+":"+str(err)
        finally:
            #关闭连接，释放资源     
            cursor.close(); 
            self.conn.close()
    def setcompleteid(self,userid):
        self.inition()
        #获取操作游标     
        cursor = self.conn.cursor()  
        try:
            ##注意一下啊，flag=0 未扒取任何内容，flag=1 扒取了用户关系，flag=2 扒取了微博信息
            cursor.execute("UPDATE weibocatch.w_user SET flag = 2 WHERE wid = %s",(userid,))
            #"只获取一条记录:"   
            self.conn.commit()
        except Exception as err:
            self.conn.rollback()
            print time.strftime('%H-%M-%S')+":"+str(err)
        finally:
            #关闭连接，释放资源     
            cursor.close(); 
            self.conn.close()
            
    def seterror(self,werror):
        if(isinstance(werror, Werror)):
            self.inition()
            #获取操作游标     
            cursor = self.conn.cursor()  
            try:
                cursor.execute("""INSERT INTO weibocatch.w_error
                                (wid,exception) VALUES (%s,%s);""",
                                (werror.id,werror.error))
                self.conn.commit()
            except Exception as err:
                self.conn.rollback()
                print time.strftime('%H-%M-%S')+":"+str(err)
            finally:
                #关闭连接，释放资源     
                cursor.close(); 
                self.conn.close()
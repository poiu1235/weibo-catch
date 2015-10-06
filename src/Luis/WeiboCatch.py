#!/usr/bin/env python
#_*_ coding: utf-8_*_
'''
Created on 2015-8-1
@author: luis
werror.id='00000'#图片路径存储异常
werror.id='33333'#图片下载超时或其他异常
werrorfriendid.id='44444'#访问名字用户页面被拒绝，拿到空id，所以赋值空id为44444，错误id也为44444
werrorovertime.id='55555'#用户id页面尝试次数过多
werrorovertime.id='66666'#用户列表页面尝试次数过多
werr.id='77777'#用户gethtm页面尝试次数过多
werr.id='88888'#用户getrealurl页面尝试次数过多
weibotransfer.tranferid='0000000000'#表示没有找到转发对象。。。这怎么可能。。。

如果下载图片返回id为空，表示图片未返回正确id，很可能是下载出错，没有下载下来
'''

from bs4 import BeautifulSoup
import cookielib
import random
import re
import socket
import string
import threading
import time
import urllib2

from Luis.Mailsender import Mailsender
from Luis.ConnSQL import ConnSQL
from Luis.Picreg import Picreg
from Luis.Relation import Relation
from Luis.Wconn import Wconn
from Luis.WeiboContent import WeiboContent
from Luis.WeiboTransfer import WeiboTransfer
from Luis.Werror import Werror
from Luis.Wuser import Wuser


#from _socket import timeout
#import Image
#import StringIO
#import requests
#import urllib
#reload(sys) 
#sys.setdefaultencoding( "utf-8" )#这个是因为插件报错，但是程序正常。
#str1.decode('gb2312')，表示将gb2312编码的字符串str1转换成unicode编码
#str2.encode('gb2312')，表示将unicode编码的字符串str2转换成gb2312编码。 
class WeiboCatch(object):
    classdbcomm=ConnSQL()#专供类方法调用的db操作类
    def __init__(self):
        self.filename='FileCookieJar.txt'
        self.dbcomm=ConnSQL()
    def getpagesize(self,prospect):
        time.sleep(3)
        count=0
        flag=1
        while (count<10 and flag==1):
            try:
                if(count>1):
                    tail=string.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a'], 5)).replace(' ','')
                    tailnumber=random.randint(1,10000)
                    surl="http://weibo.cn"+prospect+'?'+tail+'='+str(tailnumber)
                else:
                    surl="http://weibo.cn"+prospect
                print str(count)+'次尝试获取pagesize：'+surl
                req = urllib2.Request(surl)
                req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
                #req.add_header('Accept-Encoding','gzip, deflate')
                req.add_header('Accept-Language','zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
                #Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0')
                req.add_header('Referer','http://weibo.cn/')
                ckjar = cookielib.MozillaCookieJar()
                #这里读取cookie
                ckjar.load(self.filename, ignore_discard=True, ignore_expires=True)
                ckproc = urllib2.HTTPCookieProcessor(ckjar)
                #访问需要的微博页面
                opener = urllib2.build_opener(ckproc)
                f = opener.open(req,timeout=120)
                htm = f.read().decode('utf-8')
                ckjar.save(self.filename,ignore_discard=True, ignore_expires=True)
                f.close()
                opener.close()
                print htm
                tagerror='微博盗链举报'
                tagerror=tagerror.decode('utf8')
                soup=BeautifulSoup(htm).find('div',attrs={'id':'pagelist'})
                if(soup!=None):
                    strsize=soup.get_text().split('/')[-1]
                    strsize=strsize[:-1]
                    flag=0#因为有return 写不写都会跳出while循环
                    return strsize
                elif(htm.find(tagerror)!=-1):
                    count=count+1
                    time.sleep(60)
                    continue
                else:#只有一页的情况
                    flag=0#因为有return 写不写都会跳出while循环
                    return 1 
            except socket.timeout as e:
                print surl
                print "time out ,try again getpagesize %s" % count
                print type(e)    
                werr = Werror
                werr.id='77777'#用户gethtm页面尝试次数过多
                werr.error=surl
                self.dbcomm.seterror(werr)
                time.sleep(3) 
        if(count==10):
            werror=Werror()
            werror.id=prospect[1:11]
            werror.error=prospect+":"+'防盗链'
            self.dbcomm.seterror(werror)
            return None
    def getcurtime(self,timestr):
        timestr=timestr[:-1]#去掉最后一个空格
        todaystr='今天'
        monthstr='月'
        daystr='日'
        if(timestr.find(todaystr.decode('utf8'))!=-1):#把utf8解码成python默认的编码unicode
            return (time.strftime("%Y-%m-%d")+' '+timestr.split(' ')[1])
        elif(timestr.find(monthstr.decode('utf8'))!=-1):
            month=timestr.split(monthstr.decode('utf8'))[0]
            dayt=timestr.split(monthstr.decode('utf8'))[1]
            day=dayt.split(daystr.decode('utf8'))[0]
            return (time.strftime("%Y")+'-'+month+'-'+day+' '+timestr.split(' ')[1])
        else:
            return timestr
    def downloadpic(self,picurl):
        #设置读取目录是当前目录
        #但是虽然存文件方便了，但是由于当前路径变化导致不能正确读取当前cookies文件路径
        #os.chdir("/home/luis/workspace/weibo-catch/picture/")
        #os.getcwd()
        ppth="/home/luis/workspace/weibo-catch/picture/"
        tt=time.time()
        tts=str(tt)
        ran=random.randint(1, 99999999999)
        if(picurl.split('/')[-1].find('.')!=-1):
            filenamex=str(ran)+tts.split('.')[-1]+'.'+picurl.split('.')[-1]
        else:
            filenamex=str(ran)+tts.split('.')[-1]+'.'+'jpg'
        name=ppth+filenamex
        #opener = urllib2.build_opener(ckproc)
        #f = opener.open(req,timeout=90)
        #这里用了另外一种请求方法
        countt=0
        flag=1
        while(countt<10 and flag==1):
            try:
                #timeout=90 # in 90 seconds
                #socket.setdefaulttimeout(timeout)
                #data = urllib.urlopen(picurl).read()#urllib2才有timeout属性,timeout=90设置链接超时时间为90秒
                data=urllib2.urlopen(picurl, timeout=120).read()
                f = open(name,'wb',8192)#设置文件缓冲区为8M大小，有的图片较大怕一次存不完
                f.write(data)
                f.close()#close 方法相当于把缓冲区flush后再关闭的。
                print('Pic Saved!')
                flag=0
                return filenamex
            except urllib2.HTTPError as e: 
                print picurl
                print "try again pic_0 %s" % countt
                print "Error Code:", e.code 
                time.sleep(5) 
            except urllib2.URLError as e: 
                print picurl 
                print "try again pic_1 %s" % countt
                print "Error Reason:", e.reason
                time.sleep(5)
            except socket.timeout as e:
                print picurl
                print "time out ,try again pic_2 %s" % countt
                print type(e)   
                time.sleep(5)
            finally:
                countt=countt+1
        if(countt==10):
            #subprocess.call("pause",shell=True)#让程序暂停替换了os.system('pause')方法 或者用if(raw_input()): pass
            werrorovertime = Werror
            werrorovertime.id='33333'#用户下载pic尝试次数过多
            werrorovertime.error=picurl
            self.dbcomm.seterror(werrorovertime)
            return 'error.jpg'
    def getrealurl(self,aimurl):
        countt=0
        flag=1
        #这里的循环之所以没有起作用是因为正确执行后，return跳出了，否则会顺序执行的
        while(countt<10 and flag==1):
            try:
                tail=string.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a'], 5)).replace(' ','')
                tailnumber=random.randint(1,10000)
                tailstr=tail+'='+str(tailnumber)
                if(countt>1):
                    aimurlnew=aimurl+'&'+tailstr
                else:
                    aimurlnew=aimurl
                req = urllib2.Request(aimurlnew)
                req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
                #req.add_header('Accept-Encoding','gzip, deflate')
                req.add_header('Accept-Language','zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0')
                req.add_header('Referer','http://weibo.cn/')#设置通用请求方发,并不是每次都是由首页链接进入的,但是还是写上
                
                ckjar = cookielib.MozillaCookieJar()
                #这里读取cookie
                ckjar.load(self.filename, ignore_discard=True, ignore_expires=True)
                ckproc = urllib2.HTTPCookieProcessor(ckjar)
                #访问需要的微博页面
                opener = urllib2.build_opener(ckproc)
                f = opener.open(req,timeout=90)
                htm = f.read()
                reghtml=r'URL=(http://[\s\S]+|https://[\s\S]+)"'
                titletag='<title>跳转中</title>'
                if(htm.find(titletag)!=-1):
                    patternhtml=re.compile(reghtml)
                    return patternhtml.search(htm).group(1)
                else:
                    return 'video-audio-flash.com'
            except urllib2.HTTPError as e: 
                print aimurlnew
                print "try again realurl_0 %s" % countt
                print "Error Code:", e.code 
                time.sleep(60) 
            except urllib2.URLError as e: 
                print aimurlnew 
                print "try again realurl_1 %s" % countt
                print "Error Reason:", e.reason
                flag=0
                return "00null00"
                time.sleep(60)
            except socket.timeout as e:
                print aimurlnew
                print "time out ,try again realurl_2 %s" % countt
                print type(e)   
                werr = Werror
                werr.id='88888'#用户getrealurl页面尝试次数过多
                werr.error=aimurl
                self.dbcomm.seterror(werr)
                time.sleep(2) 
            finally:
                countt=countt+1
        if(countt==10):
            #subprocess.call("pause",shell=True)#让程序暂停替换了os.system('pause')方法 或者用if(raw_input()): pass
            werrorovertime = Werror
            werrorovertime.id='55555'#用户id页面尝试次数过多
            werrorovertime.error=aimurl
            self.dbcomm.seterror(werrorovertime)
            mail=Mailsender()
            mail.sendmail(time.strftime("%Y-%m-%d")+' '+"getrealurl程序被强制停止3小时")
            time.sleep(10801)
    def gethtm(self,aimurl):
        countt=0
        flag=1
        #这里的循环之所以没有起作用是因为正确执行后，return跳出了，否则会顺序执行的
        while(countt<10 and flag==1):
            try:
                tail=string.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a'], 5)).replace(' ','')
                tailnumber=random.randint(1,10000)
                tailstr=tail+'='+str(tailnumber)
                if(countt>1):
                    if(aimurl.find('?')!=-1):
                        aimurlnew=aimurl+'&'+tailstr
                    else:
                        aimurlnew=aimurl+'?'+tailstr
                else:
                    aimurlnew=aimurl
                print time.strftime('%H-%M-%S')+':'+str(countt)+'次尝试获取id：'+aimurlnew
                req = urllib2.Request(aimurlnew)
                req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
                #req.add_header('Accept-Encoding','gzip, deflate')
                req.add_header('Accept-Language','zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0')
                req.add_header('Referer','http://weibo.cn/')#设置通用请求方发,并不是每次都是由首页链接进入的,但是还是写上
                ckjar = cookielib.MozillaCookieJar()
                #这里读取cookie
                ckjar.load(self.filename, ignore_discard=True, ignore_expires=True)
                ckproc = urllib2.HTTPCookieProcessor(ckjar)
                #访问需要的微博页面
                opener = urllib2.build_opener(ckproc)
                f = opener.open(req,timeout=90)
                htm = f.read()
                urltemp=f.url
                #print htm
                f.close()
                opener.close()
                print urltemp
            except urllib2.HTTPError as e:# 原版本except urllib2.HTTPError, e:是没有用as的
                print aimurlnew
                print "try again gethtm_0 %s" % countt 
                print type(e) #这个也是新加上的
                print "Error Code:", e.code
                time.sleep(60)
            except urllib2.URLError as e: 
                print aimurlnew 
                print "try again gethtm_1 %s" % countt
                print "Error Reason:", e.reason
                print type(e)
                time.sleep(60)
            except socket.timeout as e:
                print aimurlnew
                print "time out ,try again gethtm_2 %s" % countt
                print type(e)    
                werr = Werror
                werr.id='77777'#用户gethtm页面尝试次数过多
                werr.error=aimurl
                self.dbcomm.seterror(werr)
                time.sleep(2)  
            else:
                #print htm
                
                #not htm.strip()判断空  htm 可以被“剥开”，意思就是有内容可以剥开
                #现在两种处理办法，要么按？划分，因为链接带问号表示带参数，而文件是不可以带参数的
                #要么按照. 划分，只有文件才会带后缀
                #可能会出现这样的url：http://weibo.cn/rmrf?eoisn=73
                if(urltemp.find('search/user/?keyword=')!=-1):
                    flag=0
                    print '用户不存在'
                    return '0000000000' 
                regnotfind='请尝试更换关键词，再次搜索'
                if(htm.find(regnotfind)!=-1):
                    flag=0
                    return '0000000000' #用户不存在
                regdelete='此用户不存在或更改了名字'
                if(htm.find(regdelete)!=-1):
                    flag=0
                    return '0000000000' #用户不存在
                elif(urltemp.find('?')!=-1 and urltemp.find(tailstr)==-1):
                    #拿id有时候会访问不到，所以加上了随机数参数，url里包含了？，加入其他的url判别条件来判断是否来自图片请求
                    regff="图片加载中"#因为f.read()方法读到的是str类型，默认是utf8， 可以直接用str类型进行查找，不用进行转码decode操作
                    regdel="页面不存在或已被删除"
                    if(htm.find(regdel)==-1):#作者把图片已删除
                        if(htm.find(regff)==-1):#这是一种特殊的情况，询问：“图片过大是否继续打开”
                            regpicsubmit=r'<a href="([\s\S]+?.sinaimg.cn/[\s\S]+?)">[\s\S]+?</a>'
                            patternp=re.compile(regpicsubmit)
                            urlpicsubmit=patternp.search(htm).group(1)
                            flag=0
                            return self.downloadpic(urlpicsubmit)
                        else:
                            #拿到图片列表网页
                            flag=0#正常执行就可以跳出循环了
                            return htm.decode('utf-8')
                    else:
                        return 'del.jpg'
                elif(urltemp.find('.sinaimg.cn')!=-1):
                    #纯粹的就是图片链接和文件名，用的是http://ww3.sinaimg.cn/域名，与微博无关
                    flag=0#正常执行就可以跳出循环了
                    return(self.downloadpic(urltemp))#其实这一步已经拿到了img，为了获取文件后缀名和程序结构统一，又重新获取了一次
                elif(urltemp.find('weibo.cn/pub/')!=-1):
                    print 'weibo.cn/pub/sleep'
                    time.sleep(60)
                    continue
                if(BeautifulSoup(htm).find('span', attrs={'class':'tc'})!=None):#拿到朋友id
                    partcut=BeautifulSoup(htm).find('span', attrs={'class':'tc'})
                    idstr=partcut.parent.find('a')["href"]
                    flag=0#正常执行就可以跳出循环了
                    return idstr.split('/')[1]
            finally:
                countt=countt+1
        if(countt==10):
            #subprocess.call("pause",shell=True)#让程序暂停替换了os.system('pause')方法 或者用if(raw_input()): pass
            werrorovertime = Werror
            werrorovertime.id='55555'#用户id页面尝试次数过多
            werrorovertime.error=aimurl
            self.dbcomm.seterror(werrorovertime)
            mail=Mailsender()
            mail.sendmail(time.strftime("%Y-%m-%d")+' '+"gethtm程序被强制停止3小时")
            time.sleep(10801)
    def catchfollow(self,follow):
        #htm=follow
        #"""
        try:
            size=int(self.getpagesize(follow))
        except Exception as err:
            werrorovertime = Werror
            werrorovertime.id='99999'#用户列表页面尝试次数过多
            werrorovertime.error=time.strftime('%H-%M-%S')+str(err)+"###"+follow+' follow: pagesize geterror'
            mail=Mailsender()
            mail.sendmail(time.strftime("%Y-%m-%d")+' '+"pagesize:"+werrorovertime.error)
            time.sleep(10801)
        else:
            for i in range(1,size+1):#因为python的后界是不包括的！！！
                time.sleep(3)#每换一页停3秒
                #i=19
                #follow ='/3031330053/follow'
                surl="http://weibo.cn"+follow+"?page="+str(i)
                count=0
                flag=1
                errstr=""
                followcuts=""
                while(count<10 and flag==1):
                    try:
                        if(count>1):
                            tail=string.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a'], 5)).replace(' ','')
                            tailnumber=random.randint(1,10000)
                            surl="http://weibo.cn"+follow+"?page="+str(i)+'&'+tail+'='+str(tailnumber)
                        print str(count)+'次尝试页面list：'+surl
                        req = urllib2.Request(surl)
                        req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
                        #req.add_header('Accept-Encoding','gzip, deflate')
                        req.add_header('Accept-Language','zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0')
                        req.add_header('Referer','http://weibo.cn/')
                        ckjar = cookielib.MozillaCookieJar()
                        #这里读取cookie
                        ckjar.load(self.filename, ignore_discard=True, ignore_expires=True)
                        ckproc = urllib2.HTTPCookieProcessor(ckjar)
                        #访问需要的微博页面
                        opener = urllib2.build_opener(ckproc)
                        f = opener.open(req,timeout=90)
                        htm = f.read().decode('utf-8')
                        ckjar.save(self.filename,ignore_discard=True, ignore_expires=True)
                        f.close()
                        opener.close()
                        #print htm
                        #"""
                        tagerror='微博盗链举报'
                        tagerror=tagerror.decode('utf8')
                        if(htm.find(tagerror)!=-1):
                            count=count+1
                            time.sleep(60)#停顿60秒
                            continue
                        followcuts =BeautifulSoup(htm).findAll('td', attrs={'valign':'top'})[1::2]#表示取出偶数位置的元素
                        flag=0
                    except Exception as err:
                        print(str(err)+str(err.message))
                        errstr=errstr+"\n"+(str(err)+str(err.message))
                if(count==10):
                    werror=Werror()
                    werror.id=follow[1:11]
                    werror.error="catchfollows:id:"+follow[1:11]+":"+"page:"+str(i)+":"+'防盗链'
                    self.dbcomm.seterror(werror)
                    mail=Mailsender()
                    mail.sendmail(time.strftime("%Y-%m-%d")+' '+errstr+"##"+"catchfollow程序被强制停止3小时")
                    time.sleep(10801)#如果count>9 暂停3小时
                        
                for followitem in followcuts:
                    try:
                        time.sleep(3)#不得不设置频率3秒一次
                        rega=u'<a href="http://weibo.cn/u/(\d+)">([\s\S]+?)</a>'
                        patterna=re.compile(rega)
                        #注意每个beautifulsoup对象截取出来的对象都是”特定的标签“对象，可以直接进行beautifulsoup相关操作
                        #而不是字符串类型，如果要进行一些字符串操作，必须要转成str（） 类型。
                        #Beautiful Soup用了 编码自动检测 子库来识别当前文档编码并转换成Unicode编码
                        #通过Beautiful Soup输出文档时,不管输入文档是什么编码方式,输出编码均为UTF-8编码
                        #但是像index 和 单纯的 find 方法会转成unicode编码方式再来操作，执行完后就要转码成utf8操作。
                        #即先转码再转回来（先decode（‘utf8’）再encode（‘utf8’））
                        relation=Relation()
                        wuser=Wuser()
                        if(patterna.search(str(followitem))is not None):
                            relation.friendid=patterna.search(str(followitem)).group(1)
                            relation.id=follow[1:11]#只取到了10位id 或者split('/')[0]
                            wuser.id=patterna.search(str(followitem)).group(1)
                            wuser.name=patterna.search(str(followitem)).group(2)
                        else:
                            regb=u'<a href="http://weibo.cn/[\s\S]+?">([\s\S]+?)</a>'
                            patternb=re.compile(regb)#截取用户名，因为认证用户有自己的用户名，可以不用id访问
                            regc=r'<a href="(http://weibo.cn/[\s\S]+?)">[\s\S]+?</a>'#和可能出现多个匹配上的情况，所以加长了<img标签
                            patternc=re.compile(regc)#截取id，还是想获取用户id
                            friendurl=patternc.search(str(followitem)).group(1)
                            friendid=self.gethtm(friendurl)
                            print '用户名称url的id：'+friendid
                            if(friendid!=None):
                            #friendhtm=self.gethtm(friendurl)
                            #regd=r"([\d]{10})"
                            #patternd=re.compile(regd)
                            #if(patternd.search(friendhtm).group(1)!=friendhtm):
                                #rege=r'<a href="/([\d]+)/info">[\s\S]+?</a>'
                                #patterne=re.compile(rege)
                                #relation.friendid=patterne.search(friendhtm).group(1)
                                #wuser.id=patterne.search(friendhtm).group(1)
                            #else:
                                #relation.friendid=patternd.search(friendhtm).group(1)
                                #wuser.id=patternd.search(friendhtm).group(1)
                                relation.friendid=friendid
                                wuser.id=friendid
                                relation.id=follow[1:11]
                                wuser.name=patternb.search(str(followitem)).group(1)
                            else:
                                werrorfriendid=Werror()
                                werrorfriendid.id='44444'#访问名字用户页面被拒绝，拿到空id，所以赋值空id为44444，错误id也为44444
                                werrorfriendid.error='44444'+'：被屏蔽无法获取该用户id'
                                self.dbcomm.seterror(werrorfriendid)
                                continue
                        if(followitem.find('img',attrs={'src':'http://u1.sinaimg.cn/upload/2011/07/28/5337.gif'}) is not None):#蓝v认证
                            wuser.recon=1
                            wuser.color=1
                        elif(followitem.find('img',attrs={'src':'http://u1.sinaimg.cn/upload/2011/07/28/5338.gif'})is not None):#黄v认证
                            wuser.recon=1
                            wuser.color=0
                        else:#普通用户
                            wuser.recon=0
                            wuser.color=0
                        self.dbcomm.insertuser(wuser,relation)
                    except Exception as err:
                        print(time.strftime("%Y-%m-%d")+' '+str(err)+str(err.message))
                        werrorfollowid=Werror()
                        werrorfollowid.id=follow[1:11]
                        werrorfollowid.error=follow[1:11]+"page="+str(i)+'截取内容出错'
                        self.dbcomm.seterror(werrorfollowid)
                           
    def catchprofile(self,profile):
        #"""
        #htm=profile
        #"""
        #"""
        try:
            size=self.getpagesize(profile)
            if(int(size)>30):
                pagecount=30#最多只取出前三十页微博
            else:
                pagecount=int(size)
        except Exception as err:
            werrorovertime = Werror
            werrorovertime.id='99999'#用户列表页面尝试次数过多
            werrorovertime.error=time.strftime('%H-%M-%S')+str(err)+"###"+profile+' profile: pagesize geterror'
            mail=Mailsender()
            mail.sendmail(time.strftime("%Y-%m-%d")+' '+"pagesize:"+werrorovertime.error)
            time.sleep(10801)
        else:
            for i in range(1,pagecount+1):
                time.sleep(3)#每次完成一个任务就暂停3秒
                surl="http://weibo.cn"+profile+"?page="+str(i)
                count=0
                flag=1
                errstr=""
                profilecut=""
                while(count<10 and flag==1):
                    try:
                        if(count>1):
                            tail=string.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a'], 5)).replace(' ','')
                            tailnumber=random.randint(1,10000)
                            surl="http://weibo.cn"+profile+"?page="+str(i)+'&'+tail+'='+str(tailnumber)
                        print str(count)+'次尝试页面list：'+surl
                        req = urllib2.Request(surl)
                        req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
                        #req.add_header('Accept-Encoding','gzip, deflate')
                        req.add_header('Accept-Language','zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0')
                        req.add_header('Referer','http://weibo.cn/')
                        ckjar = cookielib.MozillaCookieJar()
                        #这里读取cookie
                        ckjar.load(self.filename, ignore_discard=True, ignore_expires=True)
                        ckproc = urllib2.HTTPCookieProcessor(ckjar)
                        #访问需要的微博页面
                        opener = urllib2.build_opener(ckproc)
                        f = opener.open(req,timeout=90)
                        htm = f.read().decode('utf8')
                        ckjar.save(self.filename,ignore_discard=True, ignore_expires=True)
                        f.close()
                        opener.close()
                        print htm
                        tagerror='微博盗链举报'
                        tagerror=tagerror.decode('utf8')
                        if(htm.find(tagerror)!=-1):
                            count=count+1
                            time.sleep(60)#停顿60秒
                            continue
                    #"""
                    #这里要特殊处理，后面两个class=‘c’的标签是脚注和尾栏
                    
                        profilecut= BeautifulSoup(htm).findAll('div', attrs = {'class':'c'})[0:-2]
                        flag=0
                    except Exception as err:
                        print(str(err)+str(err.message))
                        errstr=errstr+"\n"+(str(err)+str(err.message))
                if(count==10):
                    werror=Werror()
                    werror.id=profile[1:11]
                    werror.error="catchprofiles:id:"+profile[1:11]+":"+"page:"+str(i)+":"+'防盗链'
                    self.dbcomm.seterror(werror)
                    mail=Mailsender()
                    mail.sendmail(time.strftime("%Y-%m-%d")+' '+errstr+"##"+"catchprofile程序被强制停止3小时")
                    time.sleep(10801)#如果count>9 暂停3小时
                for cut in profilecut:
                    #一般的字符串操作有rfind 从后前前找，beautifulsoup没有
                    try:
                        time.sleep(3)
                        contentcut1=cut.find('span',attrs={'class':'cmt'})
                        contentcut2=cut.find('span',attrs={'class':'ctt'})
                        contenttemp=cut.findAll('span',attrs={'class':'cmt'})
                        if(len(contenttemp)!=0):
                            contentcut3=contenttemp[-1]
                        contentcut4=cut.find('span',attrs={'class':'ct'})
                        delstr='抱歉，此微博已被作者删除'
                        #transtr='转发了'
                        if(contentcut1 is not None and contentcut2.get_text().find(delstr.decode('utf8'))==-1):#后面的条件表示原微博没有被删除
                            #说明是转发的
                            picreg=Picreg()
                            weibotransfer=WeiboTransfer()
                            wconn=Wconn()
                            splitf="来自"
                            intime=contentcut4.get_text().split(splitf.decode('utf8'))[0]
                            textlow='分钟前'
                            if (intime.find(textlow.decode('utf8'))!=-1):
                                continue;
                            weibotransfer.intime=self.getcurtime(intime)
                            weibotransfer.wfrom=contentcut4.get_text().split(splitf.decode('utf8'))[1]
                            weibotransfer.id=profile[1:11]#只取到了10位id
                            if(contentcut1.find('a')!=None):
                                userurl=contentcut1.find('a')["href"]##这里有时候会出错，找不到转发id
                                weibotransfer.tranferid=self.gethtm(userurl)
                            else:
                                weibotransfer.tranferid='0000000000'#表示没有找到转发对象。。。这怎么可能。。。
                            remark=contentcut3.parent.get_text()
                            splittag='赞'
                            sptag=splittag.decode('utf8')
                            remark=remark.split(sptag)[0]
                            xy='转发理由:'
                            remark=remark.replace(xy.decode('utf8'),'')
                            if(remark.find('//')!=-1):#表示不是原文转发
                                remark=remark.split('//')[0]
                                if(remark.find('@')!=-1):#判断是否真的是@了其他人,#并且有多个@对象
                                    regm=u"(@[\s\S]+?)<"
                                    patternm=re.compile(regm)
                                    #不可以用remove 方法，包括del pop这些方法只有list有
                                    #remove 是按照关键字删除，但是del 和pop 是按照索引删除
                                    sxx=patternm.finditer(str(contentcut3.parent))
                                    atuserid=""
                                    atusername=""
                                    for item in sxx:
                                        userurl=contentcut3.parent.find('a',text=item.group(1))["href"]
                                        userhtm=self.gethtm("http://weibo.cn"+userurl)
                                        atuserid=atuserid+userhtm+";"
                                        atusername=atusername+item.group(1)[1:]+";"#去掉前面的@符号
                                    atuserid=atuserid[:-1]
                                    atusername=atusername[:-1]
                                    wconn.atid=atuserid
                                    wconn.atname=atusername
                                    wconn.tag=1
                                else:# 也有可能是英文或者故意加入了很多空格
                                    remark=remark.strip()
                            else:#表示是原文转发的情况 
                                #表示去掉字串两头的空格,s.strip(rm)删除s字符串中开头、结尾处，位于rm序列里的字符，      
                                #当rm为空时，默认删除空白符（包括'\n', '\r',  '\t',  ' ')
                                #拿到没有标签框住的文字，在beautifulsoup里也被当作一种特殊的string标签
                                #remark=contentcut3.next_sibling.strip()
                                if(remark.find('@')!=-1):#判断是否真的是@了其他人,#并且有多个@对象
                                    regm=u"(@[\s\S]+?)<"
                                    patternm=re.compile(regm)
                                    #不可以用remove 方法，包括del pop这些方法只有list有
                                    #remove 是按照关键字删除，但是del 和pop 是按照索引删除
                                    sxx=patternm.finditer(str(contentcut3.parent))
                                    atuserid=""
                                    atusername=""
                                    for item in sxx:
                                        userurl=contentcut3.parent.find('a',text=item.group(1))["href"]
                                        userhtm=self.gethtm("http://weibo.cn"+userurl)
                                        atuserid=atuserid+userhtm+";"
                                        atusername=atusername+item.group(1)[1:]+";"#去掉前面的@符号
                                    atuserid=atuserid[:-1]
                                    atusername=atusername[:-1]
                                    wconn.atid=atuserid
                                    wconn.atname=atusername
                                    wconn.tag=1
                                else:# 也有可能是英文或者故意加入了很多空格
                                    remark=remark.strip()
                            weibotransfer.remark=remark.strip()
                            #get_text() 方法可以拿到全部内容，而content数组拿到的是被内层标签分段内容块。
                            transfercon=contentcut2.get_text()
                            reg=r"#([\s\S]*?)#" #配对标签
                            reg1=r'<a href="(http://weibo.cn/sinaurl?[\s\S]+?)">(http://t.cn/[\s\S]+?)</a>' #配对url
                            pattern=re.compile(reg)
                            pattern1=re.compile(reg1)
                            #match 是从头开始匹配，只有第一个配对上了才算，search 可以从任何地方匹配，相当于找子串
                            if(pattern.search(transfercon) is not None):
                                so=pattern.finditer(transfercon)
                                for label in so:
                                    transfercon=transfercon.replace(label.group(0),"")
                                    weibotransfer.label+=label.group(1)+"#-#"
                                weibotransfer.label=weibotransfer.label[0:-3]
                            if(pattern1.search(str(contentcut2.parent)) is not None):
                                so1=pattern1.finditer(str(contentcut2.parent))
                                for url in so1:
                                    transfercon=transfercon.replace(url.group(2),"")
                                    urlre=self.getrealurl(url.group(1).replace('&amp;','&').replace(' ',''))
                                    weibotransfer.url+=urlre+"#-#"
                                weibotransfer.url=weibotransfer.url[0:-3]
                            weibotransfer.content=transfercon
                            if(contentcut2.parent.next_sibling.find('img') is not None):
                                picdir=""
                                if(contentcut2.parent.find('a',text=re.compile(u"组图共\d张")) is not None):#a
                                    picurl=contentcut2.parent.findAll('a')[-1]["href"]
                                    pichtm=self.gethtm(picurl)
                                    s="原图"
                                    sx=s.decode('utf-8')
                                    pictmp=BeautifulSoup(pichtm)
                                    piclist=pictmp.findAll('a',text=sx)
                                    for picurl in piclist:
                                        pichtm=self.gethtm("http://weibo.cn"+picurl["href"])
                                        if(pichtm==None):
                                            pichtm=""
                                        picdir=picdir+pichtm+";"
                                    picdir=picdir[:-1]
                                    picreg.picpath=picdir
                                    picreg.picid=self.dbcomm.insertpic(picreg)
                                else:
                                    s="原图"
                                    sx=s.decode('utf-8')#千万要注意不能把两句写在一起，动态编译不会识别的
                                    if(contentcut2.parent.next_sibling.find('a',text=sx)!=None):
                                        picurl=contentcut2.parent.next_sibling.find('a',text=sx)["href"]
                                        pichtm=self.gethtm(picurl)
                                        if(pichtm==None):
                                            pichtm=""
                                        picdir=pichtm
                                        picreg.picpath=picdir
                                        picreg.picid=self.dbcomm.insertpic(picreg)
                            self.dbcomm.inserttran(weibotransfer,picreg.picid,wconn)
                        else:
                            weibocontent=WeiboContent()
                            picreg=Picreg()
                            wconn=Wconn()
                            splitf="来自"
                            intime=contentcut4.get_text().split(splitf.decode('utf8'))[0]
                            textlow='分钟前'
                            if (intime.find(textlow.decode('utf8'))!=-1):
                                continue;
                            weibocontent.intime=self.getcurtime(intime)
                            weibocontent.wfrom=contentcut4.get_text().split(splitf.decode('utf8'))[1]
                            contentcut2=cut.find('span',attrs={'class':'ctt'})
                            weibocontent.id=profile[1:11]
                            alltext=contentcut2.get_text()
                            posflag='[位置]'
                            if(alltext.find(posflag.decode('utf8'))!=-1):#如果有位置信息
                                position=alltext.split(posflag.decode('utf8'))[1]
                                alltext=alltext.split(posflag.decode('utf8'))[0]
                                weibocontent.map=position#(其实后来想想这个地方应该用经纬坐标会更好)
                            if(alltext.find('@')!=-1):#如果有艾特其他人
                                regm=u"(@[\s\S]+?)<"
                                patternm=re.compile(regm)
                                #不可以用remove 方法，包括del pop这些方法只有list有
                                #remove 是按照关键字删除，但是del 和pop 是按照索引删除
                                sxx=patternm.finditer(str(contentcut2))
                                atuserid=""
                                atusername=""
                                for item in sxx:
                                    userurl=contentcut2.parent.find('a',text=item.group(1))["href"]
                                    userhtm=self.gethtm("http://weibo.cn"+userurl)
                                    atuserid=atuserid+userhtm+";"
                                    atusername=atusername+item.group(1)[1:]+";"#去掉@符号
                                atuserid=atuserid[:-1]
                                atusername=atusername[:-1]
                                wconn.atid=atuserid
                                wconn.atname=atusername
                                wconn.tag=0
                            reg=r"#([\s\S]*?)#" #配对标签
                            reg1=r'(http://weibo.cn/sinaurl?[\s\S]+?)">(http://t.cn/[\s\S]+?)</a>' #配对url
                            pattern=re.compile(reg)
                            pattern1=re.compile(reg1)
                            if(pattern.search(alltext) is not None):
                                so=pattern.finditer(alltext)
                                for label in so:
                                    alltext=alltext.replace(label.group(0),"")
                                    weibocontent.label+=label.group(1)+"#-#"
                                weibocontent.label=weibocontent.label[0:-3]
                            if(pattern1.search(str(contentcut2.parent)) is not None):
                                so1=pattern1.finditer(str(contentcut2.parent))
                                for url in so1:
                                    alltext=alltext.replace(url.group(2),"")
                                    urlre=self.getrealurl(url.group(1).replace('&amp;','&').replace(' ',''))
                                    if(urlre==None):
                                        urlre=""
                                    weibocontent.url+=urlre+"#-#"
                                weibocontent.url=weibocontent.url[0:-3]
                            weibocontent.content=alltext
                            if(contentcut2.parent.next_sibling is not None):
                                picdir=""
                                if(contentcut2.parent.find('a',text=re.compile(u"组图共\d张")) is not None):#a
                                    picurl=contentcut2.parent.findAll('a')[-1]["href"]
                                    pichtm=self.gethtm(picurl)
                                    s="原图"
                                    sx=s.decode('utf-8')
                                    pictmp=BeautifulSoup(pichtm)
                                    piclist=pictmp.findAll('a',text=sx)
                                    for picurl in piclist:
                                        pichtm=self.gethtm("http://weibo.cn"+picurl["href"])
                                        if(pichtm==None):
                                            pichtm=""
                                        picdir=picdir+pichtm+";"
                                    picdir=picdir[:-1]
                                    picreg.picpath=picdir
                                    picreg.picid=self.dbcomm.insertpic(picreg)
                                else:
                                    s="原图"
                                    sx=s.decode('utf-8')#千万要注意不能把两句写在一起，动态编译不会识别的
                                    if(contentcut2.parent.next_sibling.find('a',text=sx)!=None):
                                        picurl=contentcut2.parent.next_sibling.find('a',text=sx)["href"]
                                        pichtm=self.gethtm(picurl)
                                        if(pichtm==None):
                                            pichtm=""
                                        picdir=pichtm
                                        picreg.picpath=picdir
                                        picreg.picid=self.dbcomm.insertpic(picreg)
                            self.dbcomm.insertcont(weibocontent,picreg.picid,wconn)
                    #补充一点，双引号会对内容进行转义，单引号则不会
                    except Exception as err:
                        print(time.strftime("%Y-%m-%d")+' '+str(err)+str(err.message))
                        werrorprofileid=Werror()
                        werrorprofileid.id=profile[1:11]
                        werrorprofileid.error=profile[1:11]+"page="+str(i)+'截取内容出错'
                        self.dbcomm.seterror(werrorprofileid)
    #类方法，用classmethod来进行修饰
    #类方法的隐含调用参数是类，而类实例方法的隐含调用参数是类的实例，静态方法没有隐含调用参数
    @classmethod
    def findweibo(cls,sweb):
        """reg1=u"<a href=\"(/\d+/follow)\">[\u4E00-\u9FA5]{2}\[\d+]</a>"
        pattern1=re.compile(reg1)
        weibofollow=pattern1.search(sweb).group(1)
        print weibofollow
        reg2=u"<a href=\"(/\d+/profile)\">[\u4E00-\u9FA5]{2}\[\d+]</a>"
        pattern2=re.compile(reg2)
        weiboporfile=pattern2.search(sweb).group(1)
        print weiboporfile
        obj=WeiboCatch()
        threads = []
        t1 = threading.Thread(target=obj.catchfollow,args=(weibofollow,))
        threads.append(t1)
        t2 = threading.Thread(target=obj.catchprofile,args=(weiboporfile,))
        threads.append(t2)
        for t in threads:
            t.setDaemon(True)
            t.start()
        #注意:join()方法的位置是在for循环外的，也就是说必须等待for循环里的两个进程都结束后，才去执行主进程。
        #或者结合flag 和while 来判断 程程是否还有效 
        #is_alive(): Return whether the thread is alive.
        for t in threads:
            t.join()
        """
        print "self task is all over "
        print "other person task is begin"
        #这是爬内容的程序
        flagg=1
        while(flagg):
            user=cls.classdbcomm.getuserid()
            time.sleep(30)#换一个人停30秒
            if(user is not None):
                userid=user[0]
                obj=WeiboCatch()
                threads = []
                #t1 = threading.Thread(target=obj.catchfollow,args=("/"+userid+"/follow",))
                #threads.append(t1)
                t2 = threading.Thread(target=obj.catchprofile,args=("/"+userid+"/profile",))
                threads.append(t2)
                for t in threads:
                    t.setDaemon(True)
                    t.start()
                #注意:join()方法的位置是在for循环外的，也就是说必须等待for循环里的两个进程都结束后，才去执行主进程。
                #或者结合flag 和while 来判断 程程是否还有效 
                #is_alive(): Return whether the thread is alive.
                for t in threads:
                    t.join()
                cls.classdbcomm.setcompleteid(userid)
            else:
                flagg=0
if __name__ == '__main__':
    #WeiboCatch().catchprofile(profile);
    #WeiboCatch().catchfollow(follow)
    WeiboCatch.findweibo("sweb")
#!/usr/bin/env python
#_*_ coding: utf-8_*_
'''
Created on 2015-8-1
@author: luis
'''
from bs4 import BeautifulSoup
import cookielib
import random
import re
import subprocess
import threading
import time
import urllib
import urllib2

from Luis.ConnSQL import ConnSQL
from Luis.Picreg import Picreg
from Luis.Relation import Relation
from Luis.Wconn import Wconn
from Luis.WeiboContent import WeiboContent
from Luis.WeiboTransfer import WeiboTransfer
from Luis.Wuser import Wuser


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
        surl="http://weibo.cn"+prospect
        print surl
        req = urllib2.Request(surl)
        req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        #req.add_header('Accept-Encoding','gzip, deflate')
        req.add_header('Accept-Language','zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
        req.add_header('Referer','http://weibo.cn/')
        ckjar = cookielib.MozillaCookieJar()
        #这里读取cookie
        ckjar.load(self.filename, ignore_discard=True, ignore_expires=True)
        ckproc = urllib2.HTTPCookieProcessor(ckjar)
        #访问需要的微博页面
        opener = urllib2.build_opener(ckproc)
        f = opener.open(req) 
        htm = f.read().decode('utf-8')
        ckjar.save(self.filename,ignore_discard=True, ignore_expires=True)
        f.close()
        print htm
        
        soup=BeautifulSoup(htm).find('div',attrs={'id':'pagelist'})
        strsize=soup.get_text().split('/')[-1]
        strsize=strsize[:-1]
        return strsize
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
        filenamex=str(ran)+tts.split('.')[-1]+'.'+picurl.split('.')[-1]
        name=ppth+filenamex
        data = urllib.urlopen(picurl).read()
        f = open(name,'wb',8192)#设置文件缓冲区为8M大小，有的图片较大怕一次存不完
        f.write(data)
        f.close#close 方法相当于把缓冲区flush后再关闭的。
        print('Pic Saved!')
        return filenamex
    def gethtm(self,aimurl):
        countt=0
        flag=1
        #这里的循环之所以没有起作用是因为正确执行后，return跳出了，否则会顺序执行的
        while(countt<10 and flag==1):
            try:
                req = urllib2.Request(aimurl)
                req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
                #req.add_header('Accept-Encoding','gzip, deflate')
                req.add_header('Accept-Language','zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
                req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
                req.add_header('Referer','http://weibo.cn/')#设置通用请求方发,并不是每次都是由首页链接进入的,但是还是写上
                ckjar = cookielib.MozillaCookieJar()
                #这里读取cookie
                ckjar.load(self.filename, ignore_discard=True, ignore_expires=True)
                ckproc = urllib2.HTTPCookieProcessor(ckjar)
                #访问需要的微博页面
                opener = urllib2.build_opener(ckproc)
                f = opener.open(req) 
                htm = f.read()
            except urllib2.HTTPError, e:
                print "try again %s" % countt  
                print "Error Code:", e.code  
            except urllib2.URLError, e:  
                print "Error Reason:", e.reason
            else:
                #print htm
                if(f.url.find('weibo.cn/u/')!=-1):#拿到朋友id
                    flag=0#正常执行就可以跳出循环了
                    return f.url.split('/')[-1]
                #not htm.strip()判断空  htm 可以被“剥开”，意思就是有内容可以剥开
                #现在两种处理办法，要么按？划分，因为链接带问号表示带参数，而文件是不可以带参数的
                #要么按照. 划分，只有文件才会带后缀
                if(f.url.find('?') !=-1 or f.url.find('weibo.cn/')!=-1):#前面一个找图片集中页面，后面一个找企业朋友的id
                    regff="图片加载中"#因为f.read()方法读到的是str类型，默认是utf8， 可以直接用str类型进行查找，不用进行转码decode操作
                    if(htm.find(regff)==-1):#这是一种特殊的情况，询问：“图片过大是否继续打开”
                        regpicsubmit=r'<a href="([\s\S]+?.sinaimg.cn/[\s\S]+?)">[\s\S]+?</a>'
                        patternp=re.compile(regpicsubmit)
                        urlpicsubmit=patternp.search(htm).group(1)
                        flag=0
                        return self.downloadpic(urlpicsubmit)
                    else:
                        flag=0#正常执行就可以跳出循环了
                        return htm.decode('utf-8')
                else:#纯粹的就是图片链接和文件名，用的是http://ww3.sinaimg.cn/域名，与微博无关
                    flag=0#正常执行就可以跳出循环了
                    return(self.downloadpic(f.url))#其实这一步已经拿到了img，为了获取文件后缀名和程序结构统一，又重新获取了一次
            finally:
                countt=countt+1
                f.close()
                opener.close()
        if(countt==10):
            subprocess.call("pause",shell=True)#让程序暂停替换了os.system('pause')方法 或者用if(raw_input()): pass
    def catchfollow(self,follow):
        #htm=follow
        #"""
        size=self.getpagesize(follow)
        for i in range(1,int(size)):
            time.sleep(2)
            surl="http://weibo.cn"+follow+"?page="+str(i)
            print surl
            req = urllib2.Request(surl)
            req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            #req.add_header('Accept-Encoding','gzip, deflate')
            req.add_header('Accept-Language','zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
            req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
            req.add_header('Referer','http://weibo.cn/')
            ckjar = cookielib.MozillaCookieJar()
            #这里读取cookie
            ckjar.load(self.filename, ignore_discard=True, ignore_expires=True)
            ckproc = urllib2.HTTPCookieProcessor(ckjar)
            #访问需要的微博页面
            opener = urllib2.build_opener(ckproc)
            f = opener.open(req) 
            htm = f.read().decode('utf-8')
            ckjar.save(self.filename,ignore_discard=True, ignore_expires=True)
            f.close()
            print htm
            #"""
            followcuts =BeautifulSoup(htm).findAll('td', attrs={'valign':'top'})[1::2]#表示取出偶数位置的元素
            rega=u'<a href="http://weibo.cn/u/(\d+)">([\s\S]+?)</a>'
            patterna=re.compile(rega)
            #注意每个beautifulsoup对象截取出来的对象都是”特定的标签“对象，可以直接进行beautifulsoup相关操作
            #而不是字符串类型，如果要进行一些字符串操作，必须要转成str（） 类型。
            #Beautiful Soup用了 编码自动检测 子库来识别当前文档编码并转换成Unicode编码
            #通过Beautiful Soup输出文档时,不管输入文档是什么编码方式,输出编码均为UTF-8编码
            #但是像index 和 单纯的 find 方法会转成unicode编码方式再来操作，执行完后就要转码成utf8操作。
            #即先转码再转回来（先decode（‘utf8’）再encode（‘utf8’））
            for followitem in followcuts:
                relation=Relation()
                wuser=Wuser()
                if(patterna.search(str(followitem)) is not None):
                    relation.friendid=patterna.search(str(followitem)).group(1)
                    relation.id=follow[1:11]#只取到了10位id 或者split('/')[0]
                    wuser.id=patterna.search(str(followitem)).group(1)
                    wuser.name=patterna.search(str(followitem)).group(2)
                else:
                    regb=u'<a href="http://weibo.cn/[\s\S]+?">([\s\S]+?)</a><img alt="V"'
                    patternb=re.compile(regb)#截取用户名，因为认证用户有自己的用户名，可以不用id访问
                    regc=r'<a href="(http://weibo.cn/[\s\S]+?)">[\s\S]+?</a><img'#和可能出现多个匹配上的情况，所以加长了<img标签
                    patternc=re.compile(regc)#截取id，还是想获取用户id
                    friendurl=patternc.search(str(followitem)).group(1)
                    friendhtm=self.gethtm(friendurl)
                    regd=r"([\d]{10})"
                    patternd=re.compile(regd)
                    if(patternd.search(friendhtm).group(1)!=friendhtm):
                        rege=r'<a href="/([\d]+)/info">[\s\S]+?</a>'
                        patterne=re.compile(rege)
                        relation.friendid=patterne.search(friendhtm).group(1)
                        wuser.id=patterne.search(friendhtm).group(1)
                    else:
                        relation.friendid=patternd.search(friendhtm).group(1)
                        wuser.id=patternd.search(friendhtm).group(1)
                    relation.id=follow[1:11]
                    wuser.name=patternb.search(str(followitem)).group(1)
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
    def catchprofile(self,profile):
        #"""
        #htm=profile
        #"""
        #"""
        size=self.getpagesize(profile)
        for i in range(1,int(size)):
            time.sleep(2)#每次完成一个任务就暂停2秒
            surl="http://weibo.cn"+profile+"?page="+str(i)
            print surl
            req = urllib2.Request(surl)
            req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            #req.add_header('Accept-Encoding','gzip, deflate')
            req.add_header('Accept-Language','zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
            req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
            req.add_header('Referer','http://weibo.cn/')
            ckjar = cookielib.MozillaCookieJar()
            #这里读取cookie
            ckjar.load(self.filename, ignore_discard=True, ignore_expires=True)
            ckproc = urllib2.HTTPCookieProcessor(ckjar)
            #访问需要的微博页面
            opener = urllib2.build_opener(ckproc)
            f = opener.open(req) 
            htm = f.read().decode('utf-8')
            ckjar.save(self.filename,ignore_discard=True, ignore_expires=True)
            f.close()
            print htm
            #"""
            profilecut= BeautifulSoup(htm).findAll('div', attrs = {'class':'c'})
            for cut in profilecut:
                #一般的字符串操作有rfind 从后前前找，beautifulsoup没有
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
                    weibotransfer.wfrom=contentcut4.get_text().split(splitf.decode('utf8'))[1][:]
                    weibotransfer.id=profile[1:11]#只取到了10位id
                    weibotransfer.tranferid=contentcut1.find('a')["href"].split('/')[-1]
                    #transfername=contentcut1.find('a').contents[0].encode("utf-8")
                    remark=contentcut3.parent.get_text()
                    xy='转发理由:'
                    remark=remark.replace(xy.decode('utf8'),'')
                    if(remark.find('//')!=-1):#表示不是原文转发
                        remark=remark.split('//')[0]
                        if(remark.find('@')!=-1):#判断是否真的是@了其他人,#并且有多个@对象
                            regm=u"(@[\s\S]+ )"
                            patternm=re.compile(regm)
                            #不可以用remove 方法，包括del pop这些方法只有list有
                            #remove 是按照关键字删除，但是del 和pop 是按照索引删除
                            sxx=patternm.search(remark).groups()
                            atuserid=""
                            atusername=""
                            for item in sxx:
                                remark=remark.replace(item,'')
                                userurl=contentcut3.parent.find('a',text=sxx[:-1])["href"]
                                userhtm=self.gethtm("http://weibo.cn"+userurl)
                                atuserid=atuserid+userhtm+";"
                                atusername=atusername+item[1:]+";"#去掉前面的@符号
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
                        remark=remark.strip()
                    weibotransfer.remark=remark
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
                            weibotransfer.url+=url.group(1)+"#-#"
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
                                picdir=picdir+pichtm+";"
                            picdir=picdir[:-1]
                            picreg.picpath=picdir
                            picreg.picid=self.dbcomm.insertpic(picreg)
                        else:
                            s="原图"
                            sx=s.decode('utf-8')#千万要注意不能把两句写在一起，动态编译不会识别的
                            picurl=contentcut2.parent.next_sibling.find('a',text=sx)["href"]
                            pichtm=self.gethtm(picurl)
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
                    weibocontent.wfrom=contentcut4.get_text().split(splitf.decode('utf8'))[1][:]
                    contentcut2=cut.find('span',attrs={'class':'ctt'})
                    weibocontent.id=profile[1:11]
                    alltext=contentcut2.get_text()
                    posflag='[位置]'
                    if(alltext.find(posflag.decode('utf8'))!=-1):#如果有位置信息
                        position=alltext.split(posflag.decode('utf8'))[1]
                        alltext=alltext.split(posflag.decode('utf8'))[0]
                        weibocontent.map=position#(其实后来想想这个地方应该用经纬坐标会更好)
                    if(alltext.find('@')!=-1):#如果有艾特其他人
                        regm=u"(@[\s\S]+ )"
                        patternm=re.compile(regm)
                        #不可以用remove 方法，包括del pop这些方法只有list有
                        #remove 是按照关键字删除，但是del 和pop 是按照索引删除
                        sxx=patternm.search(alltext).groups()
                        atuserid=""
                        atusername=""
                        for item in sxx:
                            alltext=alltext.replace(item,'')
                            userurl=contentcut2.parent.find('a',text=sxx[:-1])["href"]
                            userhtm=self.gethtm("http://weibo.cn"+userurl)
                            atuserid=atuserid+userhtm+";"
                            atusername=atusername+item[1:]+";"#去掉@符号
                        atuserid=atuserid[:-1]
                        atusername=atusername[:-1]
                        wconn.atid=atuserid
                        wconn.atname=atusername
                        wconn.tag=0
                    reg=r"#([\s\S]*)#" #配对标签
                    reg1=r'<a href="([\s\S]+)">http://t.cn/[\s\S]+</a>' #配对url
                    pattern=re.compile(reg)
                    pattern1=re.compile(reg1)
                    if(pattern.search(alltext) is not None):
                        so=pattern.search(alltext)
                        label=so.group(1)
                        alltext=alltext.replace(so.group(0),"")
                        weibocontent.label=label
                    if(pattern1.search(alltext) is not None):
                        so1=pattern1.search(alltext)
                        url=self.gethtm(so1.group(1))
                        alltext=alltext.replace(so1.group(0),"")
                        weibocontent.url=url
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
                                picdir=picdir+pichtm+";"
                            picdir=picdir[:-1]
                            picreg.picpath=picdir
                            picreg.picid=self.dbcomm.insertpic(picreg)
                        else:
                            s="原图"
                            sx=s.decode('utf-8')#千万要注意不能把两句写在一起，动态编译不会识别的
                            picurl=contentcut2.parent.next_sibling.find('a',text=sx)["href"]
                            pichtm=self.gethtm(picurl)
                            picdir=pichtm
                            picreg.picpath=picdir
                            picreg.picid=self.dbcomm.insertpic(picreg)
                    self.dbcomm.insertcont(weibocontent,picreg.picid,wconn)
                #补充一点，双引号会对内容进行转义，单引号则不会
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
        flagg=1
        while(flagg):
            user=cls.classdbcomm.getuserid()
            if(user is not None):
                userid=user[0]
                obj=WeiboCatch()
                threads = []
                t1 = threading.Thread(target=obj.catchfollow,args=("/"+userid+"/follow",))
                threads.append(t1)
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
    #profile="<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\"><html xmlns=\"http://www.w3.org/1999/xhtml\"><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /><meta http-equiv=\"Cache-Control\" content=\"no-cache\"/><meta id=\"viewport\" name=\"viewport\" content=\"width=device-width,initial-scale=1.0,minimum-scale=1.0, maximum-scale=2.0\" /><link rel=\"icon\" sizes=\"any\" mask href=\"http://h5.sinaimg.cn/upload/2015/05/15/28/WeiboLogoCh.svg\"><meta name=\"theme-color\" content=\"black\"><meta name=\"MobileOptimized\" content=\"240\"/><title>我的微博</title><style type=\"text/css\" id=\"internalStyle\">html,body,p,form,div,table,textarea,input,span,select{font-size:12px;word-wrap:break-word;}body{background:#F8F9F9;color:#000;padding:1px;margin:1px;}table,tr,td{border-width:0px;margin:0px;padding:0px;}form{margin:0px;padding:0px;border:0px;}textarea{border:1px solid #96c1e6}textarea{width:95%;}a,.tl{color:#2a5492;text-decoration:underline;}/*a:link {color:#023298}*/.k{color:#2a5492;text-decoration:underline;}.kt{color:#F00;}.ib{border:1px solid #C1C1C1;}.pm,.pmy{clear:both;background:#ffffff;color:#676566;border:1px solid #b1cee7;padding:3px;margin:2px 1px;overflow:hidden;}.pms{clear:both;background:#c8d9f3;color:#666666;padding:3px;margin:0 1px;overflow:hidden;}.pmst{margin-top: 5px;}.pmsl{clear:both;padding:3px;margin:0 1px;overflow:hidden;}.pmy{background:#DADADA;border:1px solid #F8F8F8;}.t{padding:0px;margin:0px;height:35px;}.b{background:#e3efff;text-align:center;color:#2a5492;clear:both;padding:4px;}.bl{color:#2a5492;}.n{clear:both;background:#436193;color:#FFF;padding:4px; margin: 1px;}.nt{color:#b9e7ff;}.nl{color:#FFF;text-decoration:none;}.nfw{clear:both;border:1px solid #BACDEB;padding:3px;margin:2px 1px;}.s{border-bottom:1px dotted #666666;margin:3px;clear:both;}.tip{clear:both; background:#c8d9f3;color:#676566;border:1px solid #BACDEB;padding:3px;margin:2px 1px;}.tip2{color:#000000;padding:2px 3px;clear:both;}.ps{clear:both;background:#FFF;color:#676566;border:1px solid #BACDEB;padding:3px;margin:2px 1px;}.tm{background:#feffe5;border:1px solid #e6de8d;padding:4px;}.tm a{color:#ba8300;}.tmn{color:#f00}.tk{color:#ffffff}.tc{color:#63676A;}.c{padding:2px 5px;}.c div a img{border:1px solid #C1C1C1;}.ct{color:#9d9d9d;font-style:italic;}.cmt{color:#9d9d9d;}.ctt{color:#000;}.cc{color:#2a5492;}.nk{color:#2a5492;}.por {border: 1px solid #CCCCCC;height:50px;width:50px;}.me{color:#000000;background:#FEDFDF;padding:2px 5px;}.pa{padding:2px 4px;}.nm{margin:10px 5px;padding:2px;}.hm{padding:5px;background:#FFF;color:#63676A;}.u{margin:2px 1px;background:#ffffff;border:1px solid #b1cee7;}.ut{padding:2px 3px;}.cd{text-align:center;}.r{color:#F00;}.g{color:#0F0;}.bn{background: transparent;border: 0 none;text-align: left;padding-left: 0;}</style><script>if(top != self){top.location = self.location;}</script></head><body><div class=\"n\" style=\"padding: 6px 4px;\"><a href=\"http://weibo.cn/?tf=5_009\" class=\"nl\">首页</a>|<a href=\"http://weibo.cn/msg/?tf=5_010\" class=\"nl\">消息</a>|<a href=\"http://huati.weibo.cn\" class=\"nl\">话题</a>|<a href=\"http://weibo.cn/search/?tf=5_012\" class=\"nl\">搜索</a>|<a href=\"/2468833122/profile?rand=9042&amp;p=r\" class=\"nl\">刷新</a></div><div class=\"u\"><div class=\"ut\">我的微博</div><div class=\"tip2\"><span class=\"tc\">微博[25]</span>&nbsp;<a href=\"/2468833122/follow\">关注[56]</a>&nbsp;<a href=\"/2468833122/fans\">粉丝[23]</a>&nbsp;<a href=\"/at/weibo?uid=2468833122\">@我的</a></div></div><div class=\"pmst\"><span class=\"pms\">&nbsp;微博&nbsp;</span><span class=\"pmsl\">&nbsp;<a href=\"/2468833122/photo?tf=6_008\">相册</a>&nbsp;</span></div><div class=\"pms\" ><form action=\"/mblog/sendmblog?st=48683e\" accept-charset=\"UTF-8\" method=\"post\"><div><input type=\"hidden\" name=\"rl\" value=\"1\" /><textarea name=\"content\" rows=\"2\" cols=\"20\">周一请吃素</textarea><br/><input type=\"submit\" value=\"发布\" /><input type=\"submit\" name=\"friends\" value=\"好友圈\" /><input type=\"submit\" name=\"composer\" value=\"高级\" /></div></form></div><div class=\"pms\" style=\"margin-top: 2px;\">全部-<a href=\"/2468833122/profile?filter=1\">原创</a>-<a href=\"/2468833122/profile?filter=2\">图片</a>-<a href=\"/2468833122/search?f=u&amp;rl=1\">筛选</a></div><div class=\"c\" id=\"M_CuBRhgr0C\"><div><span class=\"cmt\">转发了&nbsp;<a href=\"http://weibo.cn/u/1790597487\">五行属二</a><img src=\"http://u1.sinaimg.cn/upload/2011/07/28/5338.gif\" alt=\"V\"/><img src=\"http://u1.sinaimg.cn/upload/h5/img/hyzs/donate_btn_s.png\" alt=\"M\"/>&nbsp;的微博:</span><span class=\"ctt\">盆有圈里看到的，感觉会是一次愉悦的行程[笑cry]</span></div><div><a href=\"http://weibo.cn/mblog/pic/CuBlGsDmb?rl=1\"><img src=\"http://ww4.sinaimg.cn/wap180/6aba596fjw1eut5g9brrcj20cj0m8402.jpg\" alt=\"图片\" class=\"ib\" /></a>&nbsp;<a href=\"http://weibo.cn/mblog/oripic?id=CuBlGsDmb&amp;u=6aba596fjw1eut5g9brrcj20cj0m8402\">原图</a>&nbsp;<span class=\"cmt\">赞[3838]</span>&nbsp;<span class=\"cmt\">原文转发[5250]</span>&nbsp;<a href=\"http://weibo.cn/comment/CuBlGsDmb?rl=1#cmtfrm\" class=\"cc\">原文评论[1705]</a><!----></div><div><span class=\"cmt\">转发理由:</span><a href=\"/n/%E6%B1%9F%E6%A3%AE%E5%BC%80%E6%A0%B9%E5%8F%B7\">@江森开根号</a> 试试//<a href=\"/n/%E7%9F%A5%E4%B9%8E%E5%A4%A7%E7%A5%9E\">@知乎大神</a>: 我措手不及，只得愣在那里…&nbsp;&nbsp;<a href=\"http://weibo.cn/attitude/CuBRhgr0C/add?uid=2468833122&amp;rl=1&amp;st=48683e\">赞[0]</a>&nbsp;<a href=\"http://weibo.cn/repost/CuBRhgr0C?uid=2468833122&amp;rl=1\">转发[0]</a>&nbsp;<a href=\"http://weibo.cn/comment/CuBRhgr0C?uid=2468833122&amp;rl=1#cmtfrm\" class=\"cc\">评论[0]</a>&nbsp;<a href=\"http://weibo.cn/fav/addFav/CuBRhgr0C?rl=1&amp;st=48683e\">收藏</a>&nbsp;<a href=\"http://weibo.cn/mblog/topmblog?uid=2468833122&amp;settop=1&amp;mblogid=CuBRhgr0C&amp;toptype=&amp;st=48683e\">置顶</a><!---->&nbsp;<a href=\"http://weibo.cn/mblog/del?id=CuBRhgr0C&amp;rl=1&amp;st=48683e\" class=\"cc\">删除</a>&nbsp;<span class=\"ct\">08月06日 21:26&nbsp;来自微博 weibo.com</span></div></div><div class=\"s\"></div><div class=\"c\" id=\"M_CusseiQnb\"><div><span class=\"cmt\">转发了&nbsp;<a href=\"http://weibo.cn/u/5645097376\">小S表情包</a>&nbsp;的微博:</span><span class=\"ctt\">依萍要开始表演B-box了</span>&nbsp;[<a href=\"http://weibo.cn/mblog/picAll/CurDjuWhh?rl=2\">组图共2张</a>]</div><div><a href=\"http://weibo.cn/mblog/pic/CurDjuWhh?rl=1\"><img src=\"http://ww2.sinaimg.cn/wap180/006a2fHGjw1euryigsldej30zk0k0tcd.jpg\" alt=\"图片\" class=\"ib\" /></a>&nbsp;<a href=\"http://weibo.cn/mblog/oripic?id=CurDjuWhh&amp;u=006a2fHGjw1euryigsldej30zk0k0tcd\">原图</a>&nbsp;<span class=\"cmt\">赞[20886]</span>&nbsp;<span class=\"cmt\">原文转发[49612]</span>&nbsp;<a href=\"http://weibo.cn/comment/CurDjuWhh?rl=1#cmtfrm\" class=\"cc\">原文评论[14405]</a><!----></div><div><span class=\"cmt\">转发理由:</span>哈哈哈 //<a href=\"/n/%E7%9F%A5%E4%B9%8E%E5%A4%A7%E7%A5%9E\">@知乎大神</a>:准备好了吗 //<a href=\"/n/%E7%9C%BC%E7%9D%9B%E9%95%BF%E5%9C%A8%E5%B1%81%E8%82%A1%E4%B8%8A\">@眼睛长在屁股上</a>:哈哈啊哈哈哈哈哈哈哈哈 //<a href=\"/n/%E8%B6%B4%E4%BD%93%E7%94%B7%E7%A5%9E\">@趴体男神</a>:哈哈哈哎呀我的天，就我这笑点还有救么 //<a href=\"/n/M%E5%A4%A7%E7%8E%8B%E5%8F%AB%E6%88%91%E6%9D%A5%E5%B7%A1%E5%B1%B1\">@M大王叫我来巡山</a>:DU KUJI DU KUJI DU KUJI DUDU //<a href=\"/n/%E8%BE%A3%E6%9D%A1%E5%A8%98\">@辣条娘</a>:哈哈哈哈哈好熟练的样子呢[眼泪] &nbsp;&nbsp;<a href=\"http://weibo.cn/attitude/CusseiQnb/add?uid=2468833122&amp;rl=1&amp;st=48683e\">赞[0]</a>&nbsp;<a href=\"http://weibo.cn/repost/CusseiQnb?uid=2468833122&amp;rl=1\">转发[0]</a>&nbsp;<a href=\"http://weibo.cn/comment/CusseiQnb?uid=2468833122&amp;rl=1#cmtfrm\" class=\"cc\">评论[0]</a>&nbsp;<a href=\"http://weibo.cn/fav/addFav/CusseiQnb?rl=1&amp;st=48683e\">收藏</a>&nbsp;<a href=\"http://weibo.cn/mblog/topmblog?uid=2468833122&amp;settop=1&amp;mblogid=CusseiQnb&amp;toptype=&amp;st=48683e\">置顶</a><!---->&nbsp;<a href=\"http://weibo.cn/mblog/del?id=CusseiQnb&amp;rl=1&amp;st=48683e\" class=\"cc\">删除</a>&nbsp;<span class=\"ct\">08月05日 21:29&nbsp;来自微博手机版</span></div></div><div class=\"s\"></div><div class=\"c\" id=\"M_CukkstRSi\"><div><span class=\"cmt\">转发了&nbsp;<a href=\"http://weibo.cn/u/3974469906\">辣条娘</a><img src=\"http://u1.sinaimg.cn/upload/2011/07/28/5338.gif\" alt=\"V\"/><img src=\"http://u1.sinaimg.cn/upload/h5/img/hyzs/donate_btn_s.png\" alt=\"M\"/>&nbsp;的微博:</span><span class=\"ctt\">微博上没怎么看到有人刷这个！来给大家安利一部超级少女心满满的7月最强虐狗番，秋月空太的漫改<a href=\"http://weibo.cn/pages/100808topic?extparam=%E8%B5%A4%E5%8F%91%E7%99%BD%E9%9B%AA%E5%A7%AC&amp;from=feed\">#赤发白雪姬#</a> 一集一季系列，每集都甜得像完结撒花[拜拜]这是我见过除了告白狂魔《邻座的怪同学》后，又一部闪瞎眼的催婚秀恩爱大作，女主超聪明从头到尾1v1完全不虐不玛丽苏，单身狗简直成吨伤害[怒骂]</span>&nbsp;[<a href=\"http://weibo.cn/mblog/picAll/CujhB5BxG?rl=2\">组图共9张</a>]</div><div><a href=\"http://weibo.cn/mblog/pic/CujhB5BxG?rl=1\"><img src=\"http://ww4.sinaimg.cn/wap180/ece59912jw1euqxcg4zu7j20q7218n98.jpg\" alt=\"图片\" class=\"ib\" /></a>&nbsp;<a href=\"http://weibo.cn/mblog/oripic?id=CujhB5BxG&amp;u=ece59912jw1euqxcg4zu7j20q7218n98\">原图</a>&nbsp;<span class=\"cmt\">赞[4157]</span>&nbsp;<span class=\"cmt\">原文转发[10210]</span>&nbsp;<a href=\"http://weibo.cn/comment/CujhB5BxG?rl=1#cmtfrm\" class=\"cc\">原文评论[1705]</a><!----></div><div><span class=\"cmt\">转发理由:</span> //<a href=\"/n/%E7%9F%A5%E4%B9%8E%E5%A4%A7%E7%A5%9E\">@知乎大神</a>:不错 //<a href=\"/n/%E6%97%A5%E6%9C%AC%E9%9B%B6%E8%B7%9D%E7%A6%BB\">@日本零距离</a>:马克一下&nbsp;&nbsp;<a href=\"http://weibo.cn/attitude/CukkstRSi/add?uid=2468833122&amp;rl=1&amp;st=48683e\">赞[0]</a>&nbsp;<a href=\"http://weibo.cn/repost/CukkstRSi?uid=2468833122&amp;rl=1\">转发[0]</a>&nbsp;<a href=\"http://weibo.cn/comment/CukkstRSi?uid=2468833122&amp;rl=1#cmtfrm\" class=\"cc\">评论[0]</a>&nbsp;<a href=\"http://weibo.cn/fav/addFav/CukkstRSi?rl=1&amp;st=48683e\">收藏</a>&nbsp;<a href=\"http://weibo.cn/mblog/topmblog?uid=2468833122&amp;settop=1&amp;mblogid=CukkstRSi&amp;toptype=&amp;st=48683e\">置顶</a><!---->&nbsp;<a href=\"http://weibo.cn/mblog/del?id=CukkstRSi&amp;rl=1&amp;st=48683e\" class=\"cc\">删除</a>&nbsp;<span class=\"ct\">08月05日 00:48&nbsp;来自iPhone 6 Plus</span></div></div><div class=\"s\"></div><div class=\"c\" id=\"M_CtnoGdKqr\"><div><span class=\"cmt\">转发了&nbsp;<a href=\"http://weibo.cn/u/2891529877\">我的朋友是个呆B</a><img src=\"http://u1.sinaimg.cn/upload/2011/07/28/5338.gif\" alt=\"V\"/><img src=\"http://u1.sinaimg.cn/upload/h5/img/hyzs/donate_btn_s.png\" alt=\"M\"/>&nbsp;的微博:</span><span class=\"ctt\">好久没抽奖了，给大家送个福利！搞到了四台<a href=\"http://weibo.cn/pages/100808topic?extparam=%E9%AD%85%E8%93%9D%E6%89%8B%E6%9C%BA2&amp;from=feed\">#魅蓝手机2#</a>手机，没错，四台！从转发这条的粉丝里抽，8月3日在抽奖平台开奖。感谢大家的陪伴，爱你萌！ </span></div><div><a href=\"http://weibo.cn/mblog/pic/CtmgPbvq4?rl=1\"><img src=\"http://ww4.sinaimg.cn/wap180/0068KSUIjw1eujl85fyckj30jg0ukq77.jpg\" alt=\"图片\" class=\"ib\" /></a>&nbsp;<a href=\"http://weibo.cn/mblog/oripic?id=CtmgPbvq4&amp;u=0068KSUIjw1eujl85fyckj30jg0ukq77\">原图</a>&nbsp;<span class=\"cmt\">赞[3310]</span>&nbsp;<span class=\"cmt\">原文转发[32305]</span>&nbsp;<a href=\"http://weibo.cn/comment/CtmgPbvq4?rl=1#cmtfrm\" class=\"cc\">原文评论[6860]</a><!----></div><div><span class=\"cmt\">转发理由:</span>[哈哈][哈哈][哈哈]&nbsp;&nbsp;<a href=\"http://weibo.cn/attitude/CtnoGdKqr/add?uid=2468833122&amp;rl=1&amp;st=48683e\">赞[0]</a>&nbsp;<a href=\"http://weibo.cn/repost/CtnoGdKqr?uid=2468833122&amp;rl=1\">转发[0]</a>&nbsp;<a href=\"http://weibo.cn/comment/CtnoGdKqr?uid=2468833122&amp;rl=1#cmtfrm\" class=\"cc\">评论[0]</a>&nbsp;<a href=\"http://weibo.cn/fav/addFav/CtnoGdKqr?rl=1&amp;st=48683e\">收藏</a>&nbsp;<a href=\"http://weibo.cn/mblog/topmblog?uid=2468833122&amp;settop=1&amp;mblogid=CtnoGdKqr&amp;toptype=&amp;st=48683e\">置顶</a><!---->&nbsp;<a href=\"http://weibo.cn/mblog/del?id=CtnoGdKqr&amp;rl=1&amp;st=48683e\" class=\"cc\">删除</a>&nbsp;<span class=\"ct\">07月29日 18:47&nbsp;来自iPhone 6 Plus</span></div></div><div class=\"s\"></div><div class=\"c\" id=\"M_CrKIjBmK8\"><div><span class=\"ctt\">第一次发长微博。写的是对国内互联网数据的感慨 [位置]<a href=\"http://weibo.cn/sinaurl?f=w&amp;u=http%3A%2F%2Ft.cn%2FRLI4joD&amp;ep=CrKIjBmK8%2C2468833122%2CCrKIjBmK8%2C2468833122\">深圳市</a></span>&nbsp;<a href=\"http://place.weibo.com/imgmap/center=22.586781,113.967438&amp;backurl=http%253A%252F%252Fweibo.cn%252F2468833122%252Fprofile%253Frand%253D9042\">显示地图</a></div><div><a href=\"http://weibo.cn/mblog/pic/CrKIjBmK8?rl=1\"><img src=\"http://ww4.sinaimg.cn/wap180/93276762jw1eu7hnbukjzj20hs6x6u0x.jpg\" alt=\"图片\" class=\"ib\" /></a>&nbsp;<a href=\"http://weibo.cn/mblog/oripic?id=CrKIjBmK8&amp;u=93276762jw1eu7hnbukjzj20hs6x6u0x\">原图</a>&nbsp;<a href=\"http://weibo.cn/attitude/CrKIjBmK8/add?uid=2468833122&amp;rl=1&amp;st=48683e\">赞[1]</a>&nbsp;<a href=\"http://weibo.cn/repost/CrKIjBmK8?uid=2468833122&amp;rl=1\">转发[0]</a>&nbsp;<a href=\"http://weibo.cn/comment/CrKIjBmK8?uid=2468833122&amp;rl=1#cmtfrm\" class=\"cc\">评论[0]</a>&nbsp;<a href=\"http://weibo.cn/fav/addFav/CrKIjBmK8?rl=1&amp;st=48683e\">收藏</a>&nbsp;<a href=\"http://weibo.cn/mblog/topmblog?uid=2468833122&amp;settop=1&amp;mblogid=CrKIjBmK8&amp;toptype=&amp;st=48683e\">置顶</a><!---->&nbsp;<a href=\"http://weibo.cn/mblog/del?id=CrKIjBmK8&amp;rl=1&amp;st=48683e\" class=\"cc\">删除</a>&nbsp;<span class=\"ct\">07月19日 02:28&nbsp;来自iPhone 6 Plus</span></div></div><div class=\"s\"></div><div class=\"c\" id=\"M_CrKBnnpln\"><div><span class=\"ctt\">查看文章<a href=\"http://weibo.cn/sinaurl?f=w&amp;u=http%3A%2F%2Ft.cn%2FRLI4fYJ&amp;ep=CrKBnnpln%2C2468833122%2CCrKBnnpln%2C2468833122\">《手机“社交”功能的app，你们是不是知道的太多了。》</a>  [位置]<a href=\"http://weibo.cn/sinaurl?f=w&amp;u=http%3A%2F%2Ft.cn%2FRLI4fYa&amp;ep=CrKBnnpln%2C2468833122%2CCrKBnnpln%2C2468833122\">深圳市</a></span>&nbsp;<a href=\"http://place.weibo.com/imgmap/center=22.587009,113.967461&amp;backurl=http%253A%252F%252Fweibo.cn%252F2468833122%252Fprofile%253Frand%253D9042\">显示地图</a>&nbsp;<a href=\"http://weibo.cn/attitude/CrKBnnpln/add?uid=2468833122&amp;rl=1&amp;st=48683e\">赞[0]</a>&nbsp;<a href=\"http://weibo.cn/repost/CrKBnnpln?uid=2468833122&amp;rl=1\">转发[0]</a>&nbsp;<a href=\"http://weibo.cn/comment/CrKBnnpln?uid=2468833122&amp;rl=1#cmtfrm\" class=\"cc\">评论[0]</a>&nbsp;<a href=\"http://weibo.cn/fav/addFav/CrKBnnpln?rl=1&amp;st=48683e\">收藏</a>&nbsp;<a href=\"http://weibo.cn/mblog/topmblog?uid=2468833122&amp;settop=1&amp;mblogid=CrKBnnpln&amp;toptype=&amp;st=48683e\">置顶</a><!---->&nbsp;<a href=\"http://weibo.cn/mblog/del?id=CrKBnnpln&amp;rl=1&amp;st=48683e\" class=\"cc\">删除</a>&nbsp;<span class=\"ct\">07月19日 02:11&nbsp;来自iPhone 6 Plus</span></div></div><div class=\"s\"></div><div class=\"c\" id=\"M_CqdVduZEj\"><div><span class=\"cmt\">转发了&nbsp;<a href=\"http://weibo.cn/xiaomigamer\">小米游戏</a><img src=\"http://u1.sinaimg.cn/upload/2011/07/28/5337.gif\" alt=\"V\"/><img src=\"http://u1.sinaimg.cn/upload/h5/img/hyzs/donate_btn_s.png\" alt=\"M\"/>&nbsp;的微博:</span><span class=\"ctt\">ZAN叹不已，3D超清电影画质，细致毛发逼真还原，<a href=\"http://weibo.cn/pages/100808topic?extparam=%E8%A5%BF%E6%B8%B8%E9%99%8D%E9%AD%94%E7%AF%873D&amp;from=feed\">#西游降魔篇3D#</a>还有2天正式发布！关注转发送2台小米平板！<a href=\"http://weibo.cn/pages/100808topic?extparam=%E4%B8%BA%E6%98%9F%E7%88%B7%E7%82%B9%E8%B5%9E&amp;from=feed\">#为星爷点赞#</a></span></div><div><a href=\"http://weibo.cn/mblog/pic/CpYAcpewb?rl=1\"><img src=\"http://ww2.sinaimg.cn/wap180/005FVCB5jw1ettzfn93wqj30k00zkgto.jpg\" alt=\"图片\" class=\"ib\" /></a>&nbsp;<a href=\"http://weibo.cn/mblog/oripic?id=CpYAcpewb&amp;u=005FVCB5jw1ettzfn93wqj30k00zkgto\">原图</a>&nbsp;<span class=\"cmt\">赞[733]</span>&nbsp;<span class=\"cmt\">原文转发[24203]</span>&nbsp;<a href=\"http://weibo.cn/comment/CpYAcpewb?rl=1#cmtfrm\" class=\"cc\">原文评论[4029]</a><!----></div><div><span class=\"cmt\">转发理由:</span>[抓狂][抓狂][抓狂]&nbsp;&nbsp;<a href=\"http://weibo.cn/attitude/CqdVduZEj/add?uid=2468833122&amp;rl=1&amp;st=48683e\">赞[0]</a>&nbsp;<a href=\"http://weibo.cn/repost/CqdVduZEj?uid=2468833122&amp;rl=1\">转发[0]</a>&nbsp;<a href=\"http://weibo.cn/comment/CqdVduZEj?uid=2468833122&amp;rl=1#cmtfrm\" class=\"cc\">评论[0]</a>&nbsp;<a href=\"http://weibo.cn/fav/addFav/CqdVduZEj?rl=1&amp;st=48683e\">收藏</a>&nbsp;<a href=\"http://weibo.cn/mblog/topmblog?uid=2468833122&amp;settop=1&amp;mblogid=CqdVduZEj&amp;toptype=&amp;st=48683e\">置顶</a><!---->&nbsp;<a href=\"http://weibo.cn/mblog/del?id=CqdVduZEj&amp;rl=1&amp;st=48683e\" class=\"cc\">删除</a>&nbsp;<span class=\"ct\">07月09日 01:08&nbsp;来自iPhone 6 Plus</span></div></div><div class=\"s\"></div><div class=\"c\" id=\"M_CqdLIhcp9\"><div><span class=\"cmt\">转发了&nbsp;<a href=\"http://weibo.cn/nlpjob\">NLPJob</a>&nbsp;的微博:</span><span class=\"ctt\">本周 <a href=\"/n/NLPJob\">@NLPJob</a> 联合 <a href=\"/n/%E5%9B%BE%E7%81%B5%E6%95%99%E8%82%B2\">@图灵教育</a> 送出5本《Python数据分析基础教程：NumPy学习指南（第2版）》。简单易学的NumPy中文入门教程，Python数据分析首选, 从最基础的知识讲起，手把手带你进入数据挖掘领域；囊括大量具有启发性与实用价值的实战案例。试读：<a href=\"http://weibo.cn/sinaurl?f=w&amp;u=http%3A%2F%2Ft.cn%2FRL2RdYI&amp;ep=CqdLIhcp9%2C2468833122%2CCq2FP3s6d%2C3224962394\">http://t.cn/RL2RdYI</a> 关注并转发，7月12日晚9点抽奖</span></div><div><a href=\"http://weibo.cn/mblog/pic/Cq2FP3s6d?rl=1\"><img src=\"http://ww4.sinaimg.cn/wap180/c039055agw1etuhffi23uj20ow0sa0xe.jpg\" alt=\"图片\" class=\"ib\" /></a>&nbsp;<a href=\"http://weibo.cn/mblog/oripic?id=Cq2FP3s6d&amp;u=c039055agw1etuhffi23uj20ow0sa0xe\">原图</a>&nbsp;<span class=\"cmt\">赞[12]</span>&nbsp;<span class=\"cmt\">原文转发[875]</span>&nbsp;<a href=\"http://weibo.cn/comment/Cq2FP3s6d?rl=1#cmtfrm\" class=\"cc\">原文评论[152]</a><!----></div><div><span class=\"cmt\">转发理由:</span>[抓狂][抓狂][抓狂]&nbsp;&nbsp;<a href=\"http://weibo.cn/attitude/CqdLIhcp9/add?uid=2468833122&amp;rl=1&amp;st=48683e\">赞[0]</a>&nbsp;<a href=\"http://weibo.cn/repost/CqdLIhcp9?uid=2468833122&amp;rl=1\">转发[0]</a>&nbsp;<a href=\"http://weibo.cn/comment/CqdLIhcp9?uid=2468833122&amp;rl=1#cmtfrm\" class=\"cc\">评论[0]</a>&nbsp;<a href=\"http://weibo.cn/fav/addFav/CqdLIhcp9?rl=1&amp;st=48683e\">收藏</a>&nbsp;<a href=\"http://weibo.cn/mblog/topmblog?uid=2468833122&amp;settop=1&amp;mblogid=CqdLIhcp9&amp;toptype=&amp;st=48683e\">置顶</a><!---->&nbsp;<a href=\"http://weibo.cn/mblog/del?id=CqdLIhcp9&amp;rl=1&amp;st=48683e\" class=\"cc\">删除</a>&nbsp;<span class=\"ct\">07月09日 00:45&nbsp;来自iPhone 6 Plus</span></div></div><div class=\"s\"></div><div class=\"c\" id=\"M_CpyyclDRD\"><div><span class=\"cmt\">转发了&nbsp;<a href=\"http://weibo.cn/16fanriben\">十六番-日本</a><img src=\"http://u1.sinaimg.cn/upload/h5/img/hyzs/donate_btn_s.png\" alt=\"M\"/>&nbsp;的微博:</span><span class=\"ctt\"><a href=\"http://weibo.cn/pages/100808topic?extparam=%E5%8D%81%E5%85%AD%E7%95%AA%E6%B8%B8%E8%AE%B0&amp;from=feed\">#十六番游记#</a>【Kakitsu的东京-京都-奈良-大阪-东京13日之旅】写这篇游记另一个目的是在日本的期间，遇到了好多的国人，因为本人会日语，所以能提供帮助的时候，能帮忙翻译一下的时候都会去帮忙。希望在这里，我的行程，我的经历，可以帮到想要去日本自由行的朋友。游记地址：<a href=\"http://weibo.cn/sinaurl?f=w&amp;u=http%3A%2F%2Ft.cn%2FRLhTUpi&amp;ep=CpyyclDRD%2C2468833122%2CCpylMxcHn%2C1640452611\">http://t.cn/RLhTUpi</a></span>&nbsp;[<a href=\"http://weibo.cn/mblog/picAll/CpylMxcHn?rl=2\">组图共9张</a>]</div><div><a href=\"http://weibo.cn/mblog/pic/CpylMxcHn?rl=1\"><img src=\"http://ww3.sinaimg.cn/wap180/61c75203gw1etql35nlrpj20c80a0mxm.jpg\" alt=\"图片\" class=\"ib\" /></a>&nbsp;<a href=\"http://weibo.cn/mblog/oripic?id=CpylMxcHn&amp;u=61c75203gw1etql35nlrpj20c80a0mxm\">原图</a>&nbsp;<span class=\"cmt\">赞[77]</span>&nbsp;<span class=\"cmt\">原文转发[61]</span>&nbsp;<a href=\"http://weibo.cn/comment/CpylMxcHn?rl=1#cmtfrm\" class=\"cc\">原文评论[14]</a><!----></div><div><span class=\"cmt\">转发理由:</span>转发微博&nbsp;&nbsp;<a href=\"http://weibo.cn/attitude/CpyyclDRD/add?uid=2468833122&amp;rl=1&amp;st=48683e\">赞[0]</a>&nbsp;<a href=\"http://weibo.cn/repost/CpyyclDRD?uid=2468833122&amp;rl=1\">转发[0]</a>&nbsp;<a href=\"http://weibo.cn/comment/CpyyclDRD?uid=2468833122&amp;rl=1#cmtfrm\" class=\"cc\">评论[0]</a>&nbsp;<a href=\"http://weibo.cn/fav/addFav/CpyyclDRD?rl=1&amp;st=48683e\">收藏</a>&nbsp;<a href=\"http://weibo.cn/mblog/topmblog?uid=2468833122&amp;settop=1&amp;mblogid=CpyyclDRD&amp;toptype=&amp;st=48683e\">置顶</a><!---->&nbsp;<a href=\"http://weibo.cn/mblog/del?id=CpyyclDRD&amp;rl=1&amp;st=48683e\" class=\"cc\">删除</a>&nbsp;<span class=\"ct\">07月04日 15:49&nbsp;来自微博 weibo.com</span></div></div><div class=\"s\"></div><div class=\"c\" id=\"M_Cpyy8cheg\"><div><span class=\"cmt\">转发了&nbsp;<a href=\"http://weibo.cn/u/1805982651\">知乎大神</a><img src=\"http://u1.sinaimg.cn/upload/h5/img/hyzs/donate_btn_s.png\" alt=\"M\"/>&nbsp;的微博:</span><span class=\"ctt\">「生活中最让你怦然心动的是什么？」正是因为有这些心动的时刻，才更让我们体会到生活的美好吧。<a href=\"http://weibo.cn/pages/100808topic?extparam=%E5%A4%A7%E7%A5%9E%E6%8E%A8%E8%8D%90&amp;from=feed\">#大神推荐#</a></span>&nbsp;[<a href=\"http://weibo.cn/mblog/picAll/CpxQWaRRR?rl=2\">组图共9张</a>]</div><div><a href=\"http://weibo.cn/mblog/pic/CpxQWaRRR?rl=1\"><img src=\"http://ww3.sinaimg.cn/wap180/6ba51bbbjw1etqpfmstl7j20hs15ln20.jpg\" alt=\"图片\" class=\"ib\" /></a>&nbsp;<a href=\"http://weibo.cn/mblog/oripic?id=CpxQWaRRR&amp;u=6ba51bbbjw1etqpfmstl7j20hs15ln20\">原图</a>&nbsp;<span class=\"cmt\">赞[7019]</span>&nbsp;<span class=\"cmt\">原文转发[5389]</span>&nbsp;<a href=\"http://weibo.cn/comment/CpxQWaRRR?rl=1#cmtfrm\" class=\"cc\">原文评论[2206]</a><!----></div><div><span class=\"cmt\">转发理由:</span>转发微博&nbsp;&nbsp;<a href=\"http://weibo.cn/attitude/Cpyy8cheg/add?uid=2468833122&amp;rl=1&amp;st=48683e\">赞[0]</a>&nbsp;<a href=\"http://weibo.cn/repost/Cpyy8cheg?uid=2468833122&amp;rl=1\">转发[0]</a>&nbsp;<a href=\"http://weibo.cn/comment/Cpyy8cheg?uid=2468833122&amp;rl=1#cmtfrm\" class=\"cc\">评论[0]</a>&nbsp;<a href=\"http://weibo.cn/fav/addFav/Cpyy8cheg?rl=1&amp;st=48683e\">收藏</a>&nbsp;<a href=\"http://weibo.cn/mblog/topmblog?uid=2468833122&amp;settop=1&amp;mblogid=Cpyy8cheg&amp;toptype=&amp;st=48683e\">置顶</a><!---->&nbsp;<a href=\"http://weibo.cn/mblog/del?id=Cpyy8cheg&amp;rl=1&amp;st=48683e\" class=\"cc\">删除</a>&nbsp;<span class=\"ct\">07月04日 15:49&nbsp;来自微博 weibo.com</span></div></div><div class=\"s\"></div><div class=\"pa\" id=\"pagelist\"><form action=\"/2468833122/profile\" method=\"post\"><div><a href=\"/2468833122/profile?page=2\">下页</a>&nbsp;<input name=\"mp\" type=\"hidden\" value=\"3\" /><input type=\"text\" name=\"page\" size=\"2\" style='-wap-input-format: \"*N\"' /><input type=\"submit\" value=\"跳页\" />&nbsp;1/3页</div></form></div><div class=\"pm\"><form action=\"/search/\" method=\"post\"><div><input type=\"text\" name=\"keyword\" value=\"\" size=\"15\" /><input type=\"submit\" name=\"smblog\" value=\"搜微博\" /><input type=\"submit\" name=\"suser\" value=\"找人\" /><br/><span class=\"pmf\"><a href=\"/search/mblog/?keyword=%E6%8C%91%E6%88%98%E8%80%85%E8%81%94%E7%9B%9F&amp;rl=1\" class=\"k\">挑战者联盟</a>&nbsp;<a href=\"/search/mblog/?keyword=2015%E6%B8%B8%E6%B3%B3%E4%B8%96%E9%94%A6%E8%B5%9B&amp;rl=1\" class=\"k\">2015游泳世锦赛</a>&nbsp;<a href=\"/search/mblog/?keyword=%E5%81%B6%E6%BB%B4%E6%AD%8C%E7%A5%9E%E5%95%8A&amp;rl=1\" class=\"k\">偶滴歌神啊</a>&nbsp;<a href=\"/search/mblog/?keyword=%E5%8D%8E%E6%99%A8%E5%AE%87&amp;rl=1\" class=\"k\">华晨宇</a>&nbsp;<a href=\"/search/mblog/?keyword=%E6%8B%9B%E7%89%8C%E5%8A%A8%E4%BD%9C&amp;rl=1\" class=\"k\">招牌动作</a></span></div></form></div><div class=\"cd\"><a href=\"#top\"><img src=\"http://u1.sinaimg.cn/3g/image/upload/0/62/203/18979/5e990ec2.gif\" alt=\"TOP\"/></a></div><div class=\"pms\"> <a href=\"http://weibo.cn\">首页</a>.<a href=\"http://weibo.cn/topic/240489\">反馈</a>.<a href=\"http://weibo.cn/page/91\">帮助</a>.<a  href=\"http://down.sina.cn/weibo/default/index/soft_id/1/mid/0\"  >客户端</a>.<a href=\"http://weibo.cn/spam/?rl=1&amp;type=3&amp;fuid=2468833122\" class=\"kt\">举报</a>.<a href=\"http://passport.sina.cn/sso/logout?r=http%3A%2F%2Fweibo.cn%2Fpub%2F%3Fvt%3D&amp;entry=mweibo\">退出</a></div><div class=\"c\">设置:<a href=\"http://weibo.cn/account/customize/skin?tf=7_005&amp;st=48683e\">皮肤</a>.<a href=\"http://weibo.cn/account/customize/pic?tf=7_006&amp;st=48683e\">图片</a>.<a href=\"http://weibo.cn/account/customize/pagesize?tf=7_007&amp;st=48683e\">条数</a>.<a href=\"http://weibo.cn/account/privacy/?tf=7_008&amp;st=48683e\">隐私</a></div><div class=\"c\">彩版|<a href=\"http://m.weibo.cn/?tf=7_010\">触屏</a>|<a href=\"http://weibo.cn/page/521?tf=7_011\">语音</a></div><div class=\"b\">weibo.cn[08-07 09:47]</div></body></html>"
    #follow="<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\"><html xmlns=\"http://www.w3.org/1999/xhtml\"><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /><meta http-equiv=\"Cache-Control\" content=\"no-cache\"/><meta id=\"viewport\" name=\"viewport\" content=\"width=device-width,initial-scale=1.0,minimum-scale=1.0, maximum-scale=2.0\" /><link rel=\"icon\" sizes=\"any\" mask href=\"http://h5.sinaimg.cn/upload/2015/05/15/28/WeiboLogoCh.svg\"><meta name=\"theme-color\" content=\"black\"><meta name=\"MobileOptimized\" content=\"240\"/><title>我关注的人</title><style type=\"text/css\" id=\"internalStyle\">html,body,p,form,div,table,textarea,input,span,select{font-size:12px;word-wrap:break-word;}body{background:#F8F9F9;color:#000;padding:1px;margin:1px;}table,tr,td{border-width:0px;margin:0px;padding:0px;}form{margin:0px;padding:0px;border:0px;}textarea{border:1px solid #96c1e6}textarea{width:95%;}a,.tl{color:#2a5492;text-decoration:underline;}/*a:link {color:#023298}*/.k{color:#2a5492;text-decoration:underline;}.kt{color:#F00;}.ib{border:1px solid #C1C1C1;}.pm,.pmy{clear:both;background:#ffffff;color:#676566;border:1px solid #b1cee7;padding:3px;margin:2px 1px;overflow:hidden;}.pms{clear:both;background:#c8d9f3;color:#666666;padding:3px;margin:0 1px;overflow:hidden;}.pmst{margin-top: 5px;}.pmsl{clear:both;padding:3px;margin:0 1px;overflow:hidden;}.pmy{background:#DADADA;border:1px solid #F8F8F8;}.t{padding:0px;margin:0px;height:35px;}.b{background:#e3efff;text-align:center;color:#2a5492;clear:both;padding:4px;}.bl{color:#2a5492;}.n{clear:both;background:#436193;color:#FFF;padding:4px; margin: 1px;}.nt{color:#b9e7ff;}.nl{color:#FFF;text-decoration:none;}.nfw{clear:both;border:1px solid #BACDEB;padding:3px;margin:2px 1px;}.s{border-bottom:1px dotted #666666;margin:3px;clear:both;}.tip{clear:both; background:#c8d9f3;color:#676566;border:1px solid #BACDEB;padding:3px;margin:2px 1px;}.tip2{color:#000000;padding:2px 3px;clear:both;}.ps{clear:both;background:#FFF;color:#676566;border:1px solid #BACDEB;padding:3px;margin:2px 1px;}.tm{background:#feffe5;border:1px solid #e6de8d;padding:4px;}.tm a{color:#ba8300;}.tmn{color:#f00}.tk{color:#ffffff}.tc{color:#63676A;}.c{padding:2px 5px;}.c div a img{border:1px solid #C1C1C1;}.ct{color:#9d9d9d;font-style:italic;}.cmt{color:#9d9d9d;}.ctt{color:#000;}.cc{color:#2a5492;}.nk{color:#2a5492;}.por {border: 1px solid #CCCCCC;height:50px;width:50px;}.me{color:#000000;background:#FEDFDF;padding:2px 5px;}.pa{padding:2px 4px;}.nm{margin:10px 5px;padding:2px;}.hm{padding:5px;background:#FFF;color:#63676A;}.u{margin:2px 1px;background:#ffffff;border:1px solid #b1cee7;}.ut{padding:2px 3px;}.cd{text-align:center;}.r{color:#F00;}.g{color:#0F0;}.bn{background: transparent;border: 0 none;text-align: left;padding-left: 0;}</style><script>if(top != self){top.location = self.location;}</script></head><body><div class=\"n\" style=\"padding: 6px 4px;\"><a href=\"http://weibo.cn/?tf=5_009\" class=\"nl\">首页<span class=\"tk\">!</span></a>|<a href=\"http://weibo.cn/msg/?tf=5_010\" class=\"nl\">消息</a>|<a href=\"http://huati.weibo.cn\" class=\"nl\">话题</a>|<a href=\"http://weibo.cn/search/?tf=5_012\" class=\"nl\">搜索</a>|<a href=\"/2468833122/follow?rand=8149&amp;p=r\" class=\"nl\">刷新</a></div><div class=\"u\"><div class=\"ut\">我关注的人</div><div class=\"tip2\"><a href=\"/2468833122/profile\">微博[31]</a>&nbsp;<span class=\"tc\">关注[58]</span>&nbsp;<a href=\"/2468833122/fans\">粉丝[23]</a>&nbsp;<a href=\"/at/weibo?uid=2468833122\">@我的</a></div></div><div class=\"c\">关注时间/<a href=\"/2468833122/follow?sort=3\">更新时间</a>/<a href=\"/attgroup/index?f=atts\">分组</a>/<a href=\"/2468833122/follow?cat=more\">更多</a><form action=\"/2468833122/searchuser\" method=\"post\"><div><input type=\"text\" name=\"keyword\" value=\"\" size=\"15\" /><input type=\"hidden\" name=\"type\" value=\"0\"/><input type=\"hidden\" name=\"range\" value=\"2\"/><input type=\"submit\" value=\"查找\" /></div></form></div> <table><tr><td valign=\"top\" style=\"width: 52px\"><a href=\"http://weibo.cn/u/2793823365\"><img src=\"http://tp2.sinaimg.cn/2793823365/50/5727772578/1\" alt=\"pic\" /></a></td><td valign=\"top\"><a href=\"http://weibo.cn/u/2793823365\">表情社</a>&nbsp;(<a href=\"http://weibo.cn/attention/remark?uid=2793823365&amp;rl=1\">备注</a>)<br/>粉丝286799人<br/><a href=\"http://weibo.cn/attention/del?uid=2793823365&amp;rl=1&amp;st=a69bac\">取消关注</a>&nbsp;<a href=\"http://weibo.cn/attgroup/relisted?uid=2793823365&amp;rl=1&amp;from=att\">分组</a>&nbsp;<a href=\"http://weibo.cn/im/chat?uid=2793823365&amp;rl=1\">私信</a></td></tr></table> <div class=\"s\"></div><table><tr><td valign=\"top\" style=\"width: 52px\"><a href=\"http://weibo.cn/miappstore\"><img src=\"http://tp2.sinaimg.cn/2758590881/50/22872575819/1\" alt=\"pic\" /></a></td><td valign=\"top\"><a href=\"http://weibo.cn/miappstore\">小米应用商店</a><img src=\"http://u1.sinaimg.cn/upload/2011/07/28/5337.gif\" alt=\"V\"/>&nbsp;(<a href=\"http://weibo.cn/attention/remark?uid=2758590881&amp;rl=1\">备注</a>)<br/>粉丝873378人<br/><a href=\"http://weibo.cn/attention/del?uid=2758590881&amp;rl=1&amp;st=a69bac\">取消关注</a>&nbsp;<a href=\"http://weibo.cn/attgroup/relisted?uid=2758590881&amp;rl=1&amp;from=att\">分组</a>&nbsp;<a href=\"http://weibo.cn/im/chat?uid=2758590881&amp;rl=1\">私信</a></td></tr></table> <div class=\"s\"></div><table><tr><td valign=\"top\" style=\"width: 52px\"><a href=\"http://weibo.cn/u/2891529877\"><img src=\"http://tp2.sinaimg.cn/2891529877/50/5714970948/1\" alt=\"pic\" /></a></td><td valign=\"top\"><a href=\"http://weibo.cn/u/2891529877\">我的朋友是个呆B</a><img src=\"http://u1.sinaimg.cn/upload/2011/07/28/5338.gif\" alt=\"V\"/>&nbsp;(<a href=\"http://weibo.cn/attention/remark?uid=2891529877&amp;rl=1\">备注</a>)<br/>粉丝9595566人<br/><a href=\"http://weibo.cn/attention/del?uid=2891529877&amp;rl=1&amp;st=a69bac\">取消关注</a>&nbsp;<a href=\"http://weibo.cn/attgroup/relisted?uid=2891529877&amp;rl=1&amp;from=att\">分组</a>&nbsp;<a href=\"http://weibo.cn/im/chat?uid=2891529877&amp;rl=1\">私信</a></td></tr></table> <div class=\"s\"></div><table><tr><td valign=\"top\" style=\"width: 52px\"><a href=\"http://weibo.cn/u/1613265794\"><img src=\"http://tp3.sinaimg.cn/1613265794/50/5732458201/1\" alt=\"pic\" /></a></td><td valign=\"top\"><a href=\"http://weibo.cn/u/1613265794\">卡里F</a>&nbsp;(<a href=\"http://weibo.cn/attention/remark?uid=1613265794&amp;rl=1\">备注</a>)<br/>粉丝371093人<br/><a href=\"http://weibo.cn/attention/del?uid=1613265794&amp;rl=1&amp;st=a69bac\">取消关注</a>&nbsp;<a href=\"http://weibo.cn/attgroup/relisted?uid=1613265794&amp;rl=1&amp;from=att\">分组</a>&nbsp;<a href=\"http://weibo.cn/im/chat?uid=1613265794&amp;rl=1\">私信</a></td></tr></table> <div class=\"s\"></div><table><tr><td valign=\"top\" style=\"width: 52px\"><a href=\"http://weibo.cn/timcook\"><img src=\"http://tp1.sinaimg.cn/5524254784/50/5726290226/1\" alt=\"pic\" /></a></td><td valign=\"top\"><a href=\"http://weibo.cn/timcook\">TimCook</a><img src=\"http://u1.sinaimg.cn/upload/2011/07/28/5338.gif\" alt=\"V\"/>&nbsp;(<a href=\"http://weibo.cn/attention/remark?uid=5524254784&amp;rl=1\">备注</a>)<br/>粉丝688423人<br/><a href=\"http://weibo.cn/attention/del?uid=5524254784&amp;rl=1&amp;st=a69bac\">取消关注</a>&nbsp;<a href=\"http://weibo.cn/attgroup/relisted?uid=5524254784&amp;rl=1&amp;from=att\">分组</a>&nbsp;<a href=\"http://weibo.cn/im/chat?uid=5524254784&amp;rl=1\">私信</a></td></tr></table> <div class=\"s\"></div><table><tr><td valign=\"top\" style=\"width: 52px\"><a href=\"http://weibo.cn/xiaomigamer\"><img src=\"http://tp4.sinaimg.cn/5200227003/50/5729080850/1\" alt=\"pic\" /></a></td><td valign=\"top\"><a href=\"http://weibo.cn/xiaomigamer\">小米游戏</a><img src=\"http://u1.sinaimg.cn/upload/2011/07/28/5337.gif\" alt=\"V\"/>&nbsp;(<a href=\"http://weibo.cn/attention/remark?uid=5200227003&amp;rl=1\">备注</a>)<br/>粉丝247728人<br/><a href=\"http://weibo.cn/attention/del?uid=5200227003&amp;rl=1&amp;st=a69bac\">取消关注</a>&nbsp;<a href=\"http://weibo.cn/attgroup/relisted?uid=5200227003&amp;rl=1&amp;from=att\">分组</a>&nbsp;<a href=\"http://weibo.cn/im/chat?uid=5200227003&amp;rl=1\">私信</a></td></tr></table> <div class=\"s\"></div><table><tr><td valign=\"top\" style=\"width: 52px\"><a href=\"http://weibo.cn/DataScientistUnion\"><img src=\"http://tp4.sinaimg.cn/3847741679/50/5710230990/1\" alt=\"pic\" /></a></td><td valign=\"top\"><a href=\"http://weibo.cn/DataScientistUnion\">数盟社区</a><img src=\"http://u1.sinaimg.cn/upload/2011/07/28/5337.gif\" alt=\"V\"/>&nbsp;(<a href=\"http://weibo.cn/attention/remark?uid=3847741679&amp;rl=1\">备注</a>)<br/>粉丝9246人<br/><a href=\"http://weibo.cn/attention/del?uid=3847741679&amp;rl=1&amp;st=a69bac\">取消关注</a>&nbsp;<a href=\"http://weibo.cn/attgroup/relisted?uid=3847741679&amp;rl=1&amp;from=att\">分组</a>&nbsp;<a href=\"http://weibo.cn/im/chat?uid=3847741679&amp;rl=1\">私信</a></td></tr></table> <div class=\"s\"></div><table><tr><td valign=\"top\" style=\"width: 52px\"><a href=\"http://weibo.cn/mrjimsly\"><img src=\"http://tp2.sinaimg.cn/1950692025/50/5729970286/1\" alt=\"pic\" /></a></td><td valign=\"top\"><a href=\"http://weibo.cn/mrjimsly\">我弟弟是外星人</a>&nbsp;(<a href=\"http://weibo.cn/attention/remark?uid=1950692025&amp;rl=1\">备注</a>)<br/>粉丝258475人<br/><a href=\"http://weibo.cn/attention/del?uid=1950692025&amp;rl=1&amp;st=a69bac\">取消关注</a>&nbsp;<a href=\"http://weibo.cn/attgroup/relisted?uid=1950692025&amp;rl=1&amp;from=att\">分组</a>&nbsp;<a href=\"http://weibo.cn/im/chat?uid=1950692025&amp;rl=1\">私信</a></td></tr></table> <div class=\"s\"></div><table><tr><td valign=\"top\" style=\"width: 52px\"><a href=\"http://weibo.cn/JawboneChina\"><img src=\"http://tp1.sinaimg.cn/5303408196/50/40066174537/1\" alt=\"pic\" /></a></td><td valign=\"top\"><a href=\"http://weibo.cn/JawboneChina\">Jawbone中国</a><img src=\"http://u1.sinaimg.cn/upload/2011/07/28/5337.gif\" alt=\"V\"/>&nbsp;(<a href=\"http://weibo.cn/attention/remark?uid=5303408196&amp;rl=1\">备注</a>)<br/>粉丝2254人<br/><a href=\"http://weibo.cn/attention/del?uid=5303408196&amp;rl=1&amp;st=a69bac\">取消关注</a>&nbsp;<a href=\"http://weibo.cn/attgroup/relisted?uid=5303408196&amp;rl=1&amp;from=att\">分组</a>&nbsp;<a href=\"http://weibo.cn/im/chat?uid=5303408196&amp;rl=1\">私信</a></td></tr></table> <div class=\"s\"></div><table><tr><td valign=\"top\" style=\"width: 52px\"><a href=\"http://weibo.cn/fitbitchina\"><img src=\"http://tp2.sinaimg.cn/5090488381/50/40050939297/1\" alt=\"pic\" /></a></td><td valign=\"top\"><a href=\"http://weibo.cn/fitbitchina\">fitbitChina中国</a><img src=\"http://u1.sinaimg.cn/upload/2011/07/28/5337.gif\" alt=\"V\"/>&nbsp;(<a href=\"http://weibo.cn/attention/remark?uid=5090488381&amp;rl=1\">备注</a>)<br/>粉丝115628人<br/><a href=\"http://weibo.cn/attention/del?uid=5090488381&amp;rl=1&amp;st=a69bac\">取消关注</a>&nbsp;<a href=\"http://weibo.cn/attgroup/relisted?uid=5090488381&amp;rl=1&amp;from=att\">分组</a>&nbsp;<a href=\"http://weibo.cn/im/chat?uid=5090488381&amp;rl=1\">私信</a></td></tr></table><div class=\"s\"></div><div class=\"pa\" id=\"pagelist\"><form action=\"/2468833122/follow\" method=\"post\"><div><a href=\"/2468833122/follow?page=2\">下页</a>&nbsp;<input name=\"mp\" type=\"hidden\" value=\"6\" /><input type=\"text\" name=\"page\" size=\"2\" style='-wap-input-format: \"*N\"' /><input type=\"submit\" value=\"跳页\" />&nbsp;1/6页</div></form></div><div class=\"cd\"><a href=\"#top\"><img src=\"http://u1.sinaimg.cn/3g/image/upload/0/62/203/18979/5e990ec2.gif\" alt=\"TOP\"/></a></div><div class=\"pms\"> <a href=\"http://weibo.cn\">首页<span class=\"tk\">!</span></a>.<a href=\"http://weibo.cn/topic/240489\">反馈</a>.<a href=\"http://weibo.cn/page/91\">帮助</a>.<a  href=\"http://down.sina.cn/weibo/default/index/soft_id/1/mid/0\"  >客户端</a>.<a href=\"http://weibo.cn/spam/?rl=1&amp;type=3&amp;fuid=2468833122\" class=\"kt\">举报</a>.<a href=\"http://passport.sina.cn/sso/logout?r=http%3A%2F%2Fweibo.cn%2Fpub%2F%3Fvt%3D&amp;entry=mweibo\">退出</a></div><div class=\"c\">设置:<a href=\"http://weibo.cn/account/customize/skin?tf=7_005&amp;st=a69bac\">皮肤</a>.<a href=\"http://weibo.cn/account/customize/pic?tf=7_006&amp;st=a69bac\">图片</a>.<a href=\"http://weibo.cn/account/customize/pagesize?tf=7_007&amp;st=a69bac\">条数</a>.<a href=\"http://weibo.cn/account/privacy/?tf=7_008&amp;st=a69bac\">隐私</a></div><div class=\"c\">彩版|<a href=\"http://m.weibo.cn/?tf=7_010\">触屏</a>|<a href=\"http://weibo.cn/page/521?tf=7_011\">语音</a></div><div class=\"b\">weibo.cn[08-11 22:05]</div></body></html>"
    #WeiboCatch().catchprofile(profile);
    #WeiboCatch().catchfollow(follow)
    WeiboCatch.findweibo("sweb")
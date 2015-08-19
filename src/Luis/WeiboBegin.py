#!/usr/bin/env python
#_*_ coding: utf-8_*_
'''
Created on 2015-7-27
@author: luis
'''
import cookielib
import os
import re
import urllib2
from Luis.WeiboLogin import WeiboLogin
from Luis.WeiboCatch import WeiboCatch
class WeiboBegin(object):
    def __init__(self):
        self.filename='FileCookieJar.txt'
    def fastlogin(self):
        home_url = 'http://www.weibo.cn'
        req = urllib2.Request(home_url) 
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
        #ckjar = cookielib.MozillaCookieJar(os.path.join('C:\Documents and Settings\tom\Application Data\Mozilla\Firefox\Profiles\h5m61j1i.default', 'cookies.txt'))
        ckjar = cookielib.MozillaCookieJar()
        #这里读取cookie
        if(os.path.exists(self.filename)):
            ckjar.load(self.filename, ignore_discard=True, ignore_expires=True)
            for item in ckjar:
                print "name:" +item.name
                print "Value:"+item.value
        ckproc = urllib2.HTTPCookieProcessor(ckjar)
        opener = urllib2.build_opener(ckproc)
        f = opener.open(req) 
        htm = f.read().decode('utf-8')
        print htm
        for item in ckjar:
            print "name:" +item.name
            print "Value:"+item.value
        ckjar.save(self.filename,ignore_discard=True, ignore_expires=True)
        f.close()
        return htm
    def refreshlogin(self,htmconf):
        reg=u"<a href=('http://login.weibo.cn/[^\u4E00-\u9FA5]*?)[>]+?[\u4E00-\u9FA5]{2}</a>"
        pattern=re.compile(reg)
        strtemp='用户身份无效，请稍候重新登录'
        ckjar = cookielib.MozillaCookieJar()
        #这里读取cookie
        if(os.path.exists(self.filename)):
            ckjar.load(self.filename, ignore_discard=True, ignore_expires=True)
        if(not("gsid_CTandWM" in str(ckjar)) or htmconf.find(strtemp.decode('utf8'))!=-1):
            if(os.path.exists(self.filename)):
                os.remove(self.filename)
            htm=self.fastlogin()  
            loginweb=pattern.search(htm).group(1)
            #表示从第二个取到倒数第二个，去掉模式串中两头的单引号
            loginweb=loginweb[1:-1]
            print loginweb
            params=loginweb.split(';')
            for param in params:
                print param
            wl=WeiboLogin(loginweb,"","")
            wl.getweibologin()
        else:
            WeiboCatch.findweibo(htmconf)
if __name__ == '__main__':
    weibobegin=WeiboBegin()
    hh=weibobegin.fastlogin()
    weibobegin.refreshlogin(hh)

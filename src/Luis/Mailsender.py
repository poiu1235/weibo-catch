'''
Created on 2015-9-26

@author: luis
'''
import ConfigParser
from email.header import Header
from email.mime.text import MIMEText
import os
import smtplib

class Mailsender(object):
    '''
    classdocs
    '''


    def __init__(self):
        pass
    def getconfig(self):
        try:
            config=ConfigParser.ConfigParser()
            with open('localconfig','r') as cfgfile:
                config.readfp(cfgfile)
                EUSERNAME=config.get('email','emailuser')
                EPASSWD=config.get('email','emailpwd')
                EHOST=config.get('email','emailhost')
                ERECEIVER=config.get('email','emailrec')
                return (EUSERNAME,EPASSWD,EHOST,ERECEIVER)
        except:
            print "no config"
            os._exit()
    def sendmail(self,error):
        config=self.getconfig()
        
        sender = config[0]
        receiver = config[3]
        subject = 'python weibo-catch error'
        smtpserver = config[2]
        username = config[0]
        password = config[1]
        
        msg=MIMEText(error,'plain','utf8')
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject']=Header(subject,'utf8')
        
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver)
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()
        
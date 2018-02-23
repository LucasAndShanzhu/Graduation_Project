# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-10-23 15:28:18
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-01-02 19:24:11

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

# from .. import app

import smtplib
import chardet

class MailSender(object):

    # def __new__(cls, *args, **kws):
    #     if not hasattr(cls, "_instance"):
    #         org = super(MailSender, cls)
    #         cls._instance = org.__new__(cls, *args, **kws)
    #     return cls._instance
    
    def __init__(self, user, pwd, smtp_server, port):
        self.user = user
        self.pwd = pwd
        self.smtp_server = smtp_server
        self.port = port
        self.link()

    def link(self):
        self.server = smtplib.SMTP_SSL(self.smtp_server, self.port, timeout=5)
        self.server.login(self.user, self.pwd)        

    def sendMail(self, to="gong_lingxiao@163.com", message="", subject=u''):
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = MailSender._format_addr(u'spider <%s>' % self.user)
        msg['To'] = MailSender._format_addr('lucas <%s>' % to)
        msg['Subject'] = Header(subject, 'utf-8').encode()
        self.server.sendmail(self.user, to, msg.as_string())

    def quit(self):
        self. server.quit()

    @staticmethod
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr( (Header(name, 'utf-8').encode(), addr.encode('utf-8') if isinstance(addr, unicode) else addr) )

    @staticmethod
    def send(message, subject=u''):
        args = {}
        message = message.encode('utf8')
        args['message'] = message
        if subject == '':
            subject = u'默认爬虫警告.'
        args['subject'] = subject
        try:
            mail = MailSender('gong_lingxiao@163.com', 'glx1997', 'smtp.163.com', 465)
            mail.sendMail(**args)
            mail.quit()
        except:
            from redis import Redis 
            try:
                temp_redis = Redis()
                temp_redis.rpush('email', 'message')
            except Exception as e:
                import os
                os._exit(-1)

if __name__ == '__main__':
    MailSender.send(u'hello, this is the hello world', u'Test')




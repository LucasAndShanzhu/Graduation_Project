# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-07 09:37:53
# @Last Modified by:   shanzhu
# @Last Modified time: 2017-12-26 16:04:40
from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest
from chardet import detect

import json
import oss2
import os
import random

from app_email import MailSender

class Oss(object):

    def __init__(self, conf, session_name):
        self.conf = conf
        self.token = None
        self.auth = None
        self.session_name = session_name
        self._get_auth()

    def upload(self, bucket, filename, file):
        fail_time = 0
        while True:
            if fail_time > 10:
                break
            if self.auth is  None:
                f = open(self.conf.sts.temp + '/' + filename, 'w')
                f.write(file.read())
                f.close()
                break
            else:
                try:
                    bucket = oss2.Bucket(self.auth, self.conf.oss.endpoint, bucket)
                    if not isinstance(filename, unicode):
                        encoding = detect(filename)['encoding']
                        if encoding != 'ascii':
                            filename = filename.decode(encoding)
                    bucket.put_object(filename, file)
                except oss2.exceptions.NoSuchBucket:
                    raise
                except Exception as e:
                    raise
                else:
                    break

    def _get_auth(self):
        self.token = self._get_token(self.conf, self.session_name)
        try:
            self.auth = oss2.StsAuth(self.token['Credentials']['AccessKeyId'],
                                    self.token['Credentials']['AccessKeySecret'],
                                    self.token['Credentials']['SecurityToken'])
        except Exception as e:
            self.auth = None
            self.token = None
            raise

    def _get_token(self, conf, session_name):
        session_name = "{}{}".format(session_name, random.randint(1,10000))
        clt = client.AcsClient(conf.sts.id, conf.sts.secret, conf.sts.area)
        req = AssumeRoleRequest.AssumeRoleRequest()

        req.set_accept_format('json')
        req.set_RoleArn(conf.sts.arn)
        req.set_RoleSessionName(session_name)
        req.set_DurationSeconds(1200)

        body = clt.do_action_with_exception(req)
        try:
            token = json.loads(body)
        except Exception as e:
            MailSender.send('oss get sts token is error, e: {}'.format(e))
            self.token = self.auth = None
            if not os.path.exists(conf.sts.temp):
                os.mkdir(conf.sts.temp)
        else:
            return token


if __name__ == '__main__':
    from config import Config
    conf = Config('/Users/gonglingxiao/Graduation_Project/spider/spider.ini')
    oss = Oss(conf, 'spiderlucas')
    oss._get_auth()
    file = open('test.ini', 'r')
    oss.upload('spider-lucas', 'test.ini', file)
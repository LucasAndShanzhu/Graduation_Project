# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-06 09:59:38
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-01-23 17:32:51

import redis
import json
import sys, os
import socket

from app_email import MailSender
from config import Config
from Signal import Signal

class SRedis(object):
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config
        self._link_redis()

    @staticmethod
    def get_redis(host, port, password = None, socket_timeout=5, socket_connect_timeout=5):
        args = {
            'host': host,
            'port': port,
            'socket_timeout': socket_timeout,
            'socket_connect_timeout': socket_connect_timeout
        }
        if password is not None:
            args['password'] = password
        try:
            rds = redis.Redis(**args)
            rds.ping()
            return rds
        except Exception as e:
            return None

    def _link_redis(self):
        timeout = int(self.config.redis.socket_timeout)
        args = {
            'host': self.config.redis.host,
            'port': int(self.config.redis.port),
            'socket_timeout': timeout,
            'socket_connect_timeout': timeout 
        }
        password = self.config.redis.get('password')
        if password:
            args['password'] = password
        self.redis = redis.Redis(**args)
        self.exec_redis('ping')

    def exec_redis(self, func, *args):
        func_obt = func if hasattr(func, '__call__') else getattr(self.redis, func)
        try:
            # self.logger.write('redis ping, %d' % os.getpid())
            output = func_obt(*args)
            return output
        except AttributeError as e:
            self.logger.error()
            Signal.signal(15)
        except(redis.exceptions.TimeoutError, redis.exceptions.ConnectionError):
            self.logger.error()
            MailSender.send(u'redis-server is down, please to restart', u'redis-error')
            Signal.signal(15)
        except redis.exceptions.ResponseError as e:
            print repr(e)
            return None
        except Exception:
            self.logger.error()
            Signal.signal(15)
        return None

if __name__ == '__main__':
    client = SRedis(None)
    print client.exec_redis('sadd', 'ip', '202.53.174.162:8080')
    client.close()
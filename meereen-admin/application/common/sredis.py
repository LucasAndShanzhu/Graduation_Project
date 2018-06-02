# -*- coding: utf-8 -*-
from redis import Redis

class RedisUtil(object):
    def __init__(self, config):
        host = config.REDIS_HOST
        port = config.REDIS_PORT
        password = config.REDIS_PASSWORD
        socket_timeout = config.REDIS_TIMEOUT
        args = {
            'host': host,
            'port': port,
            'password': password,
            'socket_timeout': socket_timeout,
            'socket_connect_timeout': socket_connect_timeout
        }
        self.args = args
        self.redisClient = None
        self._link()

    def _link(self):
        if not self.redisClient:
            self.redisClient = Redis(**self.args)
            self.redisClient.ping()

    def getRedis(self):
        return self.redisClient
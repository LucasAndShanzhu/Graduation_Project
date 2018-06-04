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
            'socket_connect_timeout': socket_timeout
        }
        self.args = args

    def link(self):
        redisClient = Redis(**self.args)
        redisClient.ping()
        return redisClient
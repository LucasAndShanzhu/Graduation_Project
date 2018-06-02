# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-02-09 09:55:27
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-02-09 10:37:49

class Config(object):
    DEBUG = False
    PERMANENT_SESSION_LIFETIME = 3600

    MONGO_HOST = '127.0.0.1'
    MONGO_PORT = 27017
    MONGO_DBNAME = 'item'
    MONGO_USERNAME = 'lucas'
    MONGO_PASSWORD = '863bbc7b3febf915dd417c6195f74686'
    MONGO_CONNECT = False

    LOG_FILE_NAME = '/home/lucas/var/log/meereen-admin/access.log'

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_PASSWORD = 'glx1997'
    REDIS_TIMEOUT = 5

    SESSION_TYPE = 'filesystem'
    SECRET_KEY = '\xd7\x83F\x92\xeb\x07\xc2>W\x96\x1b\xfb\xaa\x90\x95\xdf\xd0\xe2\x97\xe0\x9dr\xaf5'

    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'gong_lingxiao@163.com'
    MAIL_PASSWORD = 'glx1997'

    MYSQL_DATABASE_HOST = '127.0.0.1'
    MYSQL_DATABASE_PORT = 3306
    MYSQL_DATABASE_USER = 'lucas'
    MYSQL_DATABASE_PASSWORD = 'glx1997'
    MYSQL_DATABASE_DB = 'meereen_admin'

class ProductionConfig(Config):
    LOG_FILE_NAME = '/var/log/meereen_admin/access.log'

class DebugProductionConfig(Config):
    DEBUG = True
    PERMANENT_SESSION_LIFETIME = 86400

config = {
    'debug': DebugProductionConfig,
    'production': ProductionConfig,

    'default': ProductionConfig
}

def getConfig(env='default'):
    return config[env]
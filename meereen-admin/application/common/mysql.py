# -*- coding: utf-8 -*-

import pymysql
from sexceptions import MysqlTimeoutException

class MysqlUtil(object):

    def __init__(self, config):
        host = config.MYSQL_DATABASE_HOST if hasattr(config, 'MYSQL_DATABASE_HOST') else '127.0.0.1'
        port = config.MYSQL_DATABASE_PORT if hasattr(config, 'MYSQL_DATABASE_PORT') else 3306 
        user = config.MYSQL_DATABASE_USER if hasattr(config, 'MYSQL_DATABASE_USER') else 'lucas'
        password = config.MYSQL_DATABASE_PASSWORD if hasattr(config, 'MYSQL_DATABASE_PASSWORD') else 'glx1997'
        db = config.MYSQL_DATABASE_DB if hasattr(config, 'MYSQL_DATABASE_DB') else 'meereen_admin'
        args = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': db,
            'charset': "utf8mb4"
        }

        self.args = args
        self.link = None

    def connect(self):
        if self.link:
            self.close()
        try:
            self.link = pymysql.connect(**self.args)
        except Exception as e:
            print e
            self.link = None

    def getCursor(self):
        if self.link:
            return self.link.cursor()
        return None

    def getConnect(self):
    	if self.link:
    		return self.link
    	raise MysqlTimeoutException()

    def close(self):
        if self.link:
            self.link.close()
            self.link = None


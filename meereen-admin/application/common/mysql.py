# -*- coding: utf-8 -*-

import pymysql
from sexceptions import MysqlTimeoutException

class MysqlUtil(object):

    def __init__(self, config):
        host = config.MYSQL_DATABASE_HOST if hasattr(config, MYSQL_DATABASE_HOST) else '127.0.0.1'
        port = config.MYSQL_DATABASE_PORT if hasattr(config, MYSQL_DATABASE_PORT) else 3306 
        user = config.MYSQL_DATABASE_USER if hasattr(config, MYSQL_DATABASE_USER) else 'lucas'
        password = config.MYSQL_DATABASE_PASSWORD if hasattr(config, MYSQL_DATABASE_PASSWORD) else 'glx1997'
        db = config.MYSQL_DATABASE_DB if hasattr(config, MYSQL_DATABASE_DB) else 'meereen_admin'
        args = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': db,
            'charset': "utf8mb4"
        }

        self.args = args
        self.connect = None

    def connect(self):
        if self.connect:
            self.close()
        try:
            self.connect = pymysql.connect(**self.args)
        except Exception as e:
            self.connect = None

    def getCursor(self):
        if self.connect:
            return self.connect.cursor()
        return None

    def getConnect(self):
    	if self.connect:
    		return self.connect
    	raise MysqlTimeoutException()

    def close(self):
        if self.connect:
            self.connect.close()
            self.connect = None


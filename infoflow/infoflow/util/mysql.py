# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-11 19:22:35
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-23 10:46:05

import pymysql

class Mysql(object):
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None

    def connect(self, database=None):
        if database is None:
            database = self.config.mysql.database
        args = {
            'host': self.config.mysql.host,
            'port': int(self.config.mysql.port),
            'user': self.config.mysql.user,
            'password': self.config.mysql.password,
            'database': database,
            'charset': "utf8mb4"
        }
        conn = pymysql.connect(**args)
        self.conn = conn
        self.cursor = conn.cursor()

    def get_connect(self):
        return self.conn

    def get_cursor(self):
        if self.cursor is None:
            self.cursor = self.conn.cursor()
        return self.cursor

    def close_cursor(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None

    def exec_mysql(self, sql, cursor=None, one=False):
        try:
            if cursor is None:
                cursor = self.cursor
            out = cursor.execute(sql)
            if out == 0:
                return []
        except Exception as e:
            return []
        return cursor.fetchone() if one else cursor.fetchall()

    def edit(self, sql, conn=None, cursor=None, data=None):
        if conn is None:
            conn = self.conn
        if cursor is None:
            cursor = self.cursor
        try:
            if data:
                cursor.execute(sql, data)
            else:
                cursor.execute(sql)
            conn.commit()
        except Exception as e:
            pass

    def get_db(self, database):
        if isinstance(database, str):
            database = {'database': database}
        args = {
            'host': database.get('host', self.config.mysql.host),
            'port': database.get('port', int(self.config.mysql.port)),
            'user': database.get('user', self.config.mysql.user),
            'password': database.get('password', self.config.mysql.password),
            'database': database['database'],
            'charset': "utf8mb4"
        }            
        conn = pymysql.connect(**args)
        return conn

    def commit(self):
        self.conn.commit()

    def close(self):
        self.close_cursor()
        if self.conn is not None:
            self.conn.close()

if __name__ == '__main__':
    from config import Config
    config = Config('test.ini')
    log = Logger('test', config.log.path)
    mysql = Mysql(config, log)
    print type(mysql.connect('meereen'))
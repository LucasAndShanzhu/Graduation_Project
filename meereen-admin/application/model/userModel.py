# -*- coding: utf-8 -*-
import datetime
from application import app
from hashlib import md5
from ..common import util

class UserModel(object):

    @staticmethod
    def getUserId(username):
        app.mysql.connect()
        cursor = app.mysql.getCursor()
        sql = "select id from user where nickname=%s"
        cursor.execute(sql, (username,))
        output = cursor.fetchone()
        app.mysql.close()
        if not output:
            return None
        else:
            return int(output[0])

    @staticmethod
    def verfiPassword(username, password):
        print app.mysql.__dict__
        app.mysql.connect()
        cursor = app.mysql.getCursor()
        sql = "select password from user where nickname=%s"
        cursor.execute(sql, (username,))
        output = cursor.fetchone()
        userPwd = output[0] if output else None
        pwd = md5(password).hexdigest()
        app.mysql.close()
        return pwd == userPwd

    @staticmethod
    def addUser(nickname, password, email):
        app.mysql.connect()
        cursor = app.mysql.getCursor()
        sql = "select id from user where email=%s"
        cursor.execute(sql, (email,))
        output = cursor.fetchone()
        userId = None if output else output[0]
        if userId is not None:
            app.mysql.close()
            return None
        pwd = md5(password).hexdigest()
        pwdRaw = util.desEncrypt(password)
        sql = "insert into user(nickname, email, password, password_raw, login_in, created_at) values(%s, %s, %s, %s, %s, %s)"
        current = datetime.datetime.now()
        cursor.execute(sql, (nickname, email, pwd, pwdRaw, current, current))
        userId = cursor.lastrowid
        connect = app.mysql.getConnect()
        connect.commit()
        app.mysql.close()
        return userId
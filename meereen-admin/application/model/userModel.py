# -*- coding: utf-8 -*-
import datetime
from application import app
from hashlib import md5
from ..common import util

class UserModel(object):

    @staticmethod
    def getUserId(username):
        connect = app.mysql.connect()
        cursor = connect.cursor()
        sql = "select id from user where nickname=%s"
        cursor.execute(sql, (username,))
        output = cursor.fetchone()
        connect.close()
        if not output:
            return None
        else:
            return int(output[0])

    @staticmethod
    def verfiPassword(username, password):
        connect = app.mysql.connect()
        cursor = connect.cursor()
        sql = "select password from user where nickname=%s"
        cursor.execute(sql, (username,))
        output = cursor.fetchone()
        userPwd = output[0] if output else None
        pwd = md5(password).hexdigest()
        connect.close()
        return pwd == userPwd

    @staticmethod
    def addUser(nickname, password, email):
        connect = app.mysql.connect()
        cursor = connect.cursor()
        sql = "select id from user where email=%s"
        cursor.execute(sql, (email,))
        output = cursor.fetchone()
        userId = None if not output else output[0]
        if userId is not None:
            connect.close()
            return None
        pwd = md5(password).hexdigest()
        pwdRaw = util.desEncrypt(password)
        sql = "insert into user(nickname, email, password, password_raw, login_in, created_at) values(%s, %s, %s, %s, %s, %s)"
        current = datetime.datetime.now()
        cursor.execute(sql, (nickname, email, pwd, pwdRaw, current, current))
        userId = cursor.lastrowid
        connect.commit()
        connect.close()
        return userId
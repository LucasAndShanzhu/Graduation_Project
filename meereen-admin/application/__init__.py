# -*- coding: utf-8 -*-
from flask import Flask, session, redirect, url_for

from common import mysql, mongo, redis
from config import getConfig

def createApp(env="default"):
    app = Flask(__name__)
    config = getConfig()
    app.config.from_object(config)

    app.mysql = mysql.MysqlUtil(config)
    app.mongo = mongo.MongoUtil(config)

    return app

app = createApp()

@app.route('/')
def test():
    print 'ok'

def hasLogin(func):
    def wrapper():
        if 'username' not in session:
            return redirect(url_for('login.login'))
        return func()
    return wrapper
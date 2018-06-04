# -*- coding: utf-8 -*-
import rsa
from flask import Flask, session, redirect, url_for, request, jsonify

from common import mysql, mongo, sredis
from config import getConfig

def createApp(env="default"):
    app = Flask(__name__)
    config = getConfig()
    app.config.from_object(config)

    rsaKey = rsa.newkeys(1024)
    app.public = rsaKey[0]
    app.publicStr = ''.join(app.public.save_pkcs1().split('\n')[1:-2])
    app.pke = hex(app.public.e)[2:]
    app.pkn = hex(app.public.n)[2:-1]
    app.private = rsaKey[1]
    app.mysql = mysql.MysqlUtil(config)
    app.redis = sredis.RedisUtil(config)
    # app.mongo = mongo.MongoUtil(config)
    return app

app = createApp()

def hasLogin(func):
    def wrapper():
        if 'username' not in session:
            method = request.method
            if method == 'GET':
                return redirect(url_for('login.login'))
            else:
                return jsonify({'error': 999})
        return func()
    return wrapper

from bp import registerBp
registerBp(app)
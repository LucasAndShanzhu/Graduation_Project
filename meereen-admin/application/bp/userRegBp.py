# -*- coding: utf-8 -*-
from flask import Blueprint, request, render_template, jsonify, session
from random import randint, seed
from base64 import b64decode
from application import app, hasLogin
from ..common import util, mailer
from ..model import userModel

userRegBp = Blueprint('register', __name__)

@userRegBp.route('/register', methods=['GET'])
def getRegister():
    return render_template('register.html')

@userRegBp.route('/requestVCode', methods=['POST'])
def sendVCode():
    email = request.form.get('email', '')
    retData = {'error': 999}
    if not email:
        return jsonify(retData)
    code = ''.join([str(randint(0,9)) for i in xrange(6)])
    try:
        redisLink = app.redis.link()
        redisKey = "{}_code".format(email)
        redisLink.set(redisKey, code)
        redisLink.expire(redisKey, 80)
        mailer.MailSender.send(code)
        retData['error'] = 0
    except Exception as e:
        print e
        retData['error'] = 1
    return jsonify(retData)

@userRegBp.route('/register', methods=['POST'])
def register():
    nickname = request.form.get('nickname', '')
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    code = request.form.get('code', '')
    retData = {'error': 999}
    if not nickname or not email or not password or not code:
        return jsonify(retData)
    redisLink = app.redis.link()
    redisKey = "{}_code".format()
    redisCode = redisLink.get(redisKey)
    if redisCode != code:
        retData['error'] = 1
    else:
        try:
            password = b64decode(password)
            pwd = util.rsaDecrypt(app.private, password)
        except Exception as e:
            retData['error'] = 2
        else:
            userId = userModel.UserModel.addUser(nickname, pwd, email)
            if userId is None:
                retData['error'] = 3
            else:
                retData['error'] = 0
                redisLink.delete(redisKey)
                session['username'] = nickname
    return jsonify(retData)

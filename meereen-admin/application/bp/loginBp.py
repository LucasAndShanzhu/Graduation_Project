# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, jsonify, session
from base64 import b64encode, b64decode
from application import app, hasLogin
from ..common import util
from ..model import userModel

loginBp = Blueprint('login', __name__)

@loginBp.route('/login', methods=['GET'])
def login():
    return render_template('login.html', publice=app.pke, publicn=app.pkn, publick=app.publicStr)

@hasLogin
@loginBp.route('/login', methods=['POST'])
def vertify():
    nickname = request.form.get('nickname', None)
    password = request.form.get('password', None)
    password = b64decode(password)
    retData = {'error': 2}
    if not nickname or not password:
        return jsonify(retData)
    pwd = util.rsaDecrypt(app.private, password)
    output = userModel.UserModel.verfiPassword(nickname, pwd)
    if output:
        retData['error'] = 0
        session['username'] = nickname
    else:
        retData['error'] = 1
    return jsonify(retData)

@loginBp.route('/re', methods=['POST'])
def reCode():
    pwd = request.form.get('password', '')
    retData = {'data': ''}
    if not pwd:
        return jsonify(retData)
    try:
        pwd = pwd[32:]
    except:
        return jsonify(retData)
    retData['data'] = b64encode(util.rsaEncrypt(app.public, pwd)) 
    return jsonify(retData)



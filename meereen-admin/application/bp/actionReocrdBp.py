# -*- coding: utf-8 -*-
from flask import Blueprint, request, render_template, jsonify, session
from bson import ObjectId
from application import app, hasLogin
from ..model import userModel, recordModel

actionReocrdBp = Blueprint('record', __name__, url_prefix='/record')

@hasLogin
@actionReocrdBp.route('/point', methods=['POST'])
def record():
    nickaname = session.get('username', '')
    itemId = request.form.get('item', '')
    action = request.form.get('action', '')
    retData = {'error': 999}
    if not nickaname or not itemId or not action:
        return jsonify(retData)
    userId = userModel.UserModel.getUserId(nickaname)
    if userId is None:
        return jsonify(retData)
    if action == 'click':
        app.mongo.link()
        collect = app.mongo.getCollect("article_big_image")
        collect.update({'_id': ObjectId(itemId)}, {'$inc': {'click_num': 1}})
        app.mongo.close()
    if recordModel.RecordModel.recordAction(userId, itemId, action):
        retData['error'] = 0
    else:
        retData['error'] = 1
    return jsonify(retData)

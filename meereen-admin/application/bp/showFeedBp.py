# -*- coding: utf-8 -*-
from flask import Blueprint, request, render_template, jsonify, session
from bson import ObjectId
from application import app, hasLogin
from ..common import mongo
from ..model import userModel
from ..moduleApi import recommend

showFeedBp = Blueprint('feed', __name__, url_prefix='/feed')

@showFeedBp.route('/show', methods=['GET'])
@hasLogin
def show():
    nickname = session['username']
    userId = userModel.UserModel.getUserId(nickname)
    itemList = []
    if userId:
        recommender = recommend.RecommendApi()
        itemIdList = recommender.getRecommendList(userId) 
        app.mongo.link()
        redisLink = app.redis.link()
        collect = app.mongo.getCollect('article_big_image')
        redisKey = "user_item_list_{}_set".format(userId)
        for itemSet in itemIdList:
            itemId = itemSet[0]
            itemData = collect.find_one({'_id': ObjectId(itemId)})
            itemData['cover'] = 'https://spider-lucas.oss-cn-beijing.aliyuncs.com/image/' + itemData['image'][0] if itemData.get('image', []) else ''
            itemData['detail'] = itemData['detail'] if itemData.get('detail', '') else '暂无简介'
            itemData['author'] = itemData['source_detail']
            itemData['_id'] = str(itemData['_id'])
            itemData['url'] = 'https://spider-lucas.oss-cn-beijing.aliyuncs.com/html/' + itemData['content']
            itemList.append(itemData)
            redisLink.sadd(redisKey, itemId)
            collect.update({'_id': ObjectId(itemId)}, {'$inc': {'show_num': 1}})
            app.mongo.close()
    app.mongo.close()
    return render_template('feed.html', itemList=itemList)
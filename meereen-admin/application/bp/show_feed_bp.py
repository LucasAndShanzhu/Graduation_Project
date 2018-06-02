# -*- coding: utf-8 -*-

from flask import Blueprint, request
from application import app
from ..common import mongo

show_feed_blueprint = Blueprint('show_feed', url_prefix='/show')

@show_feed_blueprint.route('feed', methods=['GET'])
def show_feed():
    mongo_db = mongo.MongoDb(app.config)
    collect = mongo_db.get_collect('article_big_image')
    try:
        page = request.args.get('page', 0)
        feed_num = request.args.get('window', 0)
        page = int(page)
        feed_num = int(feed_num)
    except:
    	page = 0
    	feed_num = 20
    

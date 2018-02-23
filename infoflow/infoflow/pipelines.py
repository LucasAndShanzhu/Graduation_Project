# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from util import util
ulogger = util.ulogger
conf = util.conf
uredis = util.uredis
mysql = util.util_mysql

from hashlib import md5
from .util import logger, sredis, mongo, util
import datetime, time

class InfoflowPipeline(object):
    def __init__(self):
        self.conf = conf
        self.logger = logger.Logger(self.conf.log.name, self.conf.log.path)
        self.redis = sredis.SRedis(self.conf, self.logger)
        self.mongo = mongo.Mongo(conf, ulogger)

    def process_item(self, item, spider):
        if item is None or not item:
            return item
        spider_name = spider.name

        if spider_name in ("foreignip", "nationip", "proxydbIp"):
            proxy = item['ip'] + ":" + item['port']
            self.redis.exec_redis("sadd", self.conf.pool.verify_pool, proxy)

        elif spider_name in ('qingboWx', 'sougouWx', 'toutiao'):
            collection = self.mongo.get_collection(collection='article_big_image')
            data = item.__dict__['_values']
            _id = self.getAutoIncId('article_big_image_id')
            data['id'] = _id
            data['status_code'] = 0
            data['CTR'] = 0.0
            data['show_num'] = 0
            data['click_num'] = 0
            timestamp = int(time.time())
            key = "{}#{}#{}".format(data['title'], data['source'], timestamp)
            content = md5(key).hexdigest() + ".html"
            parse_data = "{}|wx|{}".format(content, data['url'])
            self.redis.exec_redis('sadd', 'need_parsed_html', parse_data)
            data['content'] = content
            result = self.mongo.find_one(collection, {'md5': data['md5']}, {"id": 1, "tag": 1})
            if not result:
                if 'tag' in data:
                    data['tag'] = [data['tag']]
                now = self.get_current_time()
                data['update_at'] = now
                data['created_at'] = now
                self.mongo.insert(collection, data)
            else:
                tags = result['tag']
                tag =  data['tag']
                if tag not in tags:
                    tags.append(tag)
                    item_id = result['id']
                    self.mongo.update(collection, {'$set': {'tag': tags, 'update_at': self.get_current_time()}}, {'id': item_id})
        return item

    def get_current_time(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def getAutoIncId(self, collect_name):
        collection = self.mongo.get_collection(collection='item_id')
        query = {"name": collect_name}
        update = {'$inc': {'id': 1}}
        try:
            id_ = self.mongo.find_and_modify(collection, query, update)
            return id_['id']
        except Exception:
            self.logger.error()
            return -1

    def close_spider(self, spider):
        if mysql is not None:
            mysql.close()
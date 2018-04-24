# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-03-26 17:54:20
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-04-19 16:18:06
import sys, os, time, jieba
import jieba.analyse
import requests

from redis import Redis
import multiprocessing
import signal
from bson import ObjectId
from bs4 import BeautifulSoup
from pymongo import MongoClient

path = os.getcwd()
chs_dict_path = 'webdict_with_freq.txt'
idf_txt = path + '/../idf.txt'
jieba.load_userdict(idf_txt)

jieba.analyse.set_idf_path(idf_txt)
mongo_args = {
    'host': '120.79.32.91',
    'port': 27017,
    'user': 'lucas',
    'passwd': '863bbc7b3febf915dd417c6195f74686',
    'database': 'item'
}
mongo_uri = "mongodb://{}:{}@{}:{}/{}".format(mongo_args['user'], mongo_args['passwd'], mongo_args['host'], mongo_args['port'], mongo_args['database'])
oss_prefix = 'https://spider-lucas.oss-cn-beijing.aliyuncs.com/html/'

def url_run():
    mongo = MongoClient(mongo_uri)
    redis = Redis(password='glx1997')
    col = mongo.item.article_big_image
    while(True):
        item_list = col.find({'status_code': 0, 'key_words': {'$eq': None}}, {'content': 1, '_id': 1}).limit(10)
        if not item_list:
            time.sleep(60)
        else:
            for item in item_list:
                redis.sadd('key_word_needed_item', "{}#{}".format(item['content'], item['_id']))

def process_run():
    mongo = MongoClient(mongo_uri)
    redis = Redis(password='glx1997')
    col = mongo.item.article_big_image
    while True:
        unparsed_item = redis.spop('key_word_needed_item')    
        if unparsed_item is None:
            time.sleep(60)
        else:
            item_list = unparsed_item.split('#')
            url = oss_prefix + item_list[0]
            item_id = item_list[1]
            res = requests.get(url)
            tree = BeautifulSoup(res.content, 'lxml')
            text = tree.text.strip()
            keywords = jieba.analyse.extract_tags(text)[:5]
            col.update({'_id': ObjectId(item_id)}, {'$set': {'key_words': keywords}})

processes = []

def quit(*args):
    global processes
    for process in processes:
        try:
            if process.is_alive():
                os.kill(process.pid, 9)
        except Exception as e:
            pass

def run():
    global processes
    process = multiprocessing.Process(target=url_run)
    processes.append(process)
    process.start()
    for i in range(4):
        process = multiprocessing.Process(target=process_run)
        processes.append(process)
        process.start()
    signal.signal(signal.SIGTERM, quit)
    for p in processes:
        p.join()

if __name__ == '__main__':
    run()

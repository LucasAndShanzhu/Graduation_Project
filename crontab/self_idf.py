# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-03-21 20:11:38
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-22 14:59:26
# 
# 获取自定义的idf-反词频文档.

import requests
import jieba
import signal
from hashlib import md5
from redis import Redis
import multiprocessing
from bs4 import BeautifulSoup
from pymongo import MongoClient

redis_args = {
    'host': '127.0.0.1',
    'password': 'glx1997'
}

import sys, os
path = os.getcwd()
chs_dict_path = 'webdict_with_freq.txt'
jieba.load_userdict(path + '/' + chs_dict_path)

mongo_args = {
    'host': '127.0.0.1',
    'port': 27017,
    'user': 'lucas',
    'passwd': '863bbc7b3febf915dd417c6195f74686',
    'database': 'item'
}

mongo_uri = "mongodb://{}:{}@{}:{}/{}".format(mongo_args['user'], mongo_args['passwd'], mongo_args['host'], mongo_args['port'], mongo_args['database'])
oss_prefix = 'https://spider-lucas.oss-cn-beijing.aliyuncs.com/html/'
jieba.load_userdict


class Idf(object):
    def __init__(self):
        self.redis = Redis(**redis_args)

    def downloads(self, url):
        try:
            res = requests.get(url)
            print url
            print res.content
        except Exception as e:
            print e
            return None
        return res.content

    def get_text_list(self, html):
        tree = BeautifulSoup(html, 'lxml')
        text_list = tree.text.strip().split('\n')
        return filter(lambda x: len(x)>60, text_list)

    def get_words(self, text):
        iterator = jieba.cut(text, False)
        for word in iterator:
            yield word

    def run(self, url):
        html = self.downloads(url)
        if html is None:
            return 
        text_list = self.get_text_list(html)
        md5_str = md5(url).hexdigest()
        redisKey = md5_str + '_words'
        for text in text_list:
            for word in self.get_words(text):
                if not self.redis.sismember(redisKey, word):
                    self.redis.sadd(redisKey, word)
                    self.redis.hincrby('word_count', word, 1)
        self.redis.delete(redisKey)

def url_process():
    mongodb = MongoClient(mongo_uri)
    redis = Redis(**redis_args)
    collection = mongodb[mongo_args['database']]['article_big_image']
    content_cursor = collection.find({}, {'content': 1})
    redis.set('idf_handle', 'start')
    for content in content_cursor:
        url = oss_prefix + content['content']
        redis.sadd('idf_url', url)
    redis.set('idf_handle', 'over')

def process_run():
    redis = Redis(**redis_args)
    idf = Idf()
    while(True):
        url = redis.spop('idf_url')
        if not url:
            if redis.get('idf_handle') != 'start':
                return
        idf.run(url)

def quit(*args):
    global processes
    for process in processes:
        try:
            if process.is_alive():
                os.kill(process.pid, 9)
        except Exception as e:
            pass

processes = []
def run():
    global processes
    process = multiprocessing.Process(target=url_process)
    processes.append(process)
    process.start()
    for i in range(2):
        process = multiprocessing.Process(target=process_run)
        processes.append(process)
        process.start()
    signal.signal(signal.SIGTERM, quit)
    for p in processes:
        p.join()

if __name__ == '__main__':
    run()
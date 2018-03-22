# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-18 09:24:00
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-22 12:23:05
from bs4 import BeautifulSoup

import re
import requests
import hashlib
import random
import hashlib
import time, datetime
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup

from sredis import SRedis
from logger import Logger
from mongo import Mongo
# from oss import Oss

class Filter(object):
    def __init__(self, config):
        self.config = config
        self.logger = Logger('filter', self.config.log.path)
        self.redis = SRedis(self.config, self.logger)
        self.mongo = Mongo(self.config, self.logger)
        # self.oss = Oss(self.config, 'upload-html%d' % random.randint(1,10000))

    def filter_wx_article(self, html, encoding, title=None):
        html = re.sub('<script.*?>[\s\S]+?</script>', '', html)
        html = re.sub('<style[\s\S]*?>[\s\S]+?</style>', '', html)
        html = re.sub('<link.*?>', '', html)
        html = re.sub('<iframe.*?>.*?</iframe>', '', html)

        img_tuple_list = []
        tree = BeautifulSoup(html, 'lxml')
        div = tree.find('div', class_='rich_media_content')
        if div is None:
            return None
        else:
            img_list = div.findAll('img')
            for img in img_list:
                type_ = img.get('data-type', '')
                src = img.get('data-src', '')
                if type_ and src:
                    img_tuple_list.append((src, type_))

        img_name_list = [self.get_img_name(*img_tuple) for img_tuple in img_tuple_list]
        indexes = xrange(len(img_name_list))
        html = re.sub('data-src', 'src', html)
        for index in indexes:
            img_path = img_tuple_list[index][0]
            new_img_name = img_name_list[index]
            html = html.replace(img_path, self.config.oss.url + new_img_name)
            need_download_image = "{}|{}".format(new_img_name, img_path)
            self.redis.exec_redis('sadd', 'need_handle_image', need_download_image)
        # html = re.sub('<div.*?>', '<div>', html)
        html = re.sub('<p.*?>', '<p>', html)
        html = re.sub('<br.*?/>', '', html)
        html = re.sub('<a[\s\S]*?>[\s\S]*?</a>', '', html)
        html = re.sub('<!--[\s\S]+?-->', '', html)
        html = re.sub('<body.*?>', '<body>', html)
        html = re.sub('<section[\s\S]*?>', '<section>', html)
        html = re.sub('<span[\s\S]*?>', '<span>', html)
        if isinstance(html, unicode):
            html = html.encode(encoding)
        return html

    def filter_toutiao_article(self, html, encoding, title=None):
        pattern = r'articleInfo: (\{[\s\S]+?\}),\s*?commentInfo'
        need_data = re.search(pattern, html)
        # html = html.decode(encoding)
        if need_data is None:
            return self.filter_different_toutiao_article(html, encoding, title)
        else:
            html = need_data.groups()[0].decode(encoding)
            return self.filter_office_toutiao_article(html, encoding, title)

    def filter_ifeng_article(self, html, encoding, md5, title=None):
        html = re.sub('<script.*?>[\s\S]+?</script>', '', html)
        html = re.sub('<style[\s\S]*?>[\s\S]+?</style>', '', html)
        html = re.sub('<link.*?>', '', html)
        html = re.sub('<iframe.*?>.*?</iframe>', '', html)
        encoding = 'utf8'
        if html.find('id="main_content"') != -1:
            tree = BeautifulSoup(html, 'lxml')
            title = tree.find('h1').text.encode(encoding)
            original_time = re.search(r'(\d{4}年\d{2}月\d{2}日 \d{2}:\d{2}:\d{2})', html).groups()[0]
            div = tree.find('div', id='main_content')
            body = str(div)
            html = '''
            <html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                    <title>{}</title>
                </head>
                <body>
                    <h1>{}</h1>
                    <div>
                        <div>
                            <span>{}</span>
                        </div>
                        <div>
                            {}
                        </div>
                    </div>
                </body>
            </html>'''.format(title, title, original_time, body)
            return html
        else:
            collection = self.mongo.get_collection(collection='article_big_image')
            self.mongo.remove(collection, {'content': md5})

    def filter_office_toutiao_article(self, html, encoding, title):
        title_pattern = r'title:\s*\'([\s\S]+?)\''
        content_pattern = r'content:\s*\'([\s\S]+?)\''
        subInfo_pattern = r'subInfo:\s*(\{([\s\S]+?)\})'
        source_pattern = r'source:\s*\'([\s\S]+?)\''
        time_pattern = r'time:\s*\'([\s\S]+?)\''

        parser = HTMLParser()

        title = re.search(title_pattern, html).groups()[0].encode('utf8')
        content = re.search(content_pattern, html).groups()[0]
        content = parser.unescape(content).encode('utf8')

        subInfo = re.search(subInfo_pattern, html).groups()[0]
        source = re.search(source_pattern, html).groups()[0].encode('utf8')
        time_ = re.search(time_pattern, html).groups()[0]

        collection = self.mongo.get_collection(collection='article_big_image')
        upadte_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timestamp = int(time.mktime(datetime.datetime.strptime(time_, '%Y-%m-%d %H:%M:%S').timetuple()))
        self.mongo.update(collection, {'$set': {'update_at': upadte_time, 'original_time': timestamp}}, {'title': title})
        store_html = '''<html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <title>{}</title>
            </head>
            <body>
                <h1>{}</h1>
                <div>
                    <div>
                        <span>{}</span><span>{}</span>
                    </div>
                    <div>
                        {}
                    </div>
                </div>
            </body>
        </html>'''.format(title, title, source, time_, content)

        return store_html


    def filter_different_toutiao_article(self, html, encoding, title):
        return html

    def get_img_name(self, img, type_):
        to_sign = "{}{}".format(img, random.randint(1,1000))
        md5_sign = hashlib.md5(to_sign).hexdigest()
        img_name = "image/weixin-{}.{}".format(md5_sign, type_)
        return img_name

if __name__ == '__main__':
    from config import Config
    conf = Config('/Users/gonglingxiao/Graduation_Project/spider/spider.ini')
    f = Filter(conf)
    html = requests.get('http://mp.weixin.qq.com/s?src=11&timestamp=1514347937&ver=599&signature=ADLLAKM3k6juoN32QVOg0winyQ0HTM5FkmwtqeDFF9TC*MKkih7rDnLuCIBdJuYqMGeErImP7t97WOLtHCTQ7wlOxr6GIxbUoiayNgUHfZ76p8qEBmGIQqItFiyh*wQ4&new=1').text
    html = f.filter_wx_article(html, 'utf8')
    with open('/Users/gonglingxiao/test_test.html', 'w') as w:
        w.write(html)

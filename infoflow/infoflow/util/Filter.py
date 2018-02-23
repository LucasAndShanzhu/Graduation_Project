# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-18 09:24:00
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-02-23 19:32:39
from bs4 import BeautifulSoup

import re
import requests
import hashlib
import random
import hashlib

from sredis import SRedis
from logger import Logger
# from oss import Oss

class Filter(object):
    def __init__(self, config):
        self.config = config
        self.logger = Logger('filter', self.config.log.path)
        self.redis = SRedisClient(self.logger)
        # self.oss = Oss(self.config, 'upload-html%d' % random.randint(1,10000))

    def filter_wx_article(self, html, encoding, title=None):
        html = re.sub('<script.*?>[\s\S]+?</script>', '', html)
        html = re.sub('<style[\s\S]*?>[\s\S]+?</style>', '', html)
        html = re.sub('<link.*?>', '', html)
        html = re.sub('<iframe.*?>.*?</iframe>', '', html)

        img_tuple_list = []
        tree = BeautifulSoup(html, 'lxml')
        div = tree.find('div', id='img-content')
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

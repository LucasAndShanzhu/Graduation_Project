# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-01-26 19:06:31
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-23 10:49:00

import base64
import urllib, time, datetime
import json, re, random
from hashlib import md5
from urllib2 import urlparse
from bs4 import BeautifulSoup

from scrapy.spiders import Rule
from scrapy.http import Request
from infoflow.items import ArticleBigImageItem

from ..util import util
from .base import BaseSpider

conf = util.conf
uredis = util.uredis

class QingboWX(BaseSpider):
    name = "qingboWx"

    BASE_URL = 'http://www.gsdata.cn/rank/ajax_wxarc?post_time=2&page={}&types={}&industry={}&proName={}'
    LOGIN_URL = 'http://www.gsdata.cn/member/login'

    TAG_WXARC = r'tag_wxarc\((.*?)\)'
    download_delay = 4

    LOGIN_DATA = {
        'username': 18007383655,
        'password': 'glx1997',
        'remember': 1
    }

    LOGIN_HEADERS = {
        'Referer': 'http://www.gsdata.cn/member/login',
        'Host': 'www.gsdata.cn',
        'User-Agent': util.get_user_agent()
    }

    TYPE_LIST = ['政务','时事','文化','生活','健康','美食','时尚','旅行','母婴','科技','创业','职场','娱乐','搞笑','动漫','游戏','体育','汽车','金融','房产','教育','民生','企业']
    TAG_LIST = ['govement', 'event', 'culture', 'life', 'health', 'food', 'fashion', 'travel', 'baby', 'science', 'pioneer', 'workplace', 'entertain', 'joke', 'anime', 'game', 'sports', 'cars', 'economic', 'house', 'education', 'livelihood', 'company']
    AREA_TYPE_LIST = ['政务']

    @staticmethod
    def need_proxy():
        return False

    def init(self):
        TYPE_TAG_TABLE = dict(zip(QingboWX.TYPE_LIST, QingboWX.TAG_LIST))
        setattr(QingboWX, 'TYPE_TAG_TABLE', TYPE_TAG_TABLE)

        #正则匹配模式.
        pattern = re.compile(QingboWX.TAG_WXARC)
        setattr(QingboWX, 'TAG_WXARC', pattern)

        province_city = util.get_province_city()
        setattr(QingboWX, 'PROVINCE_CITY', province_city)

    def _verfi(self, html):
        verfi = False
        try:
            data = json.loads(html)
            if int(data['error']) == 0: 
                verfi = True
        except Exception as e:
            pass
        return verfi

    def _get_headers(self, url):
        headers = {
            'Host': util.get_host(url),
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'http://www.gsdata.cn/rank/wxarc'
        }
        cookie = util.login(QingboWX.LOGIN_URL, QingboWX.LOGIN_DATA, headers=QingboWX.LOGIN_HEADERS)
        headers['Cookie'] = cookie
        return headers

    def start_requests(self):
        headers = self._get_headers(QingboWX.BASE_URL)
        import requests
        res = requests.get("http://www.gsdata.cn/rank/wxarc")
        for type_ in QingboWX.TYPE_TAG_TABLE:
            for page in xrange(1, 5):
                url = QingboWX.BASE_URL.format(page, urllib.quote(type_), 'all', '')
                request = Request(url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)
                yield Request(url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)

        # for type_ in QingboWX.TYPE_TAG_TABLE:
        #     if type_ in QingboWX.AREA_TYPE_LIST:
        #         for province, citys in QingboWX.PROVINCE_CITY.items():
        #             for city in citys:
        #                 for page in xrange(1, 5):
        #                     url = QingboWX.BASE_URL.format(page, urllib.quote(type_), urllib.quote(city), urllib.quote(province))
        #                     print url
        #                     request = Request(url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)
        #                     yield Request(url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)

    def _parse(self, html, url, encoding, status_code):
        parse_result = urlparse.urlparse(url)
        params = urlparse.parse_qs(parse_result.query)
        item_type = params['types'][0]
        proName = params.get('proName', '')
        province = proName[0] if proName else 'all'
        city = params['industry'][0]
        response_data = json.loads(html)
        error = int(response_data['error'])
        if error != 0:
            yield None
        else:
            show_html = response_data['data']
            tree = BeautifulSoup(show_html, 'lxml')
            tr_list = tree.find_all('tr')
            for tr in tr_list:
                td_list = tr.find_all('td')
                overall_data = td_list[-1].a.get('onclick')
                read_num = td_list[2].get_text()
                read_num = self._get_abstract_num(read_num)
                like_num = td_list[3].get_text()
                like_num = self._get_abstract_num(like_num)
                try:
                    tag_wxarc = QingboWX.TAG_WXARC.search(overall_data).groups()[0].split(',')[1:]
                    item_url = tag_wxarc[0][1:-1]
                    title = util.get_utf8_str(tag_wxarc[1][1:-1], encoding)
                    source = tag_wxarc[2][1:-1]
                    source_detail = util.get_utf8_str(tag_wxarc[3][1:-1], encoding)
                    original_time = tag_wxarc[4][1:-1]
                    tag = QingboWX.TYPE_TAG_TABLE[item_type]
                    key = "{}#{}".format(title, source)
                    md5_key = md5(key).hexdigest()
                    item = self._get_item(title, source, source_detail, item_url, original_time, province, city, like_num, read_num, tag, md5_key)
                    yield item
                except Exception:
                    yield None
                    
    def _get_item(self, title, source, source_detail, url, original_time, province, city, like_num, read_num, tag, md5):
        item = ArticleBigImageItem()
        item['title'] = title
        item['source'] = source
        item['source_detail'] = source_detail
        item['url'] = url
        item['original_time'] = original_time
        item['province'] = province
        item['city'] = city
        item['like_num'] = like_num
        item['read_num'] = read_num
        item['comment_num'] = 0
        item['tag'] = tag
        item['md5'] = md5
        item['image'] = []
        item['channel'] = 'wechat'
        item['spider_source'] = 'qingbo'
        item['forward_num'] = 0
        return item

    def _get_abstract_num(self, amount):
        abstract_num = 0
        try:
            if amount.endswith('W+'):
                start = int(amount[:-2]) * 10000
                end =  int(amount[:-2]) * 100000
                abstract_num = random.randint(start, end)
            else:
                abstract_num = int(amount)
        except Exception as e:
            abstract_num = 0
        return abstract_num

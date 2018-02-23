# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-02-22 19:28:11
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-02-23 19:28:00

import time, re
import json

from scrapy.spiders import Rule
from scrapy.http import Request
from infoflow.items import ArticleBigImageItem
from hashlib import md5

from .base import BaseSpider
from ..util import util

ulogger = util.ulogger
conf = util.conf
uredis = util.uredis
mysql = util.mysql

class ToutiaoSpider(BaseSpider):
    driver = None
    name = 'toutiao'
    BASE_URL = 'https://www.toutiao.com/api/pc/feed/?category={}&utm_source=toutiao&widen=1&max_behot_time={}&max_behot_time_tmp={}&tadrequire=true&as=A185DA485F8948B&cp=5A8FD9A4A8DB1E1&_signature=uHkeRQAA4wNgfEZfXersxbh5Hl'
    URL_PREFIX = 'https://www.toutiao.com'

    tag_click_list = ['news_hot', 'news_tech', 'news_entertainment', 'news_game', 'news_sports', 'news_car', 'news_finance', 'funny', 'news_military', 'news_fashion', 'news_discovery', 'news_regimen', 'news_history', 'news_world', 'news_travel', 'news_baby', 'news_essay', 'news_food']
    tag_transform_table = {
        u'财经': u'金融', 
        u'养生': u'健康', 
        u'国际': u'时事', 
        u'时政': u'时事', 
        u'旅游': u'旅行',
        u'育儿': u'母婴'
    }

    cookie = None
    category_pattern = r'category=([\s\S]+?)\&' 
    category_cpattern = None
    load_nums = None

    download_delay = 5

    def init(self):
        if ToutiaoSpider.cookie is None:
            ToutiaoSpider.cookie = util.get_cookie('https://www.toutiao.com/ch/news_hot/')
        ToutiaoSpider.category_cpattern = re.compile(ToutiaoSpider.category_pattern)
        ToutiaoSpider.load_nums = dict(zip(ToutiaoSpider.tag_click_list, [0] * len(ToutiaoSpider.tag_click_list)))
        self.mysql = mysql.get_db('graduation_project')

    def _get_headers(self, url):
        headers = {
            'User-Agent': self._get_user_agent(),
            'Referer': 'https://www.toutiao.com/',
            'cookie': ToutiaoSpider.cookie,
            'x-requested-with': 'XMLHttpRequest',
        }
        return headers

    def _verfi(self, html):
        try:
            response_data = json.loads(html)
            return True
        except Exception as e:
            ulogger.error()
            return False

    def _close(self):
        self.mysql.close()

    def start_requests(self):
        for tag_click in ToutiaoSpider.tag_click_list:
            url = ToutiaoSpider.BASE_URL.format(tag_click, 0, 0)
            headers = self._get_headers(url)
            request = Request(url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)
            yield request
            break

    def _parse(self, html, url, encoding, status_code):
        tag_click = None
        try:
            tag_click = ToutiaoSpider.category_cpattern.search(url).groups()[0]
        except Exception as e:
            pass
        data = json.loads(html)
        if data['message'] == 'success':
            item_list = data['data']
            last_hot_time = None
            for item in item_list:
                if item['article_genre'] == 'article':
                    chinese_tag = item.get('chinese_tag', u'其他')
                    if chinese_tag in ToutiaoSpider.tag_transform_table:
                        chinese_tag = ToutiaoSpider.tag_transform_table[chinese_tag]
                    chinese_tag = chinese_tag.encode('utf8')
                    if not self._judge_tag(chinese_tag):
                        chinese_tag = u'其他'.encode('utf8')
                    source = item['source'].encode('utf8')
                    title = item['title'].encode('utf8')
                    comment_num = item['comments_count']
                    url = ToutiaoSpider.URL_PREFIX + item['source_url']
                    behot_time = int(item['behot_time'])
                    cover = item.get('media_avatar_url', [])
                    if cover and not cover.startswith('https'):
                        cover = ['https:' + cover]
                    detail = item['abstract'].encode('utf8')
                    article_item = ArticleBigImageItem()
                    article_item['title'] = title
                    article_item['detail'] = detail
                    article_item['source'] = article_item['source_detail'] = source
                    article_item['channel'] = 'toutiao'
                    article_item['spider_source'] = 'toutiao_web'
                    article_item['url'] = url
                    article_item['comment_num'] = comment_num
                    article_item['tag'] = chinese_tag
                    key = "{}#{}".format(title, source)
                    md5_str = md5(key).hexdigest()
                    article_item['md5'] = md5_str
                    article_item['image'] = cover
                    yield article_item
                    last_hot_time = behot_time
            max_load_num = 15
            if tag_click and tag_click == 'news_hot':
                max_load_num = 1
            if last_hot_time is not None and tag_click is not None and ToutiaoSpider.load_nums[tag_click] < max_load_num:
                url = ToutiaoSpider.BASE_URL.format(tag_click, last_hot_time, last_hot_time)
                request = Request(url, callback=self.parse, errback=self._error_handle, headers=self._get_headers(url), dont_filter=True)
                ToutiaoSpider.load_nums[tag_click] += 1
                yield request

    def _judge_tag(self, tag):
        self.mysql.ping()
        cursor = self.mysql.cursor()
        sql = "select id from topic where chs_name=%s"
        result = cursor.execute(sql, tag)
        if result == 0:
            return False
        return True
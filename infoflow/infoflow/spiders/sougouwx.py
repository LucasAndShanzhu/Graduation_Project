# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-02-11 15:17:34
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-19 14:18:02
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

ulogger = util.ulogger
conf = util.conf
uredis = util.uredis
mysql = util.util_mysql

class SougouWX(BaseSpider):
    name = "sougouWx"
    VERIFY = '<div class="img-box">'
    download_delay = 4

    Cookie = util.get_cookie('https://www.sogou.com/web?query=')
    BASE_URL = 'http://weixin.sogou.com/pcindex/pc/pc_{}/{}.html'

    def init(self):
        self.topic_list = ['热门', '搞笑', '健康', '私房话', '娱乐', '科技', '金融', '汽车', '生活', '时尚', '母婴', '旅行', '职场', '美食', '历史', '教育', '星座', '体育', '军事', '游戏', '宠物']
        self.tag_list = ['hot', 'joke', 'health', 'private', 'entertain', 'science', 'economic', 'cars', 'life', 'fashion', 'baby', 'travel', 'workplace', 'food', 'history', 'education', 'constellation', 'sports', 'military', 'game', 'pet']
        self.tag_topic_list = dict(zip(self.topic_list, self.tag_list))
        self.page_pattern = re.compile(r'.*?/pc/pc_\d+?/(.+?)\.html')
        self.itype_pattern = re.compile(r'.*?/pc/pc_(\d+?)/.+')

    def _get_headers(self, url):
        headers = {
            'User-Agent': self._get_user_agent(),
            'Referer': 'http://weixin.sogou.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'Host': util.get_host(url),
            'Cookie': SougouWX.Cookie
        }
        return headers

    def start_requests(self):
        length = len(self.topic_list)
        for index in xrange(1, length):
            url = SougouWX.BASE_URL.format(index, 'pc_%d' % index)
            headers = self._get_headers(url)
            request = Request(url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)
            yield request
            for page in xrange(1, 5):
                url = SougouWX.BASE_URL.format(index, page)
                headers = self._get_headers(url)
                request = Request(url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)
                yield request

    def _parse(self, html, url, encoding, status_code):

        tree = BeautifulSoup(html, 'lxml')
        li_list = tree.find_all('li')
        page_str = re.search(self.page_pattern, url).groups()[0]
        page = 0
        itype = self.topic_list[int(re.search(self.itype_pattern, url).groups()[0])]
        try:
            page = int(page_str)
        except :
            pass
        for li in li_list:
            try:
                item = ArticleBigImageItem()
                img_box = li.find('div', class_='img-box')
                header_a =img_box.find('a')
                item_url = header_a.get('href')
                icon = header_a.find('img').get('src')
                txt_box = li.find('div', class_='txt-box')
                title = txt_box.find('h3').find('a').get_text().encode(encoding)
                body = txt_box.find('p', class_='txt-info')
                detail = body.get_text()
                tail_div = txt_box.find('div', class_='s-p')
                timestamp = int(tail_div.get('t'))
                original_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                account_a = tail_div.find('a', class_='account')
                source = account_a.get_text().encode(encoding);
                item['title'] = title
                item['source'] = item['source_detail'] = source
                item['url'] = item_url
                item['original_time'] = original_time
                item['image'] = [icon]
                item['tag'] = itype
                item['channel'] = 'wechat'
                item['spider_source'] = 'sougou'
                key = "{}#{}".format(title, source)
                md5_key = md5(key).hexdigest()
                item['md5'] = md5_key
                yield item
            except Exception as e:
                ulogger.error()
                yield None

    def _get_like_num(self, page):
        page
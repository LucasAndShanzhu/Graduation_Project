# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-03-14 18:11:07
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-23 10:49:30

# 军事（滚动）:16874      /16874/1/list.shtml (第一页)     http://news.ifeng.com/listpage/
# 古代史: 4764 同上      /16874/2/1/56638250(第一页最后一个元素坐标)/list.shtml     
# 近代史: 4763 同上      /16874/3/1/56528035(第二页做后一个)/56637218(第二页第一个)/list.shtml
# 世界史: 4765 同上
# 
#大陆新闻 : 11528   /11528/0(20180314： 0代表当日, 而20180314代表前几日)/1(第几页)rtlist.shtml 爬去前一天的数据.             

# 文化: 59669           http://culture.ifeng.com/listpage/59669/1/list.shtml
#                      http://culture.ifeng.com/listpage/59669/3/1/55277000/55861152/list.shtml

# 数码: 817             http://digi.ifeng.com/listpage/817/1/list.shtml 
#                      http://digi.ifeng.com/listpage/817/2/list.shtml?cflag=1&cursorId=44907352
#                      http://digi.ifeng.com/listpage/817/3/list.shtml?cflag=1&prevCursorId=44907369(第一个)&cursorId=44907342(第二个)

# 明星: 3          http://ent.ifeng.com/listpage/3/3(第三页 只需更改此处)/list.shtml
# 电影: 44169      http://ent.ifeng.com/listpage/44169/4(第四页， 只改此处)/list.shtml
# 健康: 5545       http://fashion.ifeng.com/listpage/5545/5(第五页，只需改此处)/list.shtml
# 两性: 2866       http://fashion.ifeng.com/listpage/2866/3/list.shtml

# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-02-22 19:28:11
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-02-24 14:49:14

import time, re
import datetime
import json

from scrapy.spiders import Rule
from scrapy.http import Request
from infoflow.items import ArticleBigImageItem
from hashlib import md5
from bs4 import BeautifulSoup

from .base import BaseSpider
from ..util import util

conf = util.conf
uredis = util.uredis
mysql = util.mysql

class IFengSpider(BaseSpider):
    driver = None

    DIV_CLASS = {
        'col_L': ['news', 'culture', 'technology', 'fashion'],
        'newsList': ['health', 'mainth']
    }

    name = 'ifeng'
    LONGEST_TIME = 1800

    FLAG_TABLE = { 
        'news': [16874, 4763, 4764, 4765], 
        'culture': [59669], 
        'technology': [817], 
        'fashion': [3, 44169],
        'health': [2866, 5545],
        'mainth': [11528]
    }

    TAG_TABLE = {
        16874: u'军事', 4763: u'历史', 4764: u'历史', 4765: u'历史',
        59669: u'文化', 817: u'科技', 11528: u'大陆',
        3: u'娱乐', 44169: u'传媒', 5545: u'健康', 2866: u'健康'
    }

    BASE_URL_TABLE = {
        'news': 'http://news.ifeng.com/listpage/',
        'culture': 'http://culture.ifeng.com/listpage/',
        'technology': 'http://digi.ifeng.com/listpage/',
        'fashion': 'http://ent.ifeng.com/listpage/',
        'health': 'http://fashion.ifeng.com/listpage/',
        'mainth': 'http://news.ifeng.com/listpage/',
    }

    VERIFY = '<div class="h_mainNavNew cDGray h_mainNav" id="f-header">'

    cookie = None
    category_pattern = r'category=([\s\S]+?)\&' 
    category_cpattern = None
    load_nums = None

    download_delay = 5

    def init(self):
        IFengSpider.cookie = util.get_cookie('http://www.ifeng.com/')

    def _get_headers(self, url):
        headers = {
            'User-Agent': util.get_user_agent(),
            'Referer': 'http://www.ifeng.com/',
            'cookie': IFengSpider.cookie,
            'Upgrade-Insecure-Requests': '1',
        }
        return headers

    def _create_url(self, section, flag, front=0, end=0, page=1, date=""):
        base_url = IFengSpider.BASE_URL_TABLE[section]
        if section in ['news', 'culture'] :
            if front == 0:
                return "{}{}/1/list.shtml".format(base_url, flag)
            elif end == 0:
                return "{}{}/2/1/{}/list.shtml".format(base_url, flag, front)
            else:
                return "{}{}/{}/1/{}/{}/list.shtml".format(base_url, flag, page, front, end)
        elif section in ['fashion', 'health']:
            return "{}{}/{}/list.shtml".format(base_url, flag, page)
        elif section == 'technology':
            if front == 0:
                return "{}{}/{}/list.shtml".format(base_url, flag, page)
            elif end == 0:
                return "{}{}/{}/list.shtml?cflag=1&cursorId={}".format(base_url, flag, page, front)
            else:
                return "{}{}/{}/list.shtml?cflag=1&prevCursorId={}&cursorId={}".format(base_url, flag, page, front, end)
        else:
            yesterday = datetime.datetime.now() + datetime.timedelta(days=1)
            yesterday = yesterday.strftime('%Y%m%d')
            return "{}{}/{}/1/rtlist.shtml".format(base_url, flag, yesterday)

    def _get_section_from_url(self, url):
        url_list = url.split('/')
        url_prefix = '/'.join(url_list[:4]) + '/'
        flag = int(url_list[4])
        section = self._get_section(url_prefix, flag)
        return section


    def _get_section(self, url_prefix, flag):
        return [sec for (sec, prefix) in IFengSpider.BASE_URL_TABLE.items() if prefix == url_prefix and flag in IFengSpider.FLAG_TABLE[sec]][0]

    def start_requests(self):
        for section in IFengSpider.BASE_URL_TABLE:
            flag_table = IFengSpider.FLAG_TABLE[section]
            for flag in flag_table:
                url = self._create_url(section, flag)
                headers = self._get_headers(url)
                request = Request(url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)
                yield request

    def _parse(self, html, url, encoding, status_code):
        section = self._get_section_from_url(url)
        tree = BeautifulSoup(html, 'lxml')
        url_list = url.split('/')
        flag = int(url_list[4])
        tag = IFengSpider.TAG_TABLE[flag].encode('utf-8')
        firstId = lastId = 0
        if section in IFengSpider.DIV_CLASS['col_L']:
            page = int(url_list[5])
            data_div = tree.find('div', class_='col_L')
            box_list = data_div.find_all('div', class_='box_list')
            for box in box_list:
                item = ArticleBigImageItem()
                title = box.h2.a.text.encode('utf-8')
                item_url = box.h2.a.get('href')
                cover = ''
                try:
                    cover = box.find('div', class_='box_pic').a.img.get('src')
                except Exception as e:
                    pass
                detail_div = box.find('div', class_='box_txt')
                detail = detail_div.p.text.encode('utf-8')
                origin_time = detail_div.span.text.encode('utf-8')
                comment_num = int(box.find('em', class_='js_cmtNum').text)
                source = 'ifeng'
                source_detail = '凤凰网'
                md5_key = md5("{}#{}".format(title, source)).hexdigest()
                item['title'] = title
                item['detail'] = detail
                item['url'] = item_url
                item['image'] = [cover] if cover != '' else []
                item['source'] = source
                item['source_detail'] = source_detail
                item['spider_source'] = 'ifeng'
                item['original_time'] = origin_time
                item['md5'] = md5_key
                item['tag'] = tag
                item['channel'] = 'ifeng'
                item['comment_num'] = comment_num
                yield item
                if firstId == 0:
                    itemIdLine = item_url.split('/')[-1]
                    firstId = int(itemIdLine.split('_')[0])
            if len(box_list) > 0 and section != 'fashion' and lastId == 0  and page <= 4:
                itemIdLine = item_url.split('/')[-1]
                lastId = int(itemIdLine.split('_')[0])
                next_url = ''
                if page == 1:
                    next_url = self._create_url(section, flag, front=lastId, page=page + 1)
                else:
                    page += 1
                    if section != 'technology':
                        next_url = self._create_url(section, flag, lastId, firstId, page)
                    else:
                        next_url = self._create_url(section, flag, firstId, lastId, page)
                headers = self._get_headers(next_url)
                yield Request(next_url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)
            if section == 'fashion' and page <= 4:
                page += 1
                next_url = self._create_url(section, flag, page=page)
                headers = self._get_headers(next_url)
                yield Request(next_url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)

        elif section in IFengSpider.DIV_CLASS['newsList']:
            data_div = tree.find('div', class_='newsList')
            if data_div is not None:
                ul_list = data_div.find_all('ul')
                firstId = lastId = 0
                for ul in ul_list:
                    li_list = ul.find_all('li')
                    for li in li_list:
                        item = ArticleBigImageItem()
                        title = li.a.text.encode('utf-8')
                        item_url = li.a.get('href')
                        original_time = li.h4.text
                        original_time = self._get_original_time(original_time)
                        source = 'ifeng'
                        source_detail = '凤凰网'
                        md5_key = md5("{}#{}".format(title, source)).hexdigest()
                        item['title'] = title
                        item['detail'] = title
                        item['url'] = item_url
                        item['image'] = []
                        item['source'] = source
                        item['source_detail'] = source_detail
                        item['original_time'] = original_time
                        item['spider_source'] = 'ifeng'
                        item['md5'] = md5_key
                        item['tag'] = tag
                        yield item
                        if firstId == 0:
                            itemIdLine = item_url.split('/')[-1]
                            firstId = int(itemIdLine.split('_')[0])
                if section == 'health':
                    page = int(url_list[5]) + 1
                    if page <= 4:
                        next_url = self._create_url(section, flag, page=page)
                        headers = self._get_headers(next_url)
                        yield Request(next_url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)
                elif section == 'mainth':
                    date = url_list[5]
                    page = int(url_list[6]) + 1
                    if page <= 4:
                        next_url = self._create_url(section, flag, page=page+1, date=date)
                        headers = self._get_headers(next_url)
                        yield Request(next_url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)
            else:
                pass
        else:
            pass

    def _get_original_time(self, original_time):
        original_time_timetuple = time.strptime(original_time, '%m/%d %H:%M')
        original_time = datetime.datetime(2018, original_time_timetuple.tm_mon, original_time_timetuple.tm_mday, original_time_timetuple.tm_hour, original_time_timetuple.tm_min, original_time_timetuple.tm_sec)
        if original_time.timetuple() > datetime.datetime.now().timetuple():
            original_time = datetime.datetime(2017, original_time_timetuple.tm_mon, original_time_timetuple.tm_mday, original_time_timetuple.tm_hour, original_time_timetuple.tm_min, original_time_timetuple.tm_sec)
        return time.strftime('%Y-%m-%d %H:%M:%S', original_time.timetuple())

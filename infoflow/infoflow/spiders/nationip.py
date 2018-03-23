# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-01-23 17:34:01
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-23 10:48:47
import base64

from scrapy.spiders import Rule
from scrapy.http import Request
from infoflow.items import IpItem
from bs4 import BeautifulSoup

from ..util import util
from .base import BaseSpider

conf = util.conf
uredis = util.uredis

class NationipSpider(BaseSpider):
    name = 'nationip'

    VERIFY = '<table id="ip_list">'
    BASE_URL = "http://www.xicidaili.com/wn/{}"

    _IP = 1
    _PORT = 2
    _SPEED = 6
    _LINK_SPEED = 7
    _LIFE = 8
    _VERIFY_TIME = 9

    def _get_headers(self, url):
        headers = {}
        headers['Referer'] = "http://www.xicidaili.com/wn/"
        headers['Host'] = util.get_host(url)
        return headers

    def start_requests(self):
        headers = self._get_headers(NationipSpider.BASE_URL)
        for i in xrange(5):
            user_agent = util.get_user_agent()
            index = i if i > 0 else ''
            url = NationipSpider.BASE_URL.format(index)
            request = Request(url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)
            yield request

    def _parse(self, html, url, encoding, status_code):
        tree = BeautifulSoup(html, 'lxml')
        table = tree.find('table', id='ip_list')
        tr_list = table.find_all('tr')[1:]
        for tr in tr_list:
            td_list = tr.find_all('td')
            ip = td_list[NationipSpider._IP].get_text().strip()
            port = td_list[NationipSpider._PORT].get_text().strip()
            item = IpItem()
            item['ip'] = ip
            item['port'] = port
            yield item
# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-01-22 20:46:28
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-02-11 14:38:49

import json
import base64
import codecs

from scrapy.spiders import Rule
from scrapy.http import Request
from infoflow.items import IpItem
from bs4 import BeautifulSoup

from ..util import util
from .base import BaseSpider

ulogger = util.ulogger
conf = util.conf
uredis = util.uredis

class ForeignipSpider(BaseSpider):
    name = "foreignip"

    VERIFY = '<form action="/proxies/http_proxy_list"'
    BASE_URL = "https://www.cool-proxy.net/proxies/http_proxy_list/{}"

    def _get_headers(self, url):
        headers = {
            'Host': util.get_host(url),
            'Referer': 'https://www.cool-proxy.net/proxies/http_proxy_list/'
        }
        return headers

    def start_requests(self):
        headers = self._get_headers(ForeignipSpider.BASE_URL)
        for i in xrange(10):
            user_agent = util.get_user_agent()
            append = 'page:{}'.format(i) if i else ''
            url = ForeignipSpider.BASE_URL.format(append)
            request = Request(url, callback=self.parse, errback=self._error_handle, headers=headers, dont_filter=True)
            yield request

    def _parse(self, html, url, encoding, status_code):
        tree = BeautifulSoup(html, 'lxml')
        table = tree.find('div', id='main').table
        tr_list = table.find_all('tr')[1:]
        for tr in tr_list:
            td_list = tr.find_all('td')
            if len(td_list) < 8:
                continue
            b64_ip = td_list[0].script.get_text()
            ip_left = b64_ip.find('"') + 1
            ip_right = b64_ip.rfind('"')
            b64_ip = b64_ip[ip_left : ip_right]
            b64_ip = codecs.encode(b64_ip, 'rot_13')
            ip = base64.b64decode(b64_ip)
            port = td_list[1].get_text()
            item = IpItem()
            item['ip'] = ip
            item['port'] = port
            yield item
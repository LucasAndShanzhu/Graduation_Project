# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-01-23 12:16:17
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-23 10:48:24
import json

from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from infoflow.items import IpItem

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from ..util import util

conf = util.conf
uredis = util.uredis
mysql = util.mysql

class BaseSpider(CrawlSpider):
    def __init__(self, *a, **kw):
        super(BaseSpider, self).__init__(*a, **kw)
        self.retry_nums = {}
        self.init()

    #如果需要js操作设置返回true
    @staticmethod
    def js_parse():
        return False

    #需要初始化则重写此函数.
    def init(self):
        pass

    def _get_user_agent(self):
        return util.get_user_agent()

    #如果不需要代理则将此设为False.
    @staticmethod
    def need_proxy():
        return True

    #设置访问headers，需要重写.
    def _get_headers(self, url):
        return {}

    #设置获取页面验证方式.
    def _verfi(self, html):
        return html.find(self.VERIFY) != -1

    #解析页面.
    def _parse(self, html, url, encoding, status_code):
        yield None

    #资源回收处理.
    def _close(self):
        pass

    def _error_handle(self, failure):
        request = failure.request
        if failure.check(TimeoutError):
            url = request.url
            if not self.retry_nums.has_key(url):
                self.retry_nums[url] = 0
            if not self.retry_nums[url] > 3:
                print url, self.retry_nums[url]
                self.retry_nums[url] += 1
                return Request(request.url, callback=self.parse, errback=self._error_handle, dont_filter=True, headers=self._get_headers(request.url))
        elif failure.check(HttpError):
            response = failure.value.response
            url = response.url
            code = response.status
            if code == 404:
                pass
            elif code == 500:
                if not self.retry_nums.has_key(url):
                    self.retry_nums[url] = 0
                if self.retry_nums[url] > 3:
                    pass
                else:
                    self.retry_nums[url] += 1
                    return Request(request.url, callback=self.parse, errback=self._error_handle, headers=self._get_headers(request.url), dont_filter=True)
            elif code == 302 or code == 403 or code == 503:
                if self.need_proxy():
                    return Request(request.url, callback=self.parse, errback=self._error_handle, headers=self._get_headers(request.url), dont_filter=True)
            else:
                pass
        elif failure.check(DNSLookupError):
            url = failure.request.url

    def parse(self, response):
        html = response.body
        url = response.url
        encoding = response.encoding
        status_code = response.status
        if not self._verfi(html):
            if hasattr(self, 'VERIFY'):
                print html.find(self.VERIFY), self.VERIFY, html
            if self.need_proxy():
                request = Request(url, callback=self.parse, errback=self._error_handle, headers=self._get_headers(url), dont_filter=True)
                yield request
            else:
                yield None
        else:
            for item in self._parse(html, url, encoding, status_code):
                yield item

    def closed(self, reason):
        try:
            mysql.close()
        except:
            pass
        self._close()
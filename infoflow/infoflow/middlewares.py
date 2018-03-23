# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from util import util

conf = util.conf
uredis = util.uredis

from scrapy import signals
from scrapy.exceptions import CloseSpider

class ProxySpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.
    USER_AGENT = None

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        if spider.need_proxy():
            ip = uredis.exec_redis('spop', conf.pool.pool)
            if ip is None:
                raise CloseSpider("ip is None, stop immediately")                
            request.meta['proxy'] = "http://" + ip
            uredis.exec_redis('sadd', conf.pool.verify_pool, ip)

        user_agent = ''

        if ProxySpiderMiddleware.USER_AGENT is None:
            user_agent = util.get_user_agent()
            ProxySpiderMiddleware.USER_AGENT = user_agent
        else:
            user_agent = ProxySpiderMiddleware.USER_AGENT
        request.headers.setdefault('User-Agent', user_agent)
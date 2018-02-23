# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-01-23 19:27:31
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-02-23 15:08:44

import sys, os
import time
path = os.getcwd() + '/..'
sys.path.append(path)

from selenium import webdriver
from bs4 import BeautifulSoup
from base64 import b64decode

from ..util import util

class ProxydbIpSpider(object):
    name = "proxydbIp"

    VERIFY = '<table class="table table-sm table-hover">'

    BASE_URL = 'http://proxydb.net/?protocol=https&country={}'

    SLEEP_TIME = 2


    def __init__(self):
        self.webdriver = webdriver.PhantomJS()
        self.redis = util.uredis
        self.conf = util.conf
        self.logger = util.ulogger

    def start_requests(self):
        for i in range(0, 7):
            index = '&offset={}'.format(15 * i) if i != 0 else ''
            url = ProxydbIpSpider.BASE_URL.format(index)
            yield url

    def get_html(self, url):
        self.webdriver.get(url)
        return self.webdriver.page_source

    def parse(self, html):
        tree = BeautifulSoup(html, 'lxml')
        div = tree.find('div', class_='table-responsive')
        tbody = div.find('tbody')
        tr_list = tbody.find_all('tr')
        for tr in tr_list:
            td = tr.find('td')
            ip_a = td.find('a')
            ip = ip_a.get_text()
            self.redis.exec_redis('sadd', self.conf.pool.verify_pool, ip)

    def run(self):
        try:
            for url in self.start_requests():
                html = self.get_html(url)
                self.parse(html)
                time.sleep(ProxydbIpSpider.SLEEP_TIME)
        except Exception as e:
            print e
        finally:
            self.webdriver.quit()

if __name__ == '__main__':
    proxydb = ProxydbIpSpider()
    proxydb.run()
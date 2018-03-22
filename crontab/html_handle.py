# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-26 10:12:06
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-22 11:11:56
import os
dir_path = os.getcwd() + '/../common'
import sys
sys.path.append(dir_path)

from redis import Redis
import requests
import threading
import time
import random
import multiprocessing

from oss import Oss
from config import Config
from Filter import Filter

redis_args = {
    'host': '127.0.0.1',
    'password': 'glx1997'
}

redis = Redis(**redis_args)
processes = []

def run():
    global processes
    config = Config('setting.ini')
    for i in range(2):
        process = multiprocessing.Process(target=process_run, args=(config,))
        processes.append(process)
        process.start()
    signal.signal(signal.SIGTERM, quit)
    for p in processes:
        p.join()

def process_run(config):
    threadings = []
    for i in range(4):
        thread = threading.Thread(target=thread_run, args=(config,))
        threadings.append(thread)
        thread.start()
    for t in threadings:
        t.join()

def thread_run(config):
    rand_num = random.randint(1,100)
    html = redis.spop('need_parsed_html')
    oss = Oss(config, 'upload-html%d' % rand_num)
    s_filter = Filter(config)
    while True:
        if html is None:
            time.sleep(1)
            html = redis.spop('need_parsed_html')
            continue;
        else:
            try:
                html_parts = html.split('|') 
                html_name = 'html/{}'.format(html_parts[0])
                html_source = html_parts[1]
                html_path = html_parts[2]
                res = download(html_path, html_source)
                if res is None:
                    raise Exception('download html %s failure' % html_path)
                html_content = res.content
                html_encoding = res.encoding
                if html_source.endswith('wx'):
                    html_content = s_filter.filter_wx_article(html_content, html_encoding)
                    if html_content is None:
                        raise Exception('the {} may be failed'.format(''))
                if html_source == 'toutiao':
                    html_content = s_filter.filter_toutiao_article(html_content, html_encoding)
                if html_source == 'ifeng':
                    html_content = s_filter.filter_ifeng_article(html_content, html_encoding, html_parts[0])
                try:
                    oss.upload('spider-lucas', html_name, html_content)
                except Exception as e:
                    del oss
                    oss = Oss(config, 'upload-html%d' % rand_num)
            except Exception as e:
                print e
            finally:
                html = redis.spop('need_parsed_html')
                time.sleep(1)

def download(url, html_source):
    try:
        res = None
        if html_source == 'toutiao':
            headers = {
                'referer': 'https://www.toutiao.com/', 
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
            }
            res = requests.get(url, headers=headers)
        else:
            res = requests.get(url)
        if not res or res.status_code != 200:
            return None
        else:
            return res
    except Exception as e:
        return None

import signal

def quit(*args):
    global processes
    for process in processes:
        try:
            if process.is_alive():
                os.kill(process.pid, 9)
        except Exception as e:
            pass

run()
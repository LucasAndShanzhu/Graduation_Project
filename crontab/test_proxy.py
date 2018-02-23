# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-11-14 14:22:37
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-01-26 15:47:35

from redis import Redis
import os
import requests
import threading
import time

redis_args = {
    'host': '127.0.0.1',
    'password': 'glx1997'
}

redis = Redis(**redis_args)
test_url = 'https://www.baidu.com'

threads = []

def test_proxy(redis):
    proxy = redis.spop('need_test_ip')
    while True:
        if not proxy:
            time.sleep(1)
            proxy = redis.spop('need_test_ip')
            continue;
        try:
            print proxy, 'start test'
            test_out = requests.get(test_url, proxies={'http': proxy, 'https': proxy}, timeout=4)
            if test_out.status_code != 200 or test_out.content.find('<form id=form name=f action=//www.baidu.com/s class=fm>') == -1:
                raise Exception("this is may need to be authened")
        except Exception as e:
            print proxy, ' is don\'t work'
        else:
            redis.sadd('ip', proxy)
        finally:
            proxy = redis.spop('need_test_ip')

def process_run(redis):
    threads = []
    for i in range(4):
        thread = threading.Thread(target=test_proxy, args=(redis,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def quit(*args):
    global processes
    for process in processes:
        if process.is_alive():
            os.kill(process.pid, 15)

import multiprocessing
processes = []
for i in range(2):
    process = multiprocessing.Process(target=process_run, args=(redis,))
    processes.append(process)
    process.start()

import signal

signal.signal(signal.SIGTERM, quit)

for process in processes:
    process.join()
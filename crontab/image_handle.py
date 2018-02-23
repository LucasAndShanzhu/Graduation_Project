# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-25 21:06:15
# @Last Modified by:   shanzhu
# @Last Modified time: 2017-12-26 16:04:08
from redis import Redis
import os
import requests
import threading
import time
import random
import multiprocessing

dir_path = os.getcwd() + '/../common'
import sys
sys.path.append(dir_path)

from oss import Oss
from config import Config

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
    image = redis.spop('need_handle_image')
    oss = Oss(config, 'upload-image%d' % rand_num)
    while True:
        if image is None:
            time.sleep(5)
            image = redis.spop('need_handle_image')
            continue;
        else:
            try:
                print "strart handle image %s" % image
                image_parts = image.split('|') 
                image_name = image_parts[0]
                image_url = image_parts[1]
                image = download(image_url)
                if image is None:
                    raise Exception('download img %s failure' % image_url)
                try:
                    oss.upload('spider-lucas', image_name, image)
                except Exception as e:
                    del oss
                    oss = Oss(config, 'upload-image%d' % rand_num)
            except Exception as e:
                print e
            finally:
                image = redis.spop('need_handle_image')
                time.sleep(1)

def download(url):
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return None
        else:
            return res.content
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
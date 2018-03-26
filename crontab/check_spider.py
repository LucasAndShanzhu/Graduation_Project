# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-03-26 15:46:41
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-26 16:16:15
import os, time
from redis import Redis

redis_args = {
    'password': 'glx1997'
}

redis = Redis(**redis_args)

while(True):
    keys = redis.keys('*_pid')
    for key in keys:
        key_name = key.split('_')[0]
        length_key = "{}_length".format(key_name)
        start_key = "{}_start".format(key_name)
        start = int(redis.get(start_key))
        length = int(redis.get(length_key))
        now = int(time.time())
        if start + length < now:
            os.kill(int(redis.get(key)), 9)
            redis.delete(key)
            redis.delete(length_key)
            redis.delete(start_key)

    time.sleep(60)

# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-22 14:38:00
# @Last Modified by:   shanzhu
# @Last Modified time: 2017-12-22 15:45:40

from redis import Redis

args = {
    'host': '127.0.0.1',
    'port': 6379,
    'socket_timeout': 5,
    'password': 'glx1997'
}

backup_file = '/Users/gonglingxiao/Graduation_Project/ip_list.txt'

file = open(backup_file, 'r+')

redis = Redis(**args)

ip_list = redis.smembers('ip')
if not len(ip_list):
    ip_list = file.read().split(' ')
    redis.sadd('need_test_ip', *ip_list)
else:
    data = ' '.join(ip_list)
    file.write(data)

file.close()

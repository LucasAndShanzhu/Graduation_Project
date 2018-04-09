# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-03-27 10:22:44
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-27 14:43:33
from pymongo import MongoClient
import numpy as np

import pymysql

mongo_args = {
    'host': '127.0.0.1',
    'port': 27017,
    'user': 'lucas',
    'passwd': '863bbc7b3febf915dd417c6195f74686',
    'database': 'item'
}

mysql_args = {
    'user': 'root',
    'password': 'glx1997',
    'database': 'spider',
    'host': '127.0.0.1',
    'port': 3306
}

mongo_uri = "mongodb://{}:{}@{}:{}/{}".format(mongo_args['user'], mongo_args['passwd'], mongo_args['host'], mongo_args['port'], mongo_args['database'])

mongo = MongoClient(mongo_uri)
collect = mongo.item.article_big_image

connect = pymysql.connect(**mysql_args)

def get_all_key_tag(collect):
    fields = {'_id': 0, 'key_words': 1, 'tag': 1}
    cursor = collect.find({}, fields)
    key_list = set()
    tag_list = set()
    for item in cursor:
        keys = item.get('key_words', [])
        tags = item.get('tag', [])
        for key in keys:
            key_list.add(key)
        for tag in tags:
            tag_list.add(tag)
    key_list = list(key_list)
    tag_list = list(tag_list)
    return (key_list, tag_list)

def get_position(key, key_list):
    index = -1
    try:
        index = key_list.index()
    except Exception as e:
        pass
    finally:
        return index

def judge_count(collect, type_, key_list):
    count_list = []
    for key in key_list:
        sum_amount = collect.count({type_: {'$all': [key]}})
        count_list.append(sum_amount)
    return count_list

def create_matrix(key_list, tag_list):
    lengthX = len(key_list)
    lengthY = len(tag_list)
    return np.zeros((lengthX, lengthY))

def get_detail_matrix(collect, matrix, key_list, tag_list):
    fields = {'_id': 0, 'key_words': 1, 'tag': 1}
    cursor = collect.find({}, fields)
    for item in cursor:
        keys = item.get('key_words', [])
        tags = item.get('tag', [])
        for key in keys:
            x = get_position(key, key_list)
            for tag in tags:
                y = get_position(tag, tag_list)
                matrix[x, y] += 1
    return matrix

def accurate_value(matrix, count_matrix, key_list, tag_list, connect):
    line, cow = matrix.shape
    cursor = connect.cursor()
    for x in xrange(line):
        line_m = matrix[x, : ]
        count_list = count_matrix[x, : ].tolist()
        temp_count_m = np.mat(np.diag(count_list))
        value_m = count_list * temp_count_m
        pos = np.argmax(value_m)
        key = key_list[x]
        tag = tag_list[pos]
        sql = "insert into key_tag_table(key_word, tag) values('{}', '{}')".format(key, tag)
        cursor.execute(sql)
    connect.commit()

def run():
    try:
        key_list, tag_list = get_all_key_tag(collect)
        matrix = create_matrix(key_list, tag_list)
        key_count_m = np.mat(judge_count(collect, 'key_words', key_list))
        tag_count_m = np.mat(judge_count(collect, 'tag', tag_list))
        matrix = get_detail_matrix(collect, matrix, key_list, tag_list)
        count_matrix = key_count_m.T * tag_count_m
        count_matrix = 1.0 / np.sqrt(count_matrix)
        accurate_value(matrix, count_matrix, key_list, tag_list, connect)
    except :
        pass
    finally:
        connect.close()

if __name__ == '__main__':
    run()

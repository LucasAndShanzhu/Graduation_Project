# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2017-12-11 09:20:42
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-03-23 10:47:58
import os
import pymysql
import random
import datetime
import time
import chardet

from selenium import webdriver

from Signal import Signal
from .config import Config
from .sredis import SRedis
from .mysql import Mysql

conf = Config("/home/lucas/Graduation_Project/infoflow/infoflow/util/spider.ini")
uredis = SRedis(conf)
util_mysql = Mysql(conf)
util_mysql.connect()

mysql = util_mysql
driver = None

def get_user_agent():
    mysql.get_cursor()
    sql = "select user_agent from user_agent_list"
    user_agents = mysql.exec_mysql(sql)
    mysql.close_cursor()
    return random.choice(user_agents)[0].strip()

def init_webdriver():
    global driver
    if driver is None:
        service_args = []
        service_args.append('--load-images=no')
        service_args.append('--ignore-ssl-errors=true')
        driver = webdriver.PhantomJS(service_args=service_args)
        driver.implicitly_wait(10)
    return driver

def get_cookie(url):
    global driver
    if driver is None:
        init_webdriver()
    try:
        driver.delete_all_cookies()
        driver.get(url)
        cookies = driver.get_cookies()
        cookie_list = ["{}={}".format(cookie['name'], cookie['value']) for cookie in cookies]
        cookie_header = "; ".join(cookie_list)
    except Exception:
        raise
    finally:
        driver.quit()
        driver = None
    return cookie_header

def login(url, postData = None, headers = None):
    cursor = mysql.get_cursor()
    sql = "select cookie, expires from login_cookie where url=%s"
    cursor.execute(sql, url)
    cookie_result = cursor.fetchone()
    if cookie_result and cookie_result[0]:
       now = time.time() 
       expires = int(cookie_result[1])
       if now < expires:
            return cookie_result[0]

    import urllib2
    import cookielib
    cookie = cookielib.CookieJar()
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)
    if headers:
        headers = [(key,value) for (key, value) in headers.items()]
        opener.addheaders = headers
    args = [url]
    if postData:
        temp = []
        for key,value in postData.items():
            temp.append("{}={}".format(key,value))
        postData = "&".join(temp)
        args.append(postData)
    result = None
    for i in range(5):
        try:
            result = opener.open(*args)
        except Exception as e:
            pass
        else:
            break
    if result is None:
        return ''
    cookie_list = []
    expires = 0
    for item in cookie:
        cookie_list.append("{}={}".format(item.name, item.value))
        if item.expires is not None:
            if expires == 0 or expires > item.expires:
                expires = item.expires
    cookie_str = '; '.join(cookie_list)
    if cookie_result and cookie_result[0]:
        sql = "update login_cookie set cookie=%s, expires={} where url=%s".format(expires)    
    else:
        sql = "insert login_cookie(cookie, url, expires) values (%s, %s, {})".format(expires)
    cursor.execute(sql, (cookie_str, url))
    mysql.commit()
    mysql.close_cursor()
    return cookie_str

def now():
    now = datetime.datetime.now()
    year, month, day, hour, minute, second = list(now.timetuple())[:6]
    return "{}-{}-{} {}:{}:{}".format(year, month, day, hour, minute, second)

def now_timestamp():
    now = time.time()
    return int(now)

def get_host(url):
    if not url.startswith("http") and not url.startswith("https"):
        return None
    parts = url.split("/")
    return parts[2]

UTF8 = ['u8', 'utf', 'utf8', 'utf-8']

def get_utf8_str(string, encoding):
    if isinstance(string, unicode):
        return string.encode('utf8')
    else:
        return string.decode(encoding) if encoding.lower() not in UTF8 else string

def get_province_city():
    mysql.get_cursor()
    province_sql = "select id, province from province"

    result = mysql.exec_mysql(province_sql)
    if not result and not result[0]:
        return {}
    province_list = result
    province_city = {}
    sql = "select city from city where province={}"
    for province_data in province_list:
        province_id, province = province_data
        city_list = list(mysql.exec_mysql(sql.format(province_id)))
        province = province.encode('utf8')
        city_list = [city[0].encode('utf8') for city in city_list]
        province_city[province] = city_list
    mysql.close_cursor()
    return province_city
    
def get_topic(item_type):
    conn = mysql.get_db('graduation_project')
    cursor = conn.cursor()
    topic_table = {}
    try:
        sql = "select chs_name, eng_name from topic where item_type=%s"
        count = cursor.execute(sql, item_type)
        if count != 0:
            result = cursor.fetchall()
            for item in result:
                topic_table[item[0]] = item[1]
    except Exception as e:
        pass
    finally:
        conn.close()
        return topic_table

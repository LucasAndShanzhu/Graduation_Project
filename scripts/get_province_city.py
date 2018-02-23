# -*- coding: utf-8 -*-
# @Author: shanzhu
# @Date:   2018-01-29 12:32:36
# @Last Modified by:   shanzhu
# @Last Modified time: 2018-01-29 15:35:34

from selenium import webdriver
import pymysql

driver = webdriver.Chrome()

provinces = {}
citys = {}

url = 'http://www.gsdata.cn/rank/wxarc'

driver.get(url)

area_input = driver.find_element_by_id("fromcity")
area_input.click()

province_tab = driver.find_element_by_css_selector("li[tabname='province']")
city_tab = driver.find_element_by_css_selector("li[tabname='city']")

next_tab = driver.find_element_by_class_name("city-action-next")

mysql = pymysql.connect(user='lucas', passwd='glx1997', database='test', charset="utf8")
cursor = mysql.cursor()

try:
    province_tab.click()
    for i in xrange(3):
        for j in xrange(i):
            next_tab.click()
        show_ul = driver.find_element_by_class_name("city-content-item")
        province_list = show_ul.text.split('\n')
        for province in province_list:
            province = province.encode("utf8")
            provinces[province] = 0
            citys[province] = []
            province_a = driver.find_element_by_css_selector('li[title="{}"]'.format(province))
            province_a.click()
            city_list = citys[province]
            not_over = True
            while not_over:        
                temp_city_list = show_ul.text.split('\n')
                temp_city_list = [d.encode('utf8') for d in temp_city_list]
                for city in temp_city_list:
                    if city in city_list:
                        not_over = False
                        break
                    else:
                        if city != '全省':
                            city_list.append(city)
                if not_over:
                    next_tab.click()
            province_tab.click()
            for j in xrange(i):
                next_tab.click()

    for province in provinces:
        sql = "select id from province where province='{}'".format(province)
        cursor.execute(sql)
        result = cursor.fetchone()
        province_id = 0
        if not result:
            sql = "insert into province (province) values('{}')".format(province)
            cursor.execute(sql)
            province_id = mysql.insert_id()
        else:
            province_id = result[0]
        select_sql = "select id from city where province={} and city='{}'"
        insert_sql = "insert into city(province, city) values({}, '{}')"
        for city in citys[province]:
            cursor.execute(select_sql.format(province_id, city))
            result = cursor.fetchone()
            if not result:
                cursor.execute(insert_sql.format(province_id, city))
        mysql.commit()

except Exception:
    raise
finally:
    mysql.close()
    driver.quit()

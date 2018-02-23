# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InfoflowItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

#ip
class IpItem(scrapy.Item):
    ip = scrapy.Field()
    port = scrapy.Field()

class ArticleBigImageItem(scrapy.Item):
    title = scrapy.Field()
    detail = scrapy.Field()
    source = scrapy.Field()
    source_detail = scrapy.Field()
    channel = scrapy.Field()
    spider_source = scrapy.Field()
    url = scrapy.Field()
    original_time = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    like_num = scrapy.Field()
    read_num = scrapy.Field()
    comment_num = scrapy.Field()
    forward_num = scrapy.Field()
    tag = scrapy.Field()
    md5 = scrapy.Field()
    image = scrapy.Field()

#     db.article_big_image.insert({
#     'id':123, ,
#     `tag`: [],
#     'status_code': 0, 
#     'CTR': 0.0, 
#     'show_num': 123, 
#     'click_num': 23, 
#     'created_at': ''
# })

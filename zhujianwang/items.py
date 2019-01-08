# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhujianwangItem(scrapy.Item):
    # define the fields for your item here like:
    compass_name = scrapy.Field()
    honor_code = scrapy.Field()
    province = scrapy.Field()
    legal_person = scrapy.Field()

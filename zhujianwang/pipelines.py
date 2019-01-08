# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from __future__ import print_function
import logging

import redis


class ZhujianwangPipeline(object):
    def open_spider(self, spider):
        self.redis_tool = redis.StrictRedis(db=15)

    def process_item(self, item_contains, spider):
        for item in item_contains["item_contains"]:
            k = "{}##{}".format(item["province"].strip("\n\t\r "), item["compass_name"].strip("\n\t\r "))
            v = "{}##{}".format(item["honor_code"].strip("\n\t\r "), item["legal_person"].strip("\n\t\r "))
            self.redis_tool.sadd(k, v)
            self.redis_tool.set(name=item_contains["url"], value=1)
            print(u"{}存储成功！".format(k))
        return item_contains

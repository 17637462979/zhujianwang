# -*- coding: utf-8 -*-
import logging

import redis
import scrapy
from scrapy import cmdline
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from zhujianwang.items import ZhujianwangItem

class Getlist1Spider(CrawlSpider):
    name = 'getlist1'
    allowed_domains = ['www.zhujianpt.com']
    # start_urls = ['http://www.zhujianpt.com/company/0-0-0-0-1000.html']
    start_urls = [
        # "http://www.zhujianpt.com/company/0-0-130006-0-400.html",
        # "http://www.zhujianpt.com/company/0-0-130005-0-200.html",
        # "http://www.zhujianpt.com/company/0-0-130003-0-150.html",
        # "http://www.zhujianpt.com/company/0-0-130002-0-700.html",
        # "http://www.zhujianpt.com/company/0-0-130001-0-100.html",
        "http://www.zhujianpt.com/company/0-0-130004-0-8000.html",

    ]

    # custom_settings = {
    #     # "DOWNLOAD_DELAY": 3
    # }
    redis_tool = redis.StrictRedis(db=3)
    rules = (
        Rule(LinkExtractor(allow=r'/company/0-0-130004-0-(\d+)\.html'), callback='parse_item', follow=True),   # 翻页并解析列表
    )

    def parse_item(self, response):
        nodes = response.xpath(r'//ul[@class="company_contents"]/li[contains(@class, "project")]')
        # /company/0-0-130001-0-99.html
        item_contains = []

        logging.info("解析.....{},{}".format(len(nodes), response.url))
        for node in nodes:
            i = ZhujianwangItem()
            i["compass_name"] = node.xpath('./div[contains(@class, "name")]/a[@title]/text()').extract_first()
            if not i["compass_name"]:
                logging.warning("{}没有公司名".format(response.url))
                continue
            i["honor_code"] = node.xpath('./div[contains(@class, "term")]//text()').extract_first() or "None"
            i["province"] = node.xpath('./div[contains(@class, "build_area")]//text()').extract_first() or "None"
            i["legal_person"] = node.xpath('./div[contains(@class, "legal_person")]//text()').extract_first() or "None"
            k = "{}_{}_{}_{}".format(i["compass_name"], i["honor_code"], i["province"], i["legal_person"])
            if self.redis_tool.exists(k):
                logging.warning("{}已经存在".format(k))
                break
            item_contains.append(i)
        yield {"item_contains": item_contains}

    def pre_handle_items(self, items):
        # 省为key, 相同省份的列表保存
        i = {}
        for item in items:
            if list(item.keys())[0] not in i:
                i[list(item.keys())[0]] = [list(item.values())[0]]
            else:
                i[list(item.keys())[0]].extend(item.values())

        """
        for d in mydi:
            if list(d.keys())[0] not in i:
                i[list(d.keys())[0]] = [list(d.values())[0]]
            else:
                i[list(d.keys())[0]].extend(d.values())
        """

        return i



if __name__ == "__main__":
    cmdline.execute(["scrapy ", "spider ", Getlist1Spider.name])

# /home/python/anaconda3/bin/scrapy crawl getlist1
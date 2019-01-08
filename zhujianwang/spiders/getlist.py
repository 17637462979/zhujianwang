# -*- coding: utf-8 -*-
import redis
import scrapy
from scrapy import cmdline

from zhujianwang.items import ZhujianwangItem


class Getlist1Spider(scrapy.Spider):
    name = 'getlist'
    allowed_domains = ['www.zhujianpt.com']
    start_urls = [
        # ('http://www.zhujianpt.com/company/0-0-0-0-9000.html', 12042),
        #  ('http://www.zhujianpt.com/company/0-0-0-0-7000.html', 12043),

          # ('http://www.zhujianpt.com/company/0-0-0-0-5000.html', 6999),
           # ('http://www.zhujianpt.com/company/0-0-0-0-4000.html',5000),
        # ('http://www.zhujianpt.com/company/0-0-0-0-2000.html', 4000),
        # ('http://www.zhujianpt.com/company/0-0-0-0-1.html', 2000),  31555key, 1993个链接

        # 招标代理
        ("http://www.zhujianpt.com/company/0-0-130003-0-1.html", 376),
        ("http://www.zhujianpt.com/company/0-0-130002-0-1.html", 1437),
        ("http://www.zhujianpt.com/company/0-0-130001-0-1.html", 261),
        ("http://www.zhujianpt.com/company/0-0-130005-0-1.html", 396),
        ("http://www.zhujianpt.com/company/0-0-130006-0-1.html", 852),

    ]
    # custom_settings = {
    #     "DOWNLOAD_DELAY": 3
    # }
    redis_tool = redis.StrictRedis(db=3)

    def start_requests(self):
        for url, max_page in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True, meta={"max_page": max_page})

    def parse(self, response):

        if not self.redis_tool.exists(response.url):
            print("{}.不存在,可以爬....", response.url)
            nodes = response.xpath(r'//ul[@class="company_contents"]/li[contains(@class, "project")]')
            item_contains = []

            for node in nodes:
                i = ZhujianwangItem()
                i["compass_name"] = node.xpath('./div[contains(@class, "name")]/a[@title]/text()').extract_first()
                if not i["compass_name"]:
                    print("{}没有公司名".format(response.url))
                    continue
                i["honor_code"] = node.xpath('./div[contains(@class, "term")]//text()').extract_first() or "None"
                i["province"] = node.xpath('./div[contains(@class, "build_area")]//text()').extract_first() or "None"
                i["legal_person"] = node.xpath('./div[contains(@class, "legal_person")]//text()').extract_first() or "None"
                k = u"{}##{}".format(i["province"], i["compass_name"])
                if self.redis_tool.exists(k):
                    print(u"{}已经存在".format(k), self.redis_tool.exists(k))
                    continue
                item_contains.append(i)
            yield {"item_contains": item_contains, "url": response.url}
        max_page = response.meta["max_page"]
        next_link = "http://www.zhujianpt.com" + response.xpath(u'//a[@class="control" and contains(text(), "下一页")]/@href').extract_first()
        headers = {
            "Host": "www.zhujianpt.com",
            "Referer": response.url,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",

        }
        if str(max_page) not in next_link:
            yield scrapy.Request(url=next_link, headers=headers, meta={"max_page": max_page})
        else:
            print("结束翻页：", response.url)

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

"""

k = "上海宝冶工程技术有限公司_310113000696310_阳刚_上海"
"""
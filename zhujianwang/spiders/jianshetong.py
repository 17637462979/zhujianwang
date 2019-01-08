# -*- coding: utf-8 -*-
import redis
import scrapy
from scrapy import cmdline

from zhujianwang.items import ZhujianwangItem
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class JianSheTong(scrapy.Spider):
    name = 'jianshetong'
    allowed_domains = ['hhb.cbi360.net']
    start_urls = [
        ("https://hhb.cbi360.net/companysoso/?pageIndex=201&provinceid=510000&searchMatch=2", "四川")
    ]

    redis_tool = redis.StrictRedis(db=5)

    def start_requests(self):
        for url, province in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True, meta={"province": province})

    def parse(self, response):
        meta = response.meta
        if not self.redis_tool.exists(response.url):

            print("{}.不存在,可以爬....".format(response.url))
            nodes = response.xpath(r'//ul[@class="hhb-search-list-ul"]/li')
            item_contains = []

            for node in nodes:
                i = ZhujianwangItem()
                i["compass_name"] = node.xpath('.//div[@class="list-title-w"]//a/text()').extract_first()
                if not i["compass_name"]:
                    print(u"{}没有公司名".format(response.url))
                    continue
                i["honor_code"] = "None"
                i["province"] = meta["province"]
                i["legal_person"] = "None"
                k = u"{}##{}".format(i["province"], i["compass_name"])
                if self.redis_tool.exists(k):
                    print(u"{}已经存在".format(k), self.redis_tool.exists(k))
                    continue
                item_contains.append(i)
            yield {"item_contains": item_contains, "url": response.url}
        next_page_link = response.xpath(u'//a[@class="updownpage" and contains(text(), "下一页")]/@href').extract_first()
        headers = {
            "Host": "hhb.cbi360.net",
            "Referer": response.url,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",

        }
        if next_page_link:
            next_link = "https://hhb.cbi360.net" + next_page_link
            yield scrapy.Request(url=next_link, headers=headers, meta=meta, callback=self.parse)
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
    cmdline.execute(["scrapy ", "spider ", JianSheTong.name])

"""

k = "上海宝冶工程技术有限公司_310113000696310_阳刚_上海"
"""
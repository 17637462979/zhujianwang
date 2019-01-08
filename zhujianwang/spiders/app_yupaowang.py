# -*- coding: utf-8 -*-
import redis
import scrapy
from scrapy import cmdline

from zhujianwang.items import ZhujianwangItem
import sys
reload(sys)
sys.setdefaultencoding('utf8')


headers = {
    "Host": "m.jian.net",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Linux; Android 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044408 Mobile Safari/537.36 MicroMessenger/6.6.7.1321(0x26060739) NetType/WIFI Language/zh_CN:",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,image/wxpic,image/sharpp,image/apng,image/tpg,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflat",
    "Accept-Language": "zh-CN,en-US;q=0.8",
    # "Referer": "http://m.jian.net/qiye?city_id=23&city_name=%E5%9B%9B%E5%B7%9D&page=2",
}

class YuPaoWang(scrapy.Spider):
    name = 'yupao'
    allowed_domains = ['m.jian.net']
    start_urls = [
        # ("http://m.jian.net/qiye?city_id=23&city_name=四川", "四川"),
        ("http://m.jian.net/qiye?city_id=27&city_name=陕西", "陕西"),

        # ("http://m.jian.net/qiye?city_id=1&city_name=北京", "北京"),
        # ("http://m.jian.net/qiye?city_id=2&city_name=天津", "天津"),
        # ("http://m.jian.net/qiye?city_id=3&city_name=河北", "河北"),
        # ("http://m.jian.net/qiye?city_id=4&city_name=山西", "山西"),
        # ("http://m.jian.net/qiye?city_id=5&city_name=内蒙古", "内蒙古"),
        # ("http://m.jian.net/qiye?city_id=6&city_name=辽宁", "辽宁"),
        # ("http://m.jian.net/qiye?city_id=7&city_name=吉林", "吉林"),
        # ("http://m.jian.net/qiye?city_id=8&city_name=黑龙江", "黑龙江"),
        # ("http://m.jian.net/qiye?city_id=9&city_name=上海", "上海"),
        # ("http://m.jian.net/qiye?city_id=10&city_name=江苏", "江苏"),
        # ("http://m.jian.net/qiye?city_id=11&city_name=浙江", "浙江"),
        # ("http://m.jian.net/qiye?city_id=12&city_name=安徽", "安徽"),
        # ("http://m.jian.net/qiye?city_id=13&city_name=福建", "福建"),
        # ("http://m.jian.net/qiye?city_id=14&city_name=江西", "江西"),
        # ("http://m.jian.net/qiye?city_id=15&city_name=山东", "山东"),
        # ("http://m.jian.net/qiye?city_id=16&city_name=河南", "河南"),
        # ("http://m.jian.net/qiye?city_id=17&city_name=湖北", "湖北"),
        # ("http://m.jian.net/qiye?city_id=18&city_name=湖南", "湖南"),
        # ("http://m.jian.net/qiye?city_id=19&city_name=广东", "广东"),
        # ("http://m.jian.net/qiye?city_id=20&city_name=广西", "广西"),
        # ("http://m.jian.net/qiye?city_id=21&city_name=海南", "海南"),
        # ("http://m.jian.net/qiye?city_id=22&city_name=重庆", "重庆"),
        # ("http://m.jian.net/qiye?city_id=24&city_name=贵州", "贵州"),
        # ("http://m.jian.net/qiye?city_id=25&city_name=云南", "云南"),
        # ("http://m.jian.net/qiye?city_id=26&city_name=西藏", "西藏"),
        # ("http://m.jian.net/qiye?city_id=28&city_name=甘肃", "甘肃"),
        # ("http://m.jian.net/qiye?city_id=29&city_name=青海", "青海"),
        # ("http://m.jian.net/qiye?city_id=30&city_name=宁夏", "宁夏"),
        # ("http://m.jian.net/qiye?city_id=31&city_name=新疆", "新疆"),
    ]
    custom_settings = {
        "DOWNLOAD_DELAY": 2
    }
    redis_tool = redis.StrictRedis(db=15)

    def start_requests(self):
        for url, province in self.start_urls:
            headers["Referer"] = "http://m.jian.net"
            yield scrapy.Request(url, callback=self.parse, headers=headers, dont_filter=True, meta={"province": province, "cur_page": 1, "total_page": 180644})

    def parse(self, response):
        meta = response.meta

        if not self.redis_tool.exists(response.url):

            print("{}.不存在,可以爬....".format(response.url))
            nodes = response.xpath(r'//ul[@id="companylist"]/li')
            print("{}".format(len(nodes)))
            item_contains = []
            for node in nodes:
                i = ZhujianwangItem()
                i["compass_name"] = "".join(node.xpath('.//span[@class="span1"]//text()').extract())
                if not i["compass_name"]:
                    print(u"{}没有公司名".format(response.url))
                    continue
                i["honor_code"] = "None"
                i["province"] = meta["province"]
                i["legal_person"] = node.xpath('./a[contains(@href, "qiye")]/@href').extract_first()
                k = u"{}##{}".format(i["province"], i["compass_name"])
                if self.redis_tool.exists(k):
                    print(u"{}已经存在".format(k), self.redis_tool.exists(k))
                    continue
                item_contains.append(i)
            print(item_contains)
            yield {"item_contains": item_contains, "url": response.url}
        # string()与text(): 前者表示所有后代文本,后者表示儿子代文本
        next_page_link = response.xpath(u'//tr[@valign="bottom"]//a[contains(@href, "qiye") and contains(string(), "下一页")]/@href').extract_first()
        cur_page, total_page = meta["cur_page"], meta["total_page"]

        if next_page_link or int(cur_page) < int(total_page):
            headers["Referer"] = response.url
            yield scrapy.Request(url=next_page_link, headers=headers, meta=meta, callback=self.parse)
        else:
            print("结束翻页：", response.url)
            print(u"打印resposne:\n\n{}".format(response.text))


if __name__ == "__main__":
    cmdline.execute(["scrapy ", "spider ", YuPaoWang.name])

"""

k = "上海宝冶工程技术有限公司_310113000696310_阳刚_上海"
"""
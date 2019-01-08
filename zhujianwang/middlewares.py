# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import base64
import random
import time



from .UserAgentList import USER_AGENT_LIST
class DelayMiddleware(object):
    def process_request(self, request, spider):
        print(request.url)
        print("DelayMiddleware.......")
        time.sleep(random.random()*2)
        ua = random.choice(USER_AGENT_LIST)
        request.headers["User-Agent"] = ua
        pass


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.headers['Proxy-Authorization'] = base64.b64encode("2055381145:84nehtqp")
        print("-"*10)
        print(request.headers['Proxy-Authorization'])
        time.sleep(random.random()*3)
        print("-"*15)
        # return request


# -*- coding: utf-8 -*-
import logging

import scrapy
from scrapy import Request


class HeungaSpider(scrapy.Spider):
    name = 'heunga'
    allowed_domains = ['http://www.heung-a.co.kr']
    start_urls = ['http://www.heung-a.co.kr/dzSmart/innerFile/modules/portlist.xml?_=1575014547347']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            'RCL.pipelines.MongoPipeline': 300
        }
    }

    def start_requests(self):
        yield Request(url=self.start_urls[0],
                      method='GET',
                      meta={
                      },
                      dont_filter=True,
                      callback=self.parse)

    def parse(self, response):
        logging.info(response.text)

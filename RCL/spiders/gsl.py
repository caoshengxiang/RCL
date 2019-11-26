# -*- coding: utf-8 -*-
import logging

import scrapy


class GslSpider(scrapy.Spider):
    name = 'gsl'
    allowed_domains = ['https://www.gslltd.com.hk']
    start_urls = ['https://www.gslltd.com.hk/point-to-point_g.php']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            'RCL.pipelines.MongoPipeline': 300
        }
    }

    def parse(self, response):
        logging.info(response.text)

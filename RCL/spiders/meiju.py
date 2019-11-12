# -*- coding: utf-8 -*-
import scrapy


class MeijuSpider(scrapy.Spider):
    name = 'meiju'
    allowed_domains = ['meijutt.com']
    start_urls = ['http://www.meijutt.com/new100.html']

    def parse(self, response):
        print(response.text)
        pass

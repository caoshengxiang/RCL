# -*- coding: utf-8 -*-
import logging
import re

import scrapy
from pyquery import PyQuery as pq
from scrapy import FormRequest, Request

from RCL.items import StaticsItem


class NamsungstaticSpider(scrapy.Spider):
    name = 'NSRU_STATIC'
    allowed_domains = ['http://www.namsung.co.kr']
    start_urls = ['http://www.namsung.co.kr/frt/ko/business/road/screen.do']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    def parse(self, response):
        doc = pq(response.text)
        alink = doc('#tab_road ul li a')
        url_base = 'http://www.namsung.co.kr/frt/ko/business/road/'
        for al in alink.items():
            service = al.text()
            href = al.attr('href')
            yield Request(
                url=url_base + href,
                method='GET',
                meta={
                    'service': service,
                },
                dont_filter=True,
                callback=self.parse_routecode)

    def parse_routecode(self, response):
        doc = pq(response.text)
        service = response.meta['service']
        alink = ''
        if service == 'KOREA - JAPAN':
            alink = doc("#submenu1 a")
        elif service == 'KOREA - CHINA':
            alink = doc("#submenu2 a")
        elif service == 'CHINA - JAPAN':
            alink = doc("#submenu3 a")
        elif service == 'KOREA - INTRA ASIA':
            alink = doc("#submenu4 a")

        url = 'http://www.namsung.co.kr/frt/ko/business/road_table/screen.do?code1={}&code2={}'
        for a in alink.items():
            routeCode = a.text()
            href = a.attr('href')
            reP = re.compile(r'[\'](.*?)[\']', re.S)  # 解析 js
            param = re.findall(reP, href)
            logging.info(response.meta['service'])
            logging.info(routeCode)
            logging.info(param)

            yield Request(
                url=url.format(param[0], param[1]),
                method='GET',
                meta={
                    'service': response.meta['service'],
                    'routeCode': routeCode,
                },
                dont_filter=True,
                callback=self.parse_list)

    def parse_list(self, response):
        doc = pq(response.text)
        trs = doc('#mainTable table tr')

        item = StaticsItem()
        item['ROUTE_PARENT'] = response.meta['service']
        item['ROUTE_NAME_EN'] = response.meta['service']
        item['ROUTE_CODE'] = response.meta['routeCode']
        list = []
        for index, tr in enumerate(trs.items()):
            if index == 0:
                continue
            tds = tr.find('td')
            list.append({
                'PORT': tds.eq(0).text(),
                'ETA': tds.eq(1).text().split(' ')[0],
                'ETD': tds.eq(2).text().split(' ')[0],
                'TERMINAL': tds.eq(3).text()
            })
        item['DOCKING_LIST'] = list
        yield item

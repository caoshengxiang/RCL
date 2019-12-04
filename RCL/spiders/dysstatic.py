# -*- coding: utf-8 -*-
import logging
import time

import requests
import scrapy
from scrapy import FormRequest
from pyquery import PyQuery as pq

from RCL.items import PortItem, PortGroupItem, GroupItem, StaticsItem


class DysSpider(scrapy.Spider):
    name = 'DYSL_STATIC'
    allowed_domains = ['http://www.pcsline.co.kr']
    start_urls = ['http://www.pcsline.co.kr/eng/service/schedule.asp']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    def start_requests(self):

        # 静态航线
        staticUrls = [
            {
                'url': 'http://www.pcsline.co.kr/eng/service/service0111.asp',
                'ROUTE_PARENT': 'KOREA-JAPAN',
                'ROUTE_NAME_EN': 'HANSHIN SERVICE'
            },
            {
                'url': 'http://www.pcsline.co.kr/eng/service/service0112.asp',
                'ROUTE_PARENT': 'KOREA-JAPAN',
                'ROUTE_NAME_EN': 'KEIHIN SERVICE'
            },
            {
                'url': 'http://www.pcsline.co.kr/eng/service/service0113.asp',
                'ROUTE_PARENT': 'KOREA-JAPAN',
                'ROUTE_NAME_EN': 'WEST JAPAN SERVICE'
            }
        ]
        for sta_route in staticUrls:
            yield FormRequest(url=sta_route['url'],
                              method='GET',
                              # dont_filter=True,
                              meta={
                                  'ROUTE_PARENT': sta_route['ROUTE_PARENT'],
                                  'ROUTE_NAME_EN': sta_route['ROUTE_NAME_EN']
                              },
                              callback=self.parse_static_route)

    def parse_static_route(self, response):
        doc = pq(response.text)
        mT20 = doc('table.mT20')

        for index, mt20 in enumerate(mT20.items()):
            logging.info('航线代码：')
            route_code = mt20.find('strong').text().replace(' ', '').split(':')[1]
            logging.info(route_code)
            mT15 = mt20.next('table.mT15')
            item = StaticsItem()
            item['ROUTE_PARENT'] = response.meta['ROUTE_PARENT']
            item['ROUTE_NAME_EN'] = response.meta['ROUTE_NAME_EN']
            item['ROUTE_CODE'] = route_code
            list = []
            trs = mT15.find('tr')
            for tr in trs.items():
                if tr.find('td[bgcolor="#f4f4f4"]'):
                    row = {}
                    tds = tr.find('td')
                    row['PORT'] = tds.eq(0).text()
                    row['ETA'] = tds.eq(1).text().split(' ')[0]
                    row['ETD'] = tds.eq(2).text().split(' ')[0]
                    row['TERMINAL'] = tds.eq(3).text()
                    list.append(row)
            item['DOCKING_LIST'] = list
            yield item

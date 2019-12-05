# -*- coding: utf-8 -*-
import logging
import time

import requests
import scrapy
from scrapy import FormRequest, Request
from pyquery import PyQuery as pq

from RCL.items import PortItem, PortGroupItem, GroupItem, StaticsItem


class DysSpider(scrapy.Spider):
    name = 'EASC_STATIC'
    allowed_domains = ['http://www.pcsline.co.kr']
    start_urls = ['http://www.pcsline.co.kr/eng/service/schedule.asp']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    def start_requests(self):

        # 静态航线
        staticUrls = [
            {
                'url': 'http://www.easline.co.kr/service/xingang.aspx',
                'ROUTE_PARENT': 'KOREA-CHINA',
                'ROUTE_NAME_EN': 'XINGANG/DALIAN',
            },
            {
                'url': 'http://www.easline.co.kr/service/yantai.aspx',
                'ROUTE_PARENT': 'KOREA-CHINA',
                'ROUTE_NAME_EN': 'YANTAI/XINGANG',
            },
            {
                'url': 'http://www.easline.co.kr/service/shanghai.aspx',
                'ROUTE_PARENT': 'KOREA-CHINA',
                'ROUTE_NAME_EN': 'SHANGHAI/NINGBO',
            },
            {
                'url': 'http://www.easline.co.kr/service/lianyungang.aspx',
                'ROUTE_PARENT': 'KOREA-CHINA',
                'ROUTE_NAME_EN': 'LIANYUNGANG/QINGDAO',
            }
        ]
        for sta_route in staticUrls:
            yield Request(url=sta_route['url'],
                              method='GET',
                              # dont_filter=True,
                              meta={
                                  'ROUTE_PARENT': sta_route['ROUTE_PARENT'],
                                  'ROUTE_NAME_EN': sta_route['ROUTE_NAME_EN'],
                              },
                              callback=self.parse_static_route)

    def parse_static_route(self, response):
        doc = pq(response.text)
        cont = doc('#cont')

        mapSet = cont.find('div.mapSet')
        for map in mapSet.items():
            item = StaticsItem()
            item['ROUTE_PARENT'] = response.meta['ROUTE_PARENT']
            item['ROUTE_NAME_EN'] = response.meta['ROUTE_NAME_EN']
            item['ROUTE_CODE'] = response.meta['ROUTE_NAME_EN']
            h3text = map.find('h3').text()
            item['ROUTE_CODE'] = h3text
            trs = map.find('table.data tr')
            list = []
            for tr in trs.items():
                if tr.find('th[scope="row"]') and tr.find('td[class="ac"]'):
                    tds = tr.find('td')
                    list.append({
                        'PORT': tr.find('th').text(),
                        'TERMINAL': '',
                        'ETA': tds.eq(0).text(),
                        'ETD': tds.eq(1).text(),
                    })
            item['DOCKING_LIST'] = list
            yield item

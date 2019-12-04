# -*- coding: utf-8 -*-
import logging
import re
import time
from pyquery import PyQuery as pq

import scrapy
from scrapy import FormRequest, Request

from RCL.items import PortItem, PortGroupItem, GroupItem, StaticsItem


def GetMiddleStr(content, startStr, endStr):
    patternStr = r'%s(.+?)%s' % (startStr, endStr)
    p = re.compile(patternStr, re.IGNORECASE)
    m = re.findall(p, content)
    if m:
        return m[0]


class DjsSpider(scrapy.Spider):
    name = 'DJSL_STATIC'
    allowed_domains = ['http://korea.djship.co.kr']
    start_urls = [
        'http://korea.djship.co.kr/dj/ui/cn/business/sub2_1_0.jsp?PROGRAM_ID=sub2_1&mode=JAPAN&ROUTE_CODE=KJK&SWF=01KJK.swf']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    headers = {
        'Cookie': 'JSESSIONID=F5ABD7CBFAA6AA67BEFA743B1ECA890B'
    }

    def parse(self, response):
        doc = pq(response.text)
        trs = doc(
            'body > form > table:nth-child(6) > tr > td:nth-child(2) > table > tr > td:nth-child(2) > table:nth-child(3) tr')
        for tr in trs.items():
            try:
                href = 'http://korea.djship.co.kr/dj/ui/cn/business/' + tr.find('a').attr('href')
                logging.debug(href)
                ROUTE_PARENT = GetMiddleStr(href, '&mode=', '&ROUTE_CODE')
                logging.debug(ROUTE_PARENT)
                yield Request(url=href,
                              dont_filter=True,
                              method='GET',
                              meta={
                                  'ROUTE_PARENT': ROUTE_PARENT
                              },
                              headers=self.headers,
                              callback=self.parse_code)
            except Exception as e:
                logging.error(e)

    def parse_code(self, response):
        doc = pq(response.text)
        alinks = doc('#new_route a')
        for al in alinks.items():
            try:
                href = 'http://korea.djship.co.kr/dj/ui/cn/business/' + al.attr('href')
                ROUTE_CODE = GetMiddleStr(href, '&ROUTE_CODE=', '&SWF')
                yield Request(url=href,
                              dont_filter=True,
                              method='GET',
                              meta={
                                  'ROUTE_PARENT': response.meta['ROUTE_PARENT'],
                                  'ROUTE_CODE': ROUTE_CODE,
                              },
                              headers=self.headers,
                              callback=self.parse_list)
            except Exception as e:
                logging.error(e)

    def parse_list(self, response):
        doc = pq(response.text)
        trs = doc('table.tb_color1 tr')
        item = StaticsItem()
        item['ROUTE_PARENT'] = response.meta['ROUTE_PARENT']
        item['ROUTE_NAME_EN'] = response.meta['ROUTE_CODE']
        item['ROUTE_CODE'] = response.meta['ROUTE_CODE']
        list = []
        for index, tr in enumerate(trs.items()):
            if index == 0:
                continue
            tds = tr.find('td')
            list.append({
                'PORT': tds.eq(0).text(),
                'TERMINAL': tds.eq(1).text(),
                'ETA': GetMiddleStr(tds.eq(2).text(), '\(', '\)'),
                'ETD': GetMiddleStr(tds.eq(4).text(), '\(', '\)'),
            })
        item['DOCKING_LIST'] = list
        yield item
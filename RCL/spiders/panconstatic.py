# -*- coding: utf-8 -*-
import json
import logging
import re

import scrapy
from scrapy import Request

from RCL.items import StaticsItem


class PanconstaticSpider(scrapy.Spider):
    name = 'PASU_STATIC'
    allowed_domains = ['http://www.namsung.co.kr']
    start_urls = ['http://http://www.namsung.co.kr/']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    def start_requests(self):
        yield Request(
            url='http://www.pancon.co.kr/pan/getDataMenu.pcl',
            method='POST',
            body=json.dumps({
                'I_AS_LINE_CD': ""
            }),
            headers={'Content-Type': 'application/json'},
            meta={
            },
            dont_filter=True,
            callback=self.parse)

    def parse(self, response):
        data = json.loads(response.text)
        SP_SVC_ROUTE_DTL_R = data['SP_SVC_ROUTE_DTL_R']  # 子菜单
        # SP_SVC_ROUTE_GRP_R = data['SP_SVC_ROUTE_GRP_R']  # 菜单名

        for dtl in SP_SVC_ROUTE_DTL_R:
            # reP = re.compile(r'[(](.*?)[)]', re.S)  # 解析 js
            # serv = re.findall(reP, dtl['LINE_NM'])
            # service = ''
            # if len(serv):
            #     service = serv[0]

            yield Request(
                url='http://www.pancon.co.kr/pan/getDataSvcRouteVer.pcl',
                method='POST',
                body=json.dumps({
                    'I_AS_LINE_CD': dtl['LINE_CD']
                }),
                headers={'Content-Type': 'application/json'},
                meta={
                    'route': dtl['GRP_NM'],
                    # 'routeCode': dtl['LINE_NM'],
                    'service': dtl['LINE_NM']
                },
                dont_filter=True,
                callback=self.parse_linecd)

    def parse_linecd(self, response):
        data = json.loads(response.text)
        rows = data['rows']
        for row in rows:
            yield Request(
                url='http://www.pancon.co.kr/pan/getDataRouteSection.pcl',
                method='POST',
                body=json.dumps({
                    'I_AS_LINE_CD': row['LINE_CD'],
                    'I_AS_LINE_VER_SEQ': row['LINE_VER_SEQ']
                }),
                headers={'Content-Type': 'application/json'},
                meta={
                    'route': response.meta['route'],
                    'routeCode': row['LINE_NM'],
                    'service': response.meta['service']
                },
                dont_filter=True,
                callback=self.parse_list)

    def parse_list(self, response):
        data = json.loads(response.text)
        SP_SVC_ROUTE_PORT_R = data['SP_SVC_ROUTE_PORT_R']

        item = StaticsItem()
        item['ROUTE_PARENT'] = response.meta['route']
        item['ROUTE_NAME_EN'] = response.meta['service']
        item['ROUTE_CODE'] = response.meta['routeCode']
        list = []
        for port in SP_SVC_ROUTE_PORT_R:
            list.append({
                'PORT': port['PORT_NM'],
                'ETA': port['ETA'].split(' / ')[0],
                'ETD': port['ETD'].split(' / ')[0],
                'TERMINAL': port['TMN_NM']
            })
        item['DOCKING_LIST'] = list
        yield item

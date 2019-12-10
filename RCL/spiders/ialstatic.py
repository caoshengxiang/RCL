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
    name = 'IALU_STATIC'
    allowed_domains = ['www.interasia.cc']
    start_urls = ['http://www.interasia.cc/content/o_service/routes.aspx?SiteID=2']
    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    headers = {
        'Cookie': '_ga=GA1.2.1466162237.1574247933; ASP.NET_SessionId=0lxrmj55cu0mspb0kke01v55; _gid=GA1.2.979778635.1575532007'
    }

    def parse(self, response):
        doc = pq(response.text)
        content = doc('#content')

        title1_ele = content.find('span.title1')

        logging.info(title1_ele.length)

        for route_index, route in enumerate(title1_ele.items()):
            item = StaticsItem()
            item['ROUTE_PARENT'] = route.text()
            next_tab_id = 'h3[id^=tab{}_]'.format(route_index)
            h3_eles = route.siblings(next_tab_id)

            for h3_ele in h3_eles.items():
                h3_text = h3_ele.text().split(' (')
                item['ROUTE_NAME_EN'] = h3_text[0]
                item['ROUTE_CODE'] = h3_text[1][:-1]

                div = h3_ele.next()
                # table = div.find('table[class="table_style3 routes overview"]')
                trs = div.find('tr')
                list = []
                tr0_tds = trs.eq(0).find('td')
                tr1_tds = trs.eq(1).find('td')
                tr2_tds = trs.eq(2).find('td')
                for td_index, td in enumerate(tr0_tds.items()):
                    if td_index == 0:
                        continue

                    list.append({
                        'PORT': tr0_tds.eq(td_index).text(),
                        'TERMINAL': '',
                        'ETA': tr1_tds.eq(td_index).text(),
                        'ETD': tr2_tds.eq(td_index).text(),
                    })
                item['DOCKING_LIST'] = list
                yield item

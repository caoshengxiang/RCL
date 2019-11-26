# -*- coding: utf-8 -*-
import logging
import re
import time
from pyquery import PyQuery as pq

import scrapy
from scrapy import FormRequest

from RCL.items import PortItem, PortGroupItem, GroupItem


class DjsSpider(scrapy.Spider):
    name = 'djs'
    allowed_domains = ['http://korea.djship.co.kr']
    start_urls = ['http://http://korea.djship.co.kr/']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            'RCL.pipelines.MongoPipeline': 300
        }
    }

    # js死数据
    cn_port = [
        {'value': 'CSH', 'name': 'SHANGHAI'},
        {'value': 'CXG', 'name': 'XINGANG'},
        {'value': 'CNB', 'name': 'NINGBO'},
        {'value': 'CDL', 'name': 'DALIAN'},
        {'value': 'CQD', 'name': 'QINGDAO'},
        {'value': 'HHG', 'name': 'HONGKONG'},
    ]
    other_port = [
        {'value': 'HHG', 'name': 'HONGKONG'},
        {'value': 'KBS', 'name': 'BUSAN'},
        {'value': 'KUL', 'name': 'ULSAN'},
        {'value': 'KIN', 'name': 'INCHEON'},
        {'value': 'VHC', 'name': 'HOCHIMINH'},
        {'value': 'VHP', 'name': 'HAIPONG'},
        {'value': 'VHP', 'name': 'HAIPONG'},
        {'value': 'TBK', 'name': 'BANGKOK'},
        {'value': 'TLC', 'name': 'LAEM CHABANG'},
        {'value': 'JTK', 'name': 'TOKYO'},
        {'value': 'JYH', 'name': 'YOKOHAMA'},
        {'value': 'JNG', 'name': 'NAGOYA'},
        {'value': 'JKB', 'name': 'KOBE'},
        {'value': 'JOS', 'name': 'OSAKA'},
        {'value': 'JMJ', 'name': 'MOJI'},
        {'value': 'JSZ', 'name': 'SHIMIZU'},
        {'value': 'JHT', 'name': 'HAKATA'},
        {'value': 'JKR', 'name': 'KURE'},
        {'value': 'JHB', 'name': 'HIBIKI'},
        {'value': 'JIY', 'name': 'IYOMISHIMA'},
        {'value': 'JTY', 'name': 'TOKUYAMA'},
        {'value': 'JIB', 'name': 'IMABARI'},
        {'value': 'JMZ', 'name': 'MIZUSHIMA'},
        {'value': 'JYK', 'name': 'YOKKAICHI'},
        {'value': 'JKZ', 'name': 'KANAZAWA'},
        {'value': 'JTH', 'name': 'TOYOHASHI'},
        {'value': 'JNT', 'name': 'NIIGATA'},
    ]
    url = 'http://korea.djship.co.kr/dj/servlet/cn.support.action.sub3_1_Action'

    def start_requests(self):
        localtime = time.localtime(time.time())
        year = str(localtime.tm_year)
        month = str(localtime.tm_mon)
        day = str(localtime.tm_mday)

        for request in self.get_calendar(year, month):
            yield request
        # next month
        nextYear = year
        nextMonth = month
        if int(month) + 1 > 12:
            nextYear = str(int(nextYear) + 1)
            nextMonth = '1'
        else:
            nextMonth = str(int(month) + 1)

        for request in self.get_calendar(nextYear, nextMonth):
            yield request

    def get_calendar(self, y, m):
        for cn in self.cn_port:
            for other in self.other_port:
                logging.info(cn)
                logging.debug('时间；pol-pod:{}-{}; {}-{}'.format(y, m, cn['value'], other['value']))
                yield FormRequest(url=self.url,
                                  method='POST',
                                  meta={
                                      'pol': cn['value'],
                                      'polName': cn['name'],
                                      'pod': other['value'],
                                      'podName': other['name'],
                                  },
                                  formdata={
                                      'mode': 'R',
                                      'remode': '',
                                      'SEL_YEAR': y,
                                      'SEL_MONTH': m,
                                      'pol_cd': cn['value'],
                                      'pod_cd': other['value'],
                                      'searchGbn': '1',
                                      'cargoGbn': 'C',
                                  },
                                  dont_filter=True,
                                  callback=self.parse)

    def parse(self, response):
        pItem = PortItem()
        pgItem = PortGroupItem()
        pItem['port'] = response.meta['polName']
        pItem['portCode'] = response.meta['pol']
        yield pItem
        pgItem['portPol'] = response.meta['pol']
        pgItem['portNamePol'] = response.meta['polName']
        pgItem['portPod'] = response.meta['pod']
        pgItem['portNamePod'] = response.meta['podName']
        yield pgItem

        doc = pq(response.text)
        table = doc('body > form > table:nth-child(11) > tr > td > table')
        trs = table.children('tr[height!="30"]')
        for tr in trs.items():
            tds = tr.children('td')
            for td in tds.items():
                try:
                    day = td.children("font:first").text()
                    logging.debug(day)
                    if day and int(day) >= int(time.localtime().tm_mday):
                        aEles = td.find('a')
                        for a in aEles.items():
                            paramHrefStr = a.attr('href')
                            # logging.info(paramHrefStr)
                            if paramHrefStr:
                                reP = re.compile(r'[\'](.*?)[\']', re.S)
                                param = re.findall(reP, paramHrefStr)
                                logging.info(param)
                                yield FormRequest(url=self.url,
                                                  method='POST',
                                                  meta={
                                                      'pol': param[5],
                                                      'polName': response.meta['polName'],
                                                      'pod': param[6],
                                                      'podName': response.meta['podName'],
                                                      'ROUTE_CODE': param[2]
                                                  },
                                                  # ['', 'CJ1', 'MS', '1924', 'E', 'CNSHA', 'HKHKG', '201911230630', 'Y', 'WGQ5', '', '', 'N']
                                                  formdata={
                                                      'PROGRAM_ID': 'sub3_1_0',
                                                      'mode': 'R1',
                                                      'remode': '',
                                                      'ROUTE_CODE': param[1],
                                                      'VESSEL_CODE': param[2],
                                                      'VOYAGE': param[3],
                                                      'BOUND': param[4],
                                                      'LD_PORT': param[5],
                                                      'DC_PORT': param[6],
                                                      'ETD': param[7],
                                                      'VESSEL_NAME': '',
                                                      'TS_GBN': param[8],
                                                      'LD_TERMINAL': param[9],
                                                      'DC_TERMINAL': '',
                                                      'TS_PORT': '',
                                                      'cargoGbn': 'C',
                                                      'CLOSE_YN': param[12],
                                                  },
                                                  dont_filter=True,
                                                  callback=self.parse_detail)
                except Exception as e:
                    pass

    def parse_detail(self, response):
        doc = pq(response.text)
        table = doc('body > form > table.tb_color1')
        # logging.info(table)
        gItem = GroupItem()
        vv = table.find('tr:nth-child(2) > td:nth-child(2)').text().split(' ')
        # logging.info(vv)
        row = {
            'ROUTE_CODE': response.meta['ROUTE_CODE'],
            'ETD': table.find('tr:nth-child(4) > td:nth-child(2)').text(),
            'VESSEL': vv[-1],
            'VOYAGE': ' '.join(vv[:-1]),
            'ETA': '',
            'TRANSIT_TIME': '',  # 无
            'TRANSIT_LIST': [],
            'IS_TRANSIT': 0,  # 确认为中转为1，直达为0, 默认为0
            'pol': response.meta['pol'],
            'pod': response.meta['pod'],
            'polName': response.meta['polName'],
            'podName': response.meta['podName'],
        }
        transit = table.find('tr:nth-child(2) > td:nth-child(6)').text()
        if transit:
            row['IS_TRANSIT'] = 1
            row['ETA'] = table.find('tr:nth-child(10) > td:nth-child(4)').text()
            transit_vv = table.find('tr:nth-child(8) > td:nth-child(2)').text().split(' ')
            row['TRANSIT_LIST'].append({
                'TRANSIT_PORT_EN': table.find('tr:nth-child(2) > td:nth-child(6)').text(),
                'TRANS_VESSEL': transit_vv[-1],
                'TRANS_VOYAGE': ' '.join(transit_vv[:-1]),
            })
        else:
            row['ETA'] = table.find('tr:nth-child(4) > td:nth-child(4)').text()
        logging.info(row)
        for field in gItem.fields:
            if field in row.keys():
                gItem[field] = row.get(field)
        yield gItem

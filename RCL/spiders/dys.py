# -*- coding: utf-8 -*-
import logging
import time

import requests
import scrapy
from scrapy import FormRequest
from pyquery import PyQuery as pq

from RCL.items import PortItem, PortGroupItem, GroupItem


class DysSpider(scrapy.Spider):
    name = 'DYSL'
    allowed_domains = ['http://www.pcsline.co.kr']
    start_urls = ['http://www.pcsline.co.kr/eng/service/schedule.asp']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    global_cn_port = []
    global_other_port = []

    def start_requests(self):
        headers = {
            'Cookie': 'ASPSESSIONIDQCBRCACB=LGMPDMIBHODEEJIBJNKMFNEJ',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.62 Safari/537.36',
        }
        yield FormRequest(url=self.start_urls[0],
                          method='GET',
                          meta={},
                          headers=headers,
                          callback=self.parse)

        # # 测试
        # data = {
        #     'syear': '2019',
        #     'smonth': '12',
        #     'importtype': '1',
        #     'con1': 'CN',
        #     'ld_port': 'CNDLC',
        #     'con2': 'KR',
        #     'ed_port': 'KRPUS',
        #     'action': 'search',
        # }
        # logging.debug(data)
        # yield FormRequest(url=self.start_urls[0],
        #                   method='POST',
        #                   # dont_filter=True,
        #                   meta={
        #                       'pol': 'CNDLC',
        #                       'polName': 'DALIAN',
        #                       'pod': 'KRPUS',
        #                       'podName': 'BUSAN',
        #                   },
        #                   formdata=data,
        #                   callback=self.parse_group)

    def parse(self, response):
        doc = pq(response.text)
        select = doc(
            '#container1 > table > tr > td > table:nth-child(1) > tr > td.contents > form > table.mT10 > tr:nth-child(2) > td > table > tr > td > table > tr:nth-child(4) > td:nth-child(2) > select')
        options = select.find('option')
        # countrys = []
        for option in options.items():
            country = {
                'value': option.attr('value'),
                'name': option.text()
            }
            # countrys.append(country)
            res = requests.post('http://www.pcsline.co.kr/service/ajax_category.asp',
                                data={'CATE1_IDX': country['value']})
            # logging.info(pq(res.text)('#ctl00_CPHContent_ddlDepartureL').find('option'))
            self.parse_port(res, country)

        logging.info('完成所有港口请求')
        logging.info(self.global_cn_port)
        logging.info(self.global_other_port)

        pgItem = PortGroupItem()
        pItem = PortItem()
        for cn in self.global_cn_port:
            pItem['port'] = cn['name']
            pItem['portCode'] = cn['value']
            yield pItem
            for other in self.global_other_port:
                # 港口
                pItem['port'] = other['name']
                pItem['portCode'] = other['value']
                yield pItem
                # 港口组合
                pgItem['portPol'] = cn['value']
                pgItem['portNamePol'] = cn['name']
                pgItem['portPod'] = other['value']
                pgItem['portNamePod'] = other['name']
                yield pgItem

                try:
                    localtime = time.localtime(time.time())
                    year = str(localtime.tm_year)
                    month = str(localtime.tm_mon)
                    data = {
                        'syear': year,
                        'smonth': month,
                        'importtype': '1',
                        'con1': cn['countryVa'],
                        'ld_port': cn['value'],
                        'con2': other['countryVa'],
                        'ed_port': other['value'],
                        'action': 'search',
                    }
                    logging.debug(data)
                    yield FormRequest(url=self.start_urls[0],
                                      method='POST',
                                      dont_filter=True,
                                      meta={
                                          'pol': cn['value'],
                                          'polName': cn['name'],
                                          'pod': other['value'],
                                          'podName': other['name'],
                                      },
                                      formdata=data,
                                      callback=self.parse_group)
                    # next month
                    nextYear = year
                    if int(month) + 1 > 12:
                        nextYear = str(int(nextYear) + 1)
                        nextMonth = '1'
                    else:
                        nextMonth = str(int(month) + 1)

                    data['syear'] = nextYear
                    data['smonth'] = nextMonth

                    logging.debug(data)
                    yield FormRequest(url=self.start_urls[0],
                                      method='POST',
                                      dont_filter=True,
                                      meta={
                                          'pol': cn['value'],
                                          'polName': cn['name'],
                                          'pod': other['value'],
                                          'podName': other['name'],
                                      },
                                      formdata=data,
                                      callback=self.parse_group)
                except Exception as e:
                    logging.error('dys error')
                    logging.error(e)

    def parse_port(self, response, country):
        logging.info('解析港口')
        logging.info(response.text)
        doc = pq(response.text)
        portOptions = doc('select.main_select').find('option')
        ports = []
        for option in portOptions.items():
            va = option.attr('value')
            name = option.text()
            if va != '0':
                ports.append({'value': va, 'name': name, 'countryVa': country['value'], 'countryName': country['name']})
        if country['name'] == 'CHINA':
            self.global_cn_port.extend(ports)
        elif country['name'] == 'HONG KONG':
            self.global_cn_port.extend(ports)
            self.global_other_port.extend(ports)
        else:
            self.global_other_port.extend(ports)
        # logging.info(country)
        # logging.info(ports)

    def parse_group(self, response):
        doc = pq(response.text)
        table = doc('#container1 > table:nth-child(1) > tr > td > table > tr > td.contents > table:nth-child(4)')
        # logging.info(table)
        trs = table.find('tr')
        gItem = GroupItem()
        for index, tr in enumerate(trs.items()):
            try:
                if index == 0:
                    continue
                if tr.find('td').text() == 'No Data.':
                    logging.debug('查询无数据-无数据')
                    continue

                if tr.find('td'):
                    row = {
                        'ETD': tr.find('td').eq(3).text(),
                        'VESSEL': tr.find('td').eq(1).text(),
                        'VOYAGE': tr.find('td').eq(2).text(),
                        'ETA': tr.find('td').eq(5).text(),
                        'TRANSIT_TIME': int(tr.find('td').eq(7).text().replace('Days', '')),
                        'TRANSIT_LIST': [],
                        'IS_TRANSIT': 0,  # 确认为中转为1，直达为0, 默认为0
                        'pol': response.meta['pol'],
                        'pod': response.meta['pod'],
                        'polName': response.meta['polName'],
                        'podName': response.meta['podName'],
                    }
                    for field in gItem.fields:
                        if field in row.keys():
                            gItem[field] = row.get(field)
                    yield gItem
                    logging.info('{}列数据：'.format(index))

                    # 未发现有中转情况
            except Exception as e:
                pass

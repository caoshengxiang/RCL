# -*- coding: utf-8 -*-
import logging
import math
import re
import time

import requests
import scrapy
from pyquery import PyQuery as pq
from scrapy import FormRequest, Request

from RCL.items import PortGroupItem, PortItem, GroupItem


class NamsungSpider(scrapy.Spider):
    name = 'NSRU'
    allowed_domains = ['http://www.namsung.co.kr']
    start_urls = ['http://www.namsung.co.kr/eng/biz/eService/selectSchdulList.do']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    global_cn_port = []
    global_other_port = []
    port_url = ' http://www.namsung.co.kr/eng/biz/eService/AjaxPortList.do?searchGuggaCd={}'
    calendar_url = 'http://www.namsung.co.kr/eng/biz/eService/selectSchdulList.do?searchYear={}&searchMonth={}&searchDateOption={}&searchGuggaCdFrom={}&searchPortCdFrom={}&searchGuggaCdTo={}&searchPortCdTo={}'
    detail_url = 'http://www.namsung.co.kr/eng/biz/eService/AjaxNewViewList.do?searchPortCdFrom={}&searchPortCdTo={}&searchDate={}&searchVslCdTag={}&searchVslvoy={}&searchDateOption={}&searchv_por={}&searchv_otag={}&searchv_oday={}&searchv_ofec={}&searchv_pord={}&searchv_pvy={}&searchv_itag={}&searchv_iday={}&searchv_ifec={}&searchv_pvyd={}&search_lpt={}&search_dpt={}'

    def parse(self, response):
        try:
            doc = pq(response.text)
            options = doc('#searchGuggaCdFrom option')
            for option in options.items():
                country = {
                    'value': option.attr('value'),
                    'name': option.text()
                }
                res = requests.get(self.port_url.format(country['value']))
                self.parse_port(res, country)

            logging.info('完成所有港口请求')
            logging.info(self.global_cn_port)
            logging.info(self.global_other_port)

            pgItem = PortGroupItem()
            pItem = PortItem()

            localtime = time.localtime(time.time())
            year = str(localtime.tm_year)
            month = str(localtime.tm_mon)
            day = str(localtime.tm_mday)

            for cnindex, cn in enumerate(self.global_cn_port):
                # # 测试
                # if cnindex != 13:
                #     continue
                pItem['port'] = cn['name']
                pItem['portCode'] = cn['value']
                yield pItem
                for oincex, other in enumerate(self.global_other_port):
                    # # 测试
                    # if oincex != 0:
                    #     continue
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

                    # 日历数据

                    for request in self.get_calendar(year, month, cn, other, False):
                        yield request
                    # next month
                    nextYear = year
                    nextMonth = month
                    if int(month) + 1 > 12:
                        nextYear = str(int(nextYear) + 1)
                        nextMonth = '1'
                    else:
                        nextMonth = str(int(month) + 1)

                    for request in self.get_calendar(nextYear, nextMonth, cn, other, True):
                        yield request

                    # 测试
                    # for request in self.get_calendar('2019', '12', cn, other, False):
                    #     yield request

        except Exception as e:
            logging.error(e)

    def get_calendar(self, y, m, cn, other, isNextMonth):
        # logging.info(cn)
        # logging.debug('时间；pol-pod:{}-{}; {}-{}'.format(y, m, cn['value'], other['value']))
        yield Request(
            url=self.calendar_url.format(y, m, 'startdate', cn['countryVa'], cn['value'], other['countryVa'],
                                         other['value']),
            method='GET',
            meta={
                'pol': cn['value'],
                'polName': cn['name'],
                'pod': other['value'],
                'podName': other['name'],
                'isNextMonth': isNextMonth,
            },
            dont_filter=True,
            callback=self.parse_calendar)

        # 测试
        # yield Request(
        #     # url='http://www.namsung.co.kr/eng/biz/eService/selectSchdulList.do?searchYear=2019&searchMonth=11&searchDateOption=startdate&searchGuggaCdFrom=CN&searchPortCdFrom=CNJIA&searchGuggaCdTo=JP&searchPortCdTo=JPTBT',
        #     url='http://www.namsung.co.kr/eng/biz/eService/selectSchdulList.do?searchYear=2019&searchMonth=12&searchDateOption=startdate&searchGuggaCdFrom=HK&searchPortCdFrom=HKHKG&searchGuggaCdTo=VN&searchPortCdTo=VNHPH',
        #     method='GET',
        #     meta={
        #         'pol': 'CNJIA',
        #         'polName': 'aa',
        #         'pod': 'JPTBT',
        #         'podName': 'bb',
        #     },
        #     dont_filter=True,
        #     callback=self.parse_calendar)

    def parse_calendar(self, response):
        try:
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
            table = doc('#schdulVO > div > div.calendar > table')
            trs = table.find('tr')
            for tr in trs.items():
                tds = tr.children('td')
                if not tds:
                    logging.info('表头')
                    continue

                for td in tds.items():
                    dayStr = td.text()
                    if dayStr == '':
                        continue

                    if '\n' in dayStr:
                        day = dayStr.splitlines()[0]  # 换行符拆分
                    else:
                        continue
                    isNextMonth = response.meta['isNextMonth']
                    logging.debug(isNextMonth)
                    if response.meta['isNextMonth'] == False:
                        if int(day) < int(time.localtime().tm_mday):
                            continue

                    aEles = td.find('a')
                    for a in aEles.items():
                        paramHrefStr = a.attr('href')
                        # logging.info(paramHrefStr)
                        if paramHrefStr:
                            reP = re.compile(r'[\'](.*?)[\']', re.S)  # 解析 js
                            param = re.findall(reP, paramHrefStr)
                            # [searchPortCdFrom, searchPortCdTo, searchDate, searchVslvoy, searchVslCdTag, searchv_por, searchv_otag, searchv_oday,searchv_ofec,searchv_pord, searchv_pvy, searchv_itag,searchv_iday,searchv_ifec,searchv_pvyd,search_lpt,search_dpt]
                            url = self.detail_url.format(
                                param[0],
                                param[1],
                                param[2],
                                param[4],
                                param[3],
                                'startdate',
                                param[5],
                                param[6],
                                param[7],
                                param[8],
                                param[9],
                                param[10],
                                param[11],
                                param[12],
                                param[13],
                                param[14],
                                param[-2],
                                param[-1])
                            logging.info(url)
                            yield Request(url=url,
                                          method='GET',
                                          meta={
                                              'pol': response.meta['pol'],
                                              'polName': response.meta['polName'],
                                              'pod': response.meta['pod'],
                                              'podName': response.meta['podName'],
                                              'param': param,
                                          },
                                          dont_filter=True,
                                          callback=self.parse_detail)

        except Exception as e:
            logging.error(e)

    def parse_detail(self, response):
        try:
            doc = pq(response.text)
            tables = doc('table')
            # logging.info(table)
            gItem = GroupItem()

            pol_table_index = 0
            tb1 = tables.eq(pol_table_index)
            len1 = tables.eq(pol_table_index).find('tr').length
            if len1 != 6 and len1 != 7:
                pol_table_index += 1

            tb2 = tables.eq(pol_table_index)
            len2 = tables.eq(pol_table_index).find('tr').length
            if len2 != 6 and len2 != 7:
                logging.error('异常需要处理 ')
                return

            vv = tables.eq(pol_table_index).find('tr:nth-child(1) > td:nth-child(2)').text().splitlines()[0]
            timeStr = tables.eq(pol_table_index).find('tr:nth-child(1) > td:nth-child(4)').text()
            if timeStr:
                time = float(timeStr)
            else:
                time = 0
            row = {
                'ETD': tables.eq(pol_table_index).find('tr:nth-child(3) > td:nth-child(2)').text(),
                'VESSEL': vv.split(' / ')[0],
                'VOYAGE': vv.split(' / ')[1],
                'ETA': tables.eq(pol_table_index).find('tr:nth-child(3) > td:nth-child(4)').text(),
                'TRANSIT_TIME': time,
                'TRANSIT_LIST': [],
                'IS_TRANSIT': 0,  # 确认为中转为1，直达为0, 默认为0
                'pol': response.meta['pol'],
                'pod': response.meta['pod'],
                'polName': response.meta['polName'],
                'podName': response.meta['podName'],
            }

            transitTable = doc('table[id^=id_view_]')
            if transitTable:
                for tab in transitTable.items():
                    row['TRANSIT_LIST'] = []
                    vv_t = tab.find('tr:nth-child(1) > td:nth-child(2)').text().splitlines()[0]
                    tra_timeStr = tab.find('tr:nth-child(1) > td:nth-child(4)').text()
                    if tra_timeStr:
                        tra_time = float(tra_timeStr)
                    else:
                        tra_time = 0

                    row['TRANSIT_TIME'] = math.ceil(time + tra_time)
                    row['IS_TRANSIT'] = 1
                    row['ETA'] = tab.find('tr:nth-child(3) > td:nth-child(4)').text()
                    row['TRANSIT_LIST'].append({
                        'TRANSIT_PORT_EN': tab.find('tr:nth-child(2) > td:nth-child(2)').text().split(' ')[0],
                        'TRANS_VESSEL': vv_t.split(' / ')[0],
                        'TRANS_VOYAGE': vv_t.split(' / ')[1]
                    })
                    logging.info(row)
                    for field in gItem.fields:
                        if field in row.keys():
                            gItem[field] = row.get(field)
                    yield gItem
            else:
                row['TRANSIT_TIME'] = math.ceil(time)
                for field in gItem.fields:
                    if field in row.keys():
                        gItem[field] = row.get(field)
                yield gItem

        except Exception as e:
            logging.error(e)

    def parse_port(self, response, country):
        try:
            logging.info('解析港口')
            doc = pq(response.text)
            portOptions = doc('option')
            ports = []
            for option in portOptions.items():
                va = option.attr('value')
                name = option.text()
                ports.append({'value': va, 'name': name, 'countryVa': country['value'], 'countryName': country['name']})
            if country['name'] == 'CHINA':
                self.global_cn_port.extend(ports)
            elif country['name'] == 'HONG KONG':
                self.global_cn_port.extend(ports)
                self.global_other_port.extend(ports)
            else:
                self.global_other_port.extend(ports)
        except Exception as e:
            logging.error(e)

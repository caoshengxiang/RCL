# -*- coding: utf-8 -*-
import logging
import re
import time

import requests
import scrapy
from pyquery import PyQuery as pq
from scrapy import FormRequest, Request

from RCL.items import PortGroupItem, PortItem, GroupItem


class NamsungSpider(scrapy.Spider):
    name = 'namsung'
    allowed_domains = ['http://www.namsung.co.kr']
    start_urls = ['http://www.namsung.co.kr/eng/biz/eService/selectSchdulList.do']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            'RCL.pipelines.MongoPipeline': 300
        }
    }

    global_cn_port = []
    global_other_port = []
    port_url = ' http://www.namsung.co.kr/eng/biz/eService/AjaxPortList.do?searchGuggaCd={}'
    calendar_url = 'http://www.namsung.co.kr/eng/biz/eService/selectSchdulList.do?searchYear={}&searchMonth={}&searchDateOption={}&searchGuggaCdFrom={}&searchPortCdFrom={}&searchGuggaCdTo={}&searchPortCdTo={}'
    detail_url = 'http://www.namsung.co.kr/eng/biz/eService/AjaxNewViewList.do?searchPortCdFrom={}&searchPortCdTo={}&searchDate={}&searchVslCdTag={}&searchVslvoy={}&searchDateOption={}&searchv_por={}&searchv_otag={}&searchv_oday={}&searchv_ofec={}&searchv_pord={}&searchv_pvy={}&searchv_itag={}&searchv_iday={}&searchv_ifec={}&searchv_pvyd={}&search_lpt={}&search_dpt={}'

    def parse(self, response):
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
        for cn in self.global_cn_port:
            pItem['port'] = cn['name']
            pItem['portCode'] = ''
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

                logging.info(cn['countryVa'])
                logging.info(cn['value'])
                logging.info(other['countryVa'])
                logging.info(other['value'])

                # 日历数据
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
        for cn in self.global_cn_port:
            for other in self.global_other_port:
                logging.info(cn)
                logging.debug('时间；pol-pod:{}-{}; {}-{}'.format(y, m, cn['value'], other['value']))
                yield Request(
                    url=self.calendar_url.format(y, m, 'startdate', cn['countryVa'], cn['value'], other['countryVa'],
                                                 other['value']),
                    method='GET',
                    meta={
                        'pol': cn['value'],
                        'polName': cn['name'],
                        'pod': other['value'],
                        'podName': other['name'],
                    },
                    dont_filter=True,
                    callback=self.parse_calendar)

    def parse_calendar(self, response):
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
                try:
                    dayStr = td.text()
                    reDayP = re.compile(r'[\"](.*?)[\"]', re.S)
                    day = re.findall(reDayP, dayStr)[0]
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
                                # ['JPAXT', 'HKHKG', '20191128','JSFR1919W','T','','','0','','','','','0','','','JPAXT','HKHKG']
                                yield Request(url=self.detail_url.format(
                                    param[0],
                                    param[1],
                                    param[2],
                                    param[4],
                                    param[3],
                                    'startdate',
                                    '',
                                    '',
                                    param[7],
                                    '',
                                    '',
                                    '',
                                    '',
                                    param[12],
                                    '',
                                    '',
                                    param[-2],
                                    param[-1],
                                ),
                                    method='GET',
                                    meta={
                                        'pol': '',
                                        'polName': 'SHANGHAI',
                                        'pod': '',
                                        'podName': 'HONGKONG',
                                    },
                                    dont_filter=True,
                                    callback=self.parse_detail)
                except Exception as e:
                    logging.error(e)

    def parse_detail(self, response):
        doc = pq(response.text)
        table = doc('body > form > table.tb_color1')
        # logging.info(table)
        gItem = GroupItem()
        vv = table.find('tr:nth-child(2) > td:nth-child(2)').text().split(' ')
        # logging.info(vv)
        row = {
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

    def parse_port(self, response, country):
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

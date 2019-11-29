# -*- coding: utf-8 -*-
import logging
import time

import requests
import scrapy
from pyquery import PyQuery as pq
from scrapy import FormRequest

from RCL.items import PortGroupItem, PortItem, GroupItem


class TslSpider(scrapy.Spider):
    name = 'tsl'
    allowed_domains = ['http://vgm.tslines.com']
    start_urls = ['http://vgm.tslines.com/VSM/LineServiceByPort.aspx']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            'RCL.pipelines.MongoPipeline': 300
        }
    }

    global_cn_port = []
    global_other_port = []

    localtime = time.localtime(time.time())
    year = str(localtime.tm_year)
    month = str(localtime.tm_mon)
    day = str(localtime.tm_mday)
    if len(day) < 2:
        day = '0' + day

    next2_month = str((int(month) + 2) % 12)
    if len(next2_month) < 2:
        next2_month = '0' + next2_month
    next2_year = (int((int(month) + 2) / 12) + int(year))

    def parse(self, response):
        doc = pq(response.text)
        __EVENTTARGET = doc('#__EVENTTARGET').attr('value')
        __EVENTARGUMENT = doc('#__EVENTARGUMENT').attr('value')
        __LASTFOCUS = doc('#__LASTFOCUS').attr('value')
        __VIEWSTATE = doc('#__VIEWSTATE').attr('value')

        data = {
            '__EVENTTARGET': 'Button2',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': __VIEWSTATE,
            'DropDownList3': 'CN',
            "DropDownList1": 'CNSHA',
            "TextBox3": "{}/{}/{}".format(self.year, self.month, self.day),
            "TextBox5": "{}/{}/{}".format(self.next2_year, self.next2_month, '01'),
            "DropDownList4": 'HK',
            "DropDownList2": 'HKHK1',
            "TextBox4": "",
            "TextBox6": "",
            "DropDownList5": '0'
        }
        logging.info(data)
        yield FormRequest(url=self.start_urls[0],
                          method='POST',
                          dont_filter=True,
                          meta={
                              'pol': 'CN',
                              'polName': 'CNSHA',
                              'pod': 'HK',
                              'podName': 'HKHK1',
                          },
                          formdata=data,
                          callback=self.parse_group)

        return

        options = doc('#DropDownList3 option')
        for option in options.items():
            country = {
                'value': option.attr('value'),
                'name': option.text()
            }
            v = __VIEWSTATE

            res = requests.post(self.start_urls[0],
                                headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.62 Safari/537.36',
                                },
                                data={
                                    '__EVENTTARGET': 'DropDownList3',
                                    '__EVENTARGUMENT': '',
                                    '__LASTFOCUS': '',
                                    '__VIEWSTATE': __VIEWSTATE,
                                    'DropDownList3': country['value'],
                                    "DropDownList1": "CNDLC",
                                    "TextBox3": "{}/{}/{}".format(self.year, self.month, self.day),
                                    "TextBox5": "{}/{}/{}".format(self.next2_year, self.next2_month, '01'),
                                    "DropDownList4": "HK",
                                    "DropDownList2": "HKHK1",
                                    "TextBox4": "",
                                    "TextBox6": "",
                                    "DropDownList5": '0'
                                })
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
                pItem['portCode'] = ''
                yield pItem
                # 港口组合
                pgItem['portPol'] = ''
                pgItem['portNamePol'] = cn['name']
                pgItem['portPod'] = ''
                pgItem['portNamePod'] = other['name']
                yield pgItem

                data = {
                    '__EVENTTARGET': 'Button2',
                    '__EVENTARGUMENT': '',
                    '__LASTFOCUS': '',
                    '__VIEWSTATE': __VIEWSTATE,
                    'DropDownList3': cn['countryVa'],
                    "DropDownList1": cn['value'],
                    "TextBox3": "{}/{}/{}".format(self.year, self.month, self.day),
                    "TextBox5": "{}/{}/{}".format(self.next2_year, self.next2_month, '01'),
                    "DropDownList4": other['countryVa'],
                    "DropDownList2": other['value'],
                    "TextBox4": "",
                    "TextBox6": "",
                    "DropDownList5": '0'
                }
                logging.info(data)
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

    def parse_group(self, response):
        doc = pq(response.text)
        trs = doc('#GridView2 tr')
        gItem = GroupItem()
        for tr in trs.items():
            tds = tr.find('td')
            if not tds:
                continue
            row = {
                'ETD': tds.eq(10).text(),
                'VESSEL': tds.eq(1).text(),
                'VOYAGE': tds.eq(2).text(),
                'ETA': tds.eq(13).text(),
                'ROUTE_CODE': tds.eq(0).text(),
                'TRANSIT_TIME': tds.eq(14).text(),
                'POL_TERMINAL': tds.eq(4).text(),
                'POD_TERMINAL': tds.eq(12).text(),
                'TRANSIT_LIST': [],
                'IS_TRANSIT': 0,  # 确认为中转为1，直达为0, 默认为0
                'pol': response.meta['pol'],
                'pod': response.meta['pod'],
                'polName': response.meta['polName'],
                'podName': response.meta['podName'],
            }
            logging.info(row)
            for field in gItem.fields:
                if field in row.keys():
                    gItem[field] = row.get(field)
            yield gItem

    def parse_port(self, response, country):
        logging.info('解析港口')
        logging.info(response.text)
        doc = pq(response.text)
        portOptions = doc('#DropDownList1').find('option')
        ports = []
        for option in portOptions.items():
            va = option.attr('value')
            name = option.text()
            # if va != '0':
            ports.append({'value': va, 'name': name, 'countryVa': country['value'], 'countryName': country['name']})
        if country['value'] == 'CN':
            self.global_cn_port.extend(ports)
        elif country['value'] == 'HK':
            self.global_cn_port.extend(ports)
            self.global_other_port.extend(ports)
        else:
            self.global_other_port.extend(ports)
        # logging.info(country)
        logging.info(ports)

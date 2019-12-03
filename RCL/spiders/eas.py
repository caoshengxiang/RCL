# -*- coding: utf-8 -*-
import datetime
import json
import logging
import time

import requests
import scrapy
from scrapy import FormRequest, Request
from pyquery import PyQuery as pq

from RCL.items import PortItem, PortGroupItem, GroupItem


class EasSpider(scrapy.Spider):
    name = 'EASC'
    allowed_domains = ['http://ecomm.easline.com']
    start_urls = ['http://ecomm.easline.com/ecomm/ecxmm/weBBSys/Ssch/wecmBBSschP2PtFrame.aspx']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            'RCL.pipelines.MongoPipeline': 300
        }
    }

    __VIEWSTATE = ''
    __EVENTVALIDATION = ''

    portUrl = 'http://ecomm.easline.com/ecomm/ecxmm/weBBSys/Ssch/wecmBBSschP2PtFrame.aspx/select_wecomBBSschP2PtFramePortList'

    num = 0

    def parse(self, response):
        doc = pq(response.text)
        self.__VIEWSTATE = doc('#__VIEWSTATE').attr('value')
        self.__EVENTVALIDATION = doc('#__EVENTVALIDATION').attr('value')
        logging.info(self.__VIEWSTATE)
        logging.info(self.__EVENTVALIDATION)

        # re = requests.post(self.portUrl, data=json.dumps({'portname': '', 'inoutflag': 'out'}),
        #                    headers={
        #                        'Accept': 'application/json, text/javascript, */*; q=0.01',
        #                        'Cookie': 'ASP.NET_SessionId=scidcwoqbbwbu4laxqrwqorj',
        #                        'X-Requested-With': 'XMLHttpRequest',
        #                        'Content-Type': 'application/json',
        #                    })
        # logging.info(re)

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cookie': 'ASP.NET_SessionId=scidcwoqbbwbu4laxqrwqorj',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        }
        yield Request(url=self.portUrl,
                      dont_filter=True,
                      method='POST',
                      body=json.dumps({'portname': '', 'inoutflag': 'out'}),
                      headers=headers,
                      callback=self.parse_port)

    def parse_port(self, response):
        portList = json.loads(response.text).get('d')
        logging.info('港口')
        logging.info(portList)
        pgItem = PortGroupItem()
        pItem = PortItem()
        for index, item in enumerate(portList):
            pItem['port'] = item
            pItem['portCode'] = ''
            yield pItem
            if index + 1 < len(portList):
                for jItem in portList[index + 1:]:
                    # 港口组合
                    pgItem['portPol'] = ''
                    pgItem['portNamePol'] = item
                    pgItem['portPod'] = ''
                    pgItem['portNamePod'] = jItem
                    yield pgItem

                    if self.__VIEWSTATE == '' or self.__EVENTVALIDATION == '':
                        logging.error('参数 未正确获取')
                        break
                    localtime = time.localtime(time.time())
                    year = str(localtime.tm_year)
                    month = str(localtime.tm_mon)
                    day = str(localtime.tm_mday)

                    now = datetime.datetime.now()
                    days = 31 - int(day) + 30
                    delta = datetime.timedelta(days=days)
                    n_days = now + delta

                    data = {
                        '__EVENTTARGET': '',
                        '__EVENTARGUMENT': '',
                        '__VIEWSTATE': self.__VIEWSTATE,
                        '__EVENTVALIDATION': self.__EVENTVALIDATION,
                        'hid_Pol': '',
                        'hid_Pod': '',
                        'hid_ClickDiv': '1',
                        'txt_Pol': item,
                        'cmb_Year': year,
                        'cmb_Month': month,
                        'txt_Pod': jItem,
                        'A': 'rdo_Date',
                        'txt_EtdFrom': '{}-{}-{}'.format(year, month, day),
                        'txt_EtdTo': n_days.strftime('%Y-%m-%d'),
                        'cmb_Type': 'All',
                        'btn_Load': 'Search',
                    }

                    yield FormRequest(url=self.start_urls[0],
                                      method='POST',
                                      dont_filter=True,
                                      meta={
                                          'pol': '',
                                          'polName': item,
                                          'polVal': '',
                                          'pod': '',
                                          'podName': jItem,
                                          'podVal': '',
                                      },
                                      formdata=data,
                                      callback=self.parse_group)

    def parse_group(self, response):
        self.num += 1
        logging.info('{}-{};接口数：{}'.format(response.meta['polName'], response.meta['podName'], self.num))

        doc = pq(response.text)
        trs = doc('#grd_List tr')
        gItem = GroupItem()
        for ind, tr in enumerate(trs.items()):
            if ind == 0:
                continue

            if tr.find('td'):
                tds = tr.find('td')
                row = {
                    'ROUTE_CODE': tds.eq(1).text(),
                    'ETD': tds.eq(6).text(),
                    'VESSEL': tds.eq(2).text(),
                    'VOYAGE': tds.eq(3).text(),
                    'ETA': tds.eq(9).text(),
                    'TRANSIT_TIME': '',
                    'TRANSIT_LIST': [],
                    'IS_TRANSIT': 0,  # 确认为中转为1，直达为0, 默认为0
                    'pol': '',
                    'pod': '',
                    'polName': tds.eq(4).text(),
                    'podName': tds.eq(7).text(),
                    'POL_TERMINAL': tds.eq(5).text(),
                    'POD_TERMINAL': tds.eq(8).text(),
                }
                for field in gItem.fields:
                    if field in row.keys():
                        gItem[field] = row.get(field)
                yield gItem
                logging.info('{}列数据：{}'.format(ind, row))

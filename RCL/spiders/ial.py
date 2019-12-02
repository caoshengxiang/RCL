# -*- coding: utf-8 -*-
import json
import logging
import time

import requests
import scrapy

from pyquery import PyQuery as pq
from scrapy import Request, FormRequest

from RCL.items import PortItem, PortGroupItem, GroupItem


class IalSpider(scrapy.Spider):
    name = 'ial'
    allowed_domains = ['www.interasia.cc']
    start_urls = ['http://www.interasia.cc/content/c_service/sailing_schedule.aspx?SiteID=1']
    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            'RCL.pipelines.MongoPipeline': 300
        }
    }
    currentDate = time.strftime('%d/%m/%Y', time.localtime())

    formData = {
        '__EVENTTARGET': 'ctl00$CPHContent$ddlDepartureC',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': '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',
        '__VIEWSTATEGENERATOR': '',
        '__SCROLLPOSITIONX': '0',
        '__SCROLLPOSITIONY': '200',
        '__VIEWSTATEENCRYPTED': '',
        '__EVENTVALIDATION': 'DFssQH2GJSy3lm6XvV8Xir42nYpAgDFZuZKlawPptbZa6c1cvAiYois/EjjipjbVAnx3zTsGmCdqJzbHbz+JUr6868gkFtRJLvYNqQKo1yUW2QuxaKDzgNSwWi/U1b2JlFecmQ8wMku1XDw33QausP7J3gi0JiY8U6BeaDuttDPyfOhliDiiDZjiams2RXP+8E1rPKX5SmFXjzDOt4/35PDHTOai6lp9Nh2hP7kDFL6Wj/sfIDTySWgvfpY/Q9whNOhcpOtokxH9lX8uKKsveuloEEukFpnqZUKtnDtis4Cz2M3MvdsdJ3hMugzfne0DYLpcnc6ygY+bmoJ4becns7xOJkZWModaVgTPIN2VTyygdl18uqrBIDGszdg4lNcMbEbzAFKnT+7jYH9nIJq5tcOB2oS44hlRtxNO2Iic1o0hNQ6C',
        'ctl00$UCHeader$txtSearch': 'Search',
        'ctl00$CPHContent$ddlDepartureC': '7',
        'ctl00$CPHContent$ddlDepartureL': '0',
        'ctl00$CPHContent$ddlDestinationC': '0',
        'ctl00$CPHContent$ddlDestinationL': '0',
        'ctl00$CPHContent$txtCode': ''
    }

    headers = {
        'Cookie': '_ga=GA1.2.1466162237.1574247933; _gid=GA1.2.1407016586.1574247933; ASP.NET_SessionId=sofovbanm4lgyy552bcrft55; _gat=1',
        'Host': 'www.interasia.cc',
        'Referer': 'http://www.interasia.cc/content/c_service/sailing_schedule.aspx?SiteID=1',
    }
    data2 = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': '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',
        # '__VIEWSTATE': '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',
        '__VIEWSTATEGENERATOR': '99DD0D69',
        '__SCROLLPOSITIONX': '0',
        '__SCROLLPOSITIONY': '300',
        '__VIEWSTATEENCRYPTED': '',
        '__EVENTVALIDATION': 'SpGVCeurLXSkmoo17hSd4U5/bftj+4GormeLvC4p2q1Gm14+7p0uPgiLblCc1InJ4lr/zfBX/FVa5Se9UOR442jRGWFx2SS+2twBTX5MQbZkZE3ppB5yju1ieHEvKIkUZv5CRYc8sOhAhcPVFxkIMeKqcIedcYV4r2mG5ITSuOGJkdUoRxTJw04XM1N6/DO7DlcFJY129L9tPJPFXDXiLnbQUY6S4APa8AjMVrdPX4xo5wnduMCMyLBVzy9Gz1qx5O2l8be5H0JExfhswl+2Dd8DBcEwsZQqEzdpXQmxkYz8pe0m1nCrWRr7lS0ROS/dY71Lt6fU4Q++wodwKYeTMwtde66gX+hjaYyyzPGjV+c8it4xuCOlgOWcGalD94hZx/z0qjS7Pdk9SmA6UICbTLlQrEDlkVo4wLs2WPjv5wBJbMwNzH5EsA4q+4xKJOqRrafrU21m0judb2gj2EmCZ2+I/bQ=',
        # '__EVENTVALIDATION': 'IYjXpdE1tTTdDh1Z20oBbmz42m9uzbNeyzAzfYuZA9MM5QURyzAUXb5MoBr1+M/biccq6xj3EIerLRmFE+L388R0sT4poBhmLT3H7cfxLIqn+94/opxhzD+JAeptuL+zqoVeuKWERDedXAYMqyhYY/iR6roG00Bce4QKvQ47cJKaQ0JmtpB4KeBpBu5hjDwClmVyBWt7fefH6Z86VeEpRK7duEinQf/Ky8Qv4gO1DI5IUdpAaQhEriwKfr1X7OPH42/54MR+lSMd42/UgqJNGBf3EksTegTOpm/o4TBV/bmkGTKUDT9drhF+m4YQ0aF2bOCq/JGRXQOapGy0SICZcCzwAYvMrKpJ7wVNIVP0hOGxbOVhGtWJIw6pII+MMKEA+ESRrZz9Z2y+QiijD4Yq5OoXjnQkhNQhkD8buhnTQfTTyn2Bgc50xk0v03Ves/5N/ydXhw==',
        'ctl00$UCHeader$txtSearch': 'Search',
        'ctl00$CPHContent$ddlDepartureC': '7',
        'ctl00$CPHContent$ddlDepartureL': '8',
        'ctl00$CPHContent$ddlDestinationC': '710202045201314334',  # 11
        'ctl00$CPHContent$ddlDestinationL': '2016053012211837129',  # 12
        'ctl00$CPHContent$txtCode': 'MRSQ',
        # 'ctl00$CPHContent$txtCode': 'v9tz',
        'ctl00$CPHContent$btnSend': 'Search',
    }

    global_cn_port = []
    global_other_port = []

    # def start_requests(self):
    #     # 测试
    #     self.data2['ctl00$CPHContent$ddlDepartureC'] = '11'
    #     self.data2['ctl00$CPHContent$ddlDepartureL'] = '12'
    #     self.data2['ctl00$CPHContent$ddlDestinationC'] = '13'
    #     self.data2['ctl00$CPHContent$ddlDestinationL'] = '15'
    #     yield FormRequest(url=self.start_urls[0],
    #                       method='POST',
    #                       meta={
    #                           'dont_redirect': True,
    #                           'handle_httpstatus_list': [302],
    #                           'pol': '',
    #                           'polName': 'HONG KONG',
    #                           'polVal': '12',
    #                           'pod': '',
    #                           'podName': 'DA NANG',
    #                           'podVal': '15',
    #                       },
    #                       formdata=self.data2,
    #                       headers=self.headers,
    #                       callback=self.parse_group)

    def parse(self, response):
        doc = pq(response.text)
        countryOptions = doc('#ctl00_CPHContent_ddlDepartureC').find('option')
        countrys = []
        for option in countryOptions.items():
            va = option.attr('value')
            name = option.text()
            if va != '0':
                countrys.append({'value': va, 'name': name})
        logging.info('国家解析完成。')
        logging.info(countrys)
        for country in countrys:
            logging.info('请求国家:{}-港口数据'.format(country['name']))
            self.formData['ctl00$CPHContent$ddlDepartureC'] = country['value']
            res = requests.post(self.start_urls[0], data=self.formData)
            # logging.info(pq(res.text)('#ctl00_CPHContent_ddlDepartureL').find('option'))
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
                self.data2['ctl00$CPHContent$ddlDepartureC'] = cn['countryVa']
                self.data2['ctl00$CPHContent$ddlDepartureL'] = cn['value']
                self.data2['ctl00$CPHContent$ddlDestinationC'] = other['countryVa']
                self.data2['ctl00$CPHContent$ddlDestinationL'] = other['value']
                logging.info(cn['countryVa'])
                logging.info(cn['value'])
                logging.info(other['countryVa'])
                logging.info(other['value'])
                # 注意formData value 不能是数字
                yield FormRequest(url=self.start_urls[0],
                                  method='POST',
                                  # dont_filter=True,
                                  meta={
                                      'pol': '',
                                      'polName': cn['name'],
                                      'polVal': cn['value'],
                                      'pod': '',
                                      'podName': other['name'],
                                      'podVal': other['value'],
                                  },
                                  formdata=self.data2,
                                  headers=self.headers,
                                  callback=self.parse_group)

    def get_params(self, response):
        doc = pq(response.text)
        self.data2['__VIEWSTATE'] = doc('#__VIEWSTATE').attr('value')
        self.data2['__EVENTVALIDATION'] = doc('#__EVENTVALIDATION').attr('value')
        self.data2['ctl00$CPHContent$txtCode'] = doc('#ctl00_CPHContent_imgCode').attr('src').split('=')[1]

    def parse_port(self, response, country):
        # logging.info('解析港口')
        doc = pq(response.text)
        portOptions = doc('#ctl00_CPHContent_ddlDepartureL').find('option')
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
        gItem = GroupItem()
        doc = pq(response.text)
        trs = doc('#ctl00_CPHContent_Panel2 .table_style2').find('tr')
        # logging.warning(response.text)
        for index, tr in enumerate(trs.items()):
            logging.info('数据长度：{}'.format(tr.find('td').length))
            if tr.find('td'):
                row = {
                    'ETD': tr.find('td').eq(0).text(),
                    'VESSEL': tr.find('td').eq(1).text(),
                    'VOYAGE': tr.find('td').eq(2).text(),
                    'ETA': tr.find('td').eq(4).text(),
                    'TRANSIT_TIME': tr.find('td').eq(8).text(),
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
                logging.info('{}列数据：'.format(index + 1))

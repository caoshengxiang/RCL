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
        # '__VIEWSTATE': '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',
        '__VIEWSTATE': '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',
        '__VIEWSTATEGENERATOR': '99DD0D69',
        '__SCROLLPOSITIONX': '0',
        '__SCROLLPOSITIONY': '300',
        '__VIEWSTATEENCRYPTED': '',
        # '__EVENTVALIDATION': 'y0pPJCXJvgDYRIQSO8mv4wZY2ZN2ThVIG8tw880kXn/tWzxueGTrWjpm4hZBXFZwg4TatCFf1os02d8zWTE3XzIiAKNC77haImeV1eEDriTF2lQZgQhR3IrpzUvPHrV4sydT0DL7tEAFgpB5LBVLYXApbp2OgWpT+wt984dsSuGeByEfmmAjkThVTneutKLixjaX0gLD5SADgVov1yC3uHsP3LpkQwOmnoAJCokDSOnPNp1zH+Xy5Df/IdCM/O41AsA7g31drTGMrY0d00NwQVVc4pvxJStfz6HCLYCzIFOrsZT3ILdivhEdCRL0sInD8+IieHo51ew85nQY+8yyURdcZSOQbVN3weH4lBs1SjDi5FtS6q76QC604Rxpgj2dcHGRyYLZSWOWNP0hhuvMMBl2Pa08OXH6dAarR3aS7zqgzERzLmckVGxbZvJ/nCjeARjWU8ji6CTC7WB+grrcLXJZVok=',
        '__EVENTVALIDATION': 'SpGVCeurLXSkmoo17hSd4U5/bftj+4GormeLvC4p2q1Gm14+7p0uPgiLblCc1InJ4lr/zfBX/FVa5Se9UOR442jRGWFx2SS+2twBTX5MQbZkZE3ppB5yju1ieHEvKIkUZv5CRYc8sOhAhcPVFxkIMeKqcIedcYV4r2mG5ITSuOGJkdUoRxTJw04XM1N6/DO7DlcFJY129L9tPJPFXDXiLnbQUY6S4APa8AjMVrdPX4xo5wnduMCMyLBVzy9Gz1qx5O2l8be5H0JExfhswl+2Dd8DBcEwsZQqEzdpXQmxkYz8pe0m1nCrWRr7lS0ROS/dY71Lt6fU4Q++wodwKYeTMwtde66gX+hjaYyyzPGjV+c8it4xuCOlgOWcGalD94hZx/z0qjS7Pdk9SmA6UICbTLlQrEDlkVo4wLs2WPjv5wBJbMwNzH5EsA4q+4xKJOqRrafrU21m0judb2gj2EmCZ2+I/bQ=',
        'ctl00$UCHeader$txtSearch': 'Search',
        'ctl00$CPHContent$ddlDepartureC': '7',
        'ctl00$CPHContent$ddlDepartureL': '8',
        'ctl00$CPHContent$ddlDestinationC': '710202045201314334',  # 11
        'ctl00$CPHContent$ddlDestinationL': '2016053012211837129',  # 12
        'ctl00$CPHContent$txtCode': 'MRSQ',
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

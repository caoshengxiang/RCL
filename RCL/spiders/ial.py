# -*- coding: utf-8 -*-
import json
import logging
import time

import requests
import scrapy

from pyquery import PyQuery as pq
from scrapy import Request, FormRequest

from RCL.items import PortItem, PortGroupItem


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
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Connection': 'keep-alive',
        # 'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': '__ga=GA1.2.1466162237.1574247933; _gid=GA1.2.1407016586.1574247933; ASP.NET_SessionId=ym3rqfmwcpblnzqiqdb5lp2l; _gat=1',
        'Host': 'www.interasia.cc',
        'Referer': 'http://www.interasia.cc/content/c_service/sailing_schedule.aspx?SiteID=1',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.62 Safari/537.36',
    }
    data2 = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        # '__VIEWSTATE': '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',
        '__VIEWSTATE': '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',
        '__VIEWSTATEGENERATOR': '99DD0D69',
        '__SCROLLPOSITIONX': '0',
        '__SCROLLPOSITIONY': '200',
        '__VIEWSTATEENCRYPTED': '',
        # '__EVENTVALIDATION': 'p5RM/SZCLxH94lJLGYlc0U1w7UoewDNeA+0jVVHabY2pEFAH1/FTOGLMmydE63x8bDVWEpYRYcy1aGoRKShj98lWvFnKc7YG9wsewF1NLxN0HxI7WjZGaUeRlT8qLg4QswA/zT1nQmqyTX6ZX+bCc9mkxMC/UpQbJJitvXDQxKC2m98Jlfqi70FFKnuAml/DiO4hXjwWJHPJe0rGoRpuce5EszJXIODdtWtyCSqgy44LcvBhqWfyz5smuNht8D5uwqEcnJuE700Vp0liuSHK6EJRjV6pKWXNYGJnBk7z7qBggPPgl5IbXkZzBZyRUYYIbaJ4DonZ8J7DyNMnXQbIjbWaxov999fUMt0ZgXZwkRcILrr0EbPmsH9bWoXqW4DNAMZJY7BN7ENebXqp/ir3SH9hl7n9zC5HbJP2D6hfXQouF2ekW6mSFTf35wCKMTNe1lZsZ0DbWjUsCYnqfwjqYxMEnXA=',
        '__EVENTVALIDATION': 'ics25HCH259TxedvNxJvATFZFIMXiBvubEW14fB6yLYPba8CtJj9t2G7d9frs8ZUXqku6CjikcmLnK2iggf5eZy7CsxFyLGsOAsAP6zneH1+c0EO98irP0pYHucWZSwXfPKSU94Umlo/56W0CrrkmyPulkfRbtlh1a4U2U+vLdxLB75f8lxung3TzWIlrWtgwY1sQBiOjsc4JiPkbBcvl11SCxtMexk/LQcnEY0D++Td7s/XKfAgpDJg9xVKdBCBFnfXZoCWX7aOUvl6ZxB1Ib8a8FUL/2OHROJBGNyB8C+5N6hKKQ0IF2tJSqdyyeM2yPcvsIVUx0x+8E1QK4uoRR30GXKFPP6Uxz3F5BCcYE2k/C10GF5KPnGx7xLr7N4F8uOkL1CpxeTAaZDUdkp5ddmiDT8THjKfPaeNJ8S56dGgilMy2bvBQwGMUqGWkLF2AFZJMvGwjSBOG3ebBM7lAk/+aJCu9xAgnpg4BbUoHoeA29W54YY0HdUiGIcEPgAU19arEw==',
        'ctl00$UCHeader$txtSearch': 'Search',
        'ctl00$CPHContent$ddlDepartureC': '7',
        'ctl00$CPHContent$ddlDepartureL': '8',
        'ctl00$CPHContent$ddlDestinationC': '710202045201314334',  # 11
        'ctl00$CPHContent$ddlDestinationL': '2016053012211837129',  # 12
        'ctl00$CPHContent$txtCode': 'ZFW7',
        'ctl00$CPHContent$btnSend': 'Search',
    }

    global_cn_port = []
    global_other_port = []

    # def start_requests(self):
    #     # 测试
    # yield FormRequest(url=self.start_urls[0],
    #                   method='POST',
    #                   # dont_filter=True,
    #                   meta={
    #                       'pol': '',
    #                       'polName': 'SHANGHAI',
    #                       'pod': '',
    #                       'podName': 'HONG KONG',
    #                   },
    #                   formdata=self.data2,
    #                   headers=self.headers,
    #                   callback=self.parse_group)

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
            res = requests.post(self.start_urls[0], data=self.formData) # ??????????????
            self.parse_port(res, country)

        logging.info('完成所有港口请求')
        logging.info(self.global_cn_port)
        logging.info(self.global_other_port)

        pgItem = PortGroupItem()
        for cn in self.global_cn_port:
            for other in self.global_other_port:
                pgItem['portPol'] = ''
                pgItem['portNamePol'] = cn['name']
                pgItem['portPod'] = ''
                pgItem['portNamePod'] = other['name']
                yield pgItem
                self.data2['ctl00$CPHContent$ddlDepartureC'] = cn['countryVa']
                self.data2['ctl00$CPHContent$ddlDepartureL'] = cn['value']
                self.data2['ctl00$CPHContent$ddlDestinationC'] = other['countryVa']
                self.data2['ctl00$CPHContent$ddlDestinationL'] = other['value']
                logging.info(self.data2)
                # 注意formData value 不能是数字
                yield FormRequest(url=self.start_urls[0],
                                  method='POST',
                                  # dont_filter=True,
                                  meta={
                                      'pol': '',
                                      'polName': cn['name'],
                                      'pod': '',
                                      'podName': other['name'],
                                  },
                                  formdata=self.data2,
                                  headers=self.headers,
                                  callback=self.parse_group)

    def parse_port(self, response, country):
        logging.info('解析港口')
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
        logging.info(country)
        logging.info(ports)

    def parse_group(self, response):
        doc = pq(response.text)
        trs = doc('#ctl00_CPHContent_Panel2 .table_style2').find('tr')
        for index, tr in enumerate(trs.items()):
            logging.info(tr.find('td').length)
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
                logging.info('{}列数据：'.format(index + 1))
                logging.info(row)

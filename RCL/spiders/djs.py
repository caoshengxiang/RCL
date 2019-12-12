# -*- coding: utf-8 -*-
import logging
import re
import time
from pyquery import PyQuery as pq

import scrapy
from scrapy import FormRequest

from RCL.items import PortItem, PortGroupItem, GroupItem


def GetMiddleStr(content, startStr, endStr):
    patternStr = r'%s(.+?)%s' % (startStr, endStr)
    p = re.compile(patternStr, re.IGNORECASE)
    m = re.findall(p, content)
    if m:
        return m[0]


class DjsSpider(scrapy.Spider):
    name = 'DJSL'
    allowed_domains = ['http://korea.djship.co.kr']
    start_urls = ['http://http://korea.djship.co.kr/']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    # js死数据
    cn_port = [
        {'value': 'CSH', 'name': 'SHANGHAI', 'countryVa': '', 'countryName': ''},
        {'value': 'CXG', 'name': 'XINGANG', 'countryVa': '', 'countryName': ''},
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
        if int(month) + 1 > 12:
            nextYear = str(int(nextYear) + 1)
            nextMonth = '1'
        else:
            nextMonth = str(int(month) + 1)

        for request in self.get_calendar(nextYear, nextMonth):
            yield request

        # # 测试
        # # param = ['', 'KCJ', 'DJ', '1948', 'E', 'CNSHA', 'KRPUS', '201912060530', '', 'WGQ5', '', '', 'N'] # 不中转
        # param = ['', 'KCJ', 'DJ', '1948', 'E', 'CNSHA', 'JPTYO', '201912060530', 'Y', 'WGQ5', '', '', 'N'] # 中转
        # logging.info(param)
        # yield FormRequest(url=self.url,
        #                   method='POST',
        #                   meta={
        #                       'pol': param[5],
        #                       'polName': 'SHANGHAI',
        #                       'pod': param[6],
        #                       # 'podName': 'BUSAN',
        #                       'podName': 'TOKYO',
        #                       'ROUTE_CODE': param[1]
        #                   },
        #                   formdata={
        #                       'PROGRAM_ID': 'sub3_1_0',
        #                       'mode': 'R1',
        #                       'remode': '',
        #                       'ROUTE_CODE': param[1],
        #                       'VESSEL_CODE': param[2],
        #                       'VOYAGE': param[3],
        #                       'BOUND': param[4],
        #                       'LD_PORT': param[5],
        #                       'DC_PORT': param[6],
        #                       'ETD': param[7],
        #                       'VESSEL_NAME': '',
        #                       'TS_GBN': param[8],
        #                       'LD_TERMINAL': param[9],
        #                       'DC_TERMINAL': '',
        #                       'TS_PORT': '',
        #                       'cargoGbn': 'C',
        #                       'CLOSE_YN': param[12],
        #                   },
        #                   dont_filter=True,
        #                   callback=self.parse_detail)

    def get_calendar(self, y, m):
        for cn in self.cn_port:
            for other in self.other_port:
                logging.info(cn)
                logging.debug('时间；pol-pod:{}-{}; {}-{}'.format(y, m, cn['value'], other['value']))
                yield FormRequest(url=self.url,
                                  method='POST',
                                  meta={
                                      'pol': '',
                                      'polName': cn['name'],
                                      'pod': '',
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
                                                      'ROUTE_CODE': param[1]
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
        # 港口和港口组合 如果连续连个月日历都没有数据 会不存。 待下次查询到数据补上（这样做原因是下拉得港口取不到五字码，只能在详情里面取）
        pItem = PortItem()
        pgItem = PortGroupItem()

        pItem['port'] = response.meta['polName']
        pItem['portCode'] = response.meta['pol']
        yield pItem

        pItem['port'] = response.meta['podName']
        pItem['portCode'] = response.meta['pod']
        yield pItem

        pgItem['portPol'] = response.meta['pol']
        pgItem['portNamePol'] = response.meta['polName']
        pgItem['portPod'] = response.meta['pod']
        pgItem['portNamePod'] = response.meta['podName']
        yield pgItem

        doc = pq(response.text)
        table = doc('body > form > table.tb_color1')
        trs_len = table.find('tr').length
        base_num = 6
        step_num = int((trs_len - 1) / base_num)
        gItem = GroupItem()
        vv = table.find('tr:nth-child(2) > td:nth-child(2)').text().split('\xa0')
        logging.info(vv)
        row = {
            'ROUTE_CODE': response.meta['ROUTE_CODE'],
            'ETD': table.find('tr:nth-child(4) > td:nth-child(2)').text(),
            'VESSEL': vv[0],
            'VOYAGE': vv[1],
            'ETA': '',
            'TRANSIT_TIME': 0,  # 无
            'TRANSIT_LIST': [],
            'IS_TRANSIT': 0,  # 确认为中转为1，直达为0, 默认为0
            'pol': response.meta['pol'],
            'pod': response.meta['pod'],
            'polName': response.meta['polName'],
            'podName': response.meta['podName'],
        }

        if step_num > 1:
            row['IS_TRANSIT'] = 1
            for num in range(1, step_num):
                eta = table.find('tr').eq(3 + base_num * num).find('td').eq(3).text()
                row['ETA'] = eta
                transit_vv = table.find('tr').eq(1 + base_num * num).find('td').eq(1).text().split('\xa0')
                row['TRANSIT_LIST'].append({
                    'TRANSIT_PORT_EN': table.find('tr').eq(1 + base_num * (num - 1)).find('td').eq(5).text(),
                    'TRANS_VESSEL': transit_vv[0],
                    'TRANS_VOYAGE': transit_vv[1],
                })


        else:
            row['ETA'] = table.find('tr:nth-child(4) > td:nth-child(4)').text()
        logging.info(row)
        for field in gItem.fields:
            if field in row.keys():
                gItem[field] = row.get(field)
        yield gItem

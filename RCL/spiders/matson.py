# -*- coding: utf-8 -*-
import datetime
import json
import logging

import scrapy
from pyquery import PyQuery as pq
from scrapy import Request, FormRequest

from RCL.items import PortGroupItem, PortItem, GroupItem


class MatsonSpider(scrapy.Spider):
    name = 'MATS'
    allowed_domains = ['https://www.matson.com']
    start_urls = ['https://www.matson.com/matnav/schedules/interactive_vessel_schedule.html']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    def parse(self, response):
        doc = pq(response.text)
        options = doc('#origin-locationCode option')
        pItem = PortItem()
        for option in options.items():
            logging.info(option.attr('value') is None)
            if option.attr('value') is None:
                continue
            row = {
                'value': option.attr('value'),
                'name': option.text()
            }
            logging.info('港口数据：{}'.format(row))
            pItem['port'] = row['name']
            pItem['portCode'] = ''
            yield pItem

            # yield Request(url=self.portUrl,
            #               dont_filter=True,
            #               method='POST',
            #               body=json.dumps({'portname': '', 'inoutflag': 'out'}),
            #               headers=headers,
            #               callback=self.parse_port)

            yield FormRequest(url='https://www.matson.com/wp-content/plugins/matson-plugin/Api_calls/destinations.php',
                              method='POST',
                              dont_filter=True,
                              meta={
                                  'polName': row['name'],
                                  'origin': row['value']
                              },
                              formdata={'origin': row['value']},
                              callback=self.parse_pod)

    def parse_pod(self, response):
        data = json.loads(response.text)
        logging.info(data)
        pgItem = PortGroupItem()
        for item in data:
            # 港口组合
            logging.info('港口组合:')
            pgItem['portPol'] = ''
            pgItem['portNamePol'] = response.meta['polName']
            pgItem['portPod'] = ''
            pgItem['portNamePod'] = item.get('locationName')
            yield pgItem

            today = datetime.date.today()
            nex = today + datetime.timedelta(62 - today.day)

            yield FormRequest(url='https://www.matson.com/wp-content/plugins//matson-plugin/Api_calls/search.php',
                              method='POST',
                              dont_filter=True,
                              meta={
                                  'selectedOrigin': response.meta['origin'],
                                  'selectedDestination': item['locationCode'],
                              },
                              formdata={
                                  'selectedOrigin': response.meta['origin'],
                                  'selectedDestination': item['locationCode'],
                                  'selectedStartDate': today.strftime("%m%d%Y"),
                                  'selectedEndDate': nex.strftime("%m%d%Y"),
                              },
                              callback=self.parse_list)

    def parse_list(self, response):
        data = json.loads(response.text)
        logging.info('查询列表')
        logging.info(data)
        for item in data:
            yield FormRequest(url='https://www.matson.com/wp-content/plugins//matson-plugin/Api_calls/details.php',
                              method='POST',
                              dont_filter=True,
                              meta={

                              },
                              formdata={
                                  'selectedOrigin': response.meta['selectedOrigin'],
                                  'selectedDestination': response.meta['selectedDestination'],
                                  'value': item.get('vvd'),
                              },
                              callback=self.parse_detail)

    def parse_detail(self, response):
        data = json.loads(response.text)
        logging.info('查询详情')
        logging.info(data)
        gItem = GroupItem()
        try:
            day = data.get('totalTransitDays')
            if 'days' in day:
                TRANSIT_TIME = int(data.get('totalTransitDays').split(' ')[0])
            else:
                TRANSIT_TIME = 0
            row = {
                'ROUTE_CODE': '',
                'ETD': data.get('departure'),
                'VESSEL': data.get('vessel'),
                'VOYAGE': data.get('voyage'),
                'ETA': data.get('arrival'),
                'TRANSIT_TIME': TRANSIT_TIME,
                'TRANSIT_LIST': [],
                'IS_TRANSIT': 0,  # 确认为中转为1，直达为0, 默认为0
                'pol': '',
                'pod': '',
                'polName': data.get('originName'),
                'podName': data.get('destinationName'),
            }
            fromLocationList = data.get('fromLocationList')
            if fromLocationList and len(fromLocationList) > 1:
                row['IS_TRANSIT'] = 1
                for index, fll in enumerate(fromLocationList):
                    if fll == data.get('originName'):
                        logging.info('起点站-不算为中转')
                        continue
                    logging.info('中转--')
                    row['TRANSIT_LIST'].append({
                        'TRANSIT_PORT_EN': fll,
                        'TRANSIT_ROUTE_CODE': data.get('transportaionList')[index],
                        'TRANS_VESSEL': '',
                        'TRANS_VOYAGE': '',
                    })

            for field in gItem.fields:
                if field in row.keys():
                    gItem[field] = row.get(field)
            yield gItem
        except Exception as e:
            logging.error('error 查询{}-{}'.format(data.get('originName'), data.get('destinationName')))
            logging.error(e)
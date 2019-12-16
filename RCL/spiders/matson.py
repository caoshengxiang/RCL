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
            pItem['portCode'] = row['name']
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
        pItem = PortItem()
        for item in data:
            # 目的港
            pItem['port'] = item.get('locationName')
            pItem['portCode'] = item.get('locationName')
            yield pItem

            # 港口组合
            logging.info('港口组合:')
            pgItem['portPol'] = response.meta['polName']
            pgItem['portNamePol'] = response.meta['polName']
            pgItem['portPod'] = item.get('locationName')
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
                transitList = data.get('transitList')
                for tstl in transitList:
                    if 'days' in tstl:
                        TRANSIT_TIME += int(tstl.split(' ')[0])

            today = datetime.datetime.now()
            current_month = today.month
            etd = data.get('departure')
            eta = data.get('arrival')
            etd_str = etd.split(' ')[3]
            eta_str = eta.split(' ')[3]
            etd_year = today.year
            eta_year = today.year
            etd_month = etd_str[0:2]
            etd_day = etd_str[-2:]
            eta_month = eta_str[0:2]
            eta_day = eta_str[-2:]
            if int(current_month) > int(etd_month):
                etd_year = int(etd_year) + 1
            if int(current_month) > int(eta_month):
                eta_year = int(eta_year) + 1
            ETD = '{}-{}-{}'.format(etd_year, etd_month, etd_day)
            ETA = '{}-{}-{}'.format(eta_year, eta_month, eta_day)

            row = {
                'ROUTE_CODE': '',
                'ETD': ETD,
                # 'VESSEL': data.get('vessel'),
                # 'VOYAGE': data.get('voyage') + data.get('dir'),
                'ETA': ETA,
                'TRANSIT_TIME': TRANSIT_TIME,
                'TRANSIT_LIST': [],
                'IS_TRANSIT': 0,  # 确认为中转为1，直达为0, 默认为0
                'pol': data.get('originName'),
                'pod': data.get('destinationName'),
                'polName': data.get('originName'),
                'podName': data.get('destinationName'),
            }
            fromLocationList = data.get('fromLocationList')
            for index, fll in enumerate(fromLocationList):
                transporttation = data.get('transportaionList')[index]
                tsp_arr = transporttation.split(' ', 1)
                if index == 0:  # 第一个作为船名，航次
                    row['VESSEL'] = tsp_arr[0]
                    row['VOYAGE'] = tsp_arr[1] if len(tsp_arr) > 1 else ''
                else:
                    row['TRANSIT_LIST'].append({
                        'TRANSIT_PORT_EN': fll,
                        'TRANSIT_ROUTE_CODE': '',
                        'TRANS_VESSEL': tsp_arr[0],
                        'TRANS_VOYAGE': tsp_arr[1] if len(tsp_arr) > 1 else '',
                    })

            for field in gItem.fields:
                if field in row.keys():
                    gItem[field] = row.get(field)
            yield gItem

        except Exception as e:
            logging.error('error 查询{}-{}'.format(data.get('originName'), data.get('destinationName')))
            logging.error(e)

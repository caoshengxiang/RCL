# -*- coding: utf-8 -*-
import datetime
import json
import logging
import time

import requests
import scrapy
from pyquery import PyQuery as pq
from scrapy import FormRequest, Request

from RCL.items import PortGroupItem, PortItem, GroupItem


class PanconSpider(scrapy.Spider):
    name = 'PASU'
    allowed_domains = ['pancon.co.kr']
    start_urls = ['http://www.pancon.co.kr/pan/pageLink.pcl?link=COM/WEB_201&nationals=EN']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    start_url = 'http://www.pancon.co.kr/pan/common/selectWeb252.pcl'
    global_cn_port = []
    global_other_port = []

    def start_requests(self):
        yield Request(
            url=self.start_url,
            method='POST',
            body=json.dumps({
                'I_AS_COUNTRY_CD': "",
                'I_PROGRESS_GUID': "Web252",
                'I_REQUEST_IP_ADDRESS': "0.0.0.0",
                'I_REQUEST_PROGRAM_ID': "PMG",
                'I_REQUEST_USER_ID': "USER",
            }),
            headers={'Content-Type': 'application/json'},
            meta={
            },
            dont_filter=True,
            callback=self.parse)

    def parse(self, response):
        data = json.loads(response.text)
        try:
            for item in data['list']:
                country = {
                    'value': item['COUNTRY_CD'],
                    'name': item['COUNTRY_ENM'],
                }
                res = requests.post('http://www.pancon.co.kr/pan/common/plc_cd.pcl',
                                    headers={'Content-Type': 'application/json'},
                                    data=json.dumps({
                                        'I_AS_COUNTRY_CD': country['value'],
                                        'I_AS_PLC_CAT_CD': "",
                                        'I_AS_PLC_NM': "",
                                        'I_PROGRESS_GUID': "Web251",
                                        'I_REQUEST_IP_ADDRESS': "0.0.0.0",
                                        'I_REQUEST_PROGRAM_ID': "PMG",
                                        'I_REQUEST_USER_ID': "USER",
                                    }))
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
                # if cnindex != 7:  # DALIAN
                #     continue
                pItem['port'] = cn['PLC_ENM']
                pItem['portCode'] = cn['COUNTRY_PLC_CD']
                yield pItem
                for oincex, other in enumerate(self.global_other_port):
                    # 测试
                    # if oincex != 34:  # HAIPHONG
                    #     continue
                    # 港口
                    pItem['port'] = other['PLC_ENM']
                    pItem['portCode'] = other['COUNTRY_PLC_CD']
                    yield pItem
                    # 港口组合
                    pgItem['portPol'] = cn['COUNTRY_PLC_CD']
                    pgItem['portNamePol'] = cn['PLC_ENM']
                    pgItem['portPod'] = other['COUNTRY_PLC_CD']
                    pgItem['portNamePod'] = other['PLC_ENM']
                    yield pgItem

                    yield Request(
                        url='http://www.pancon.co.kr/pan/selectWeb201.pcl',
                        method='POST',
                        body=json.dumps({
                            'I_AS_DATE': year + month,  # 接口返回就是最近两个月数据
                            'I_AS_IN_OUT_CD': "O",
                            'I_AS_POD_CD': other['PLC_CD'],
                            'I_AS_POD_CTR': other['COUNTRY_CD'],
                            'I_AS_POL_CD': cn['PLC_CD'],
                            'I_AS_POL_CTR': cn['COUNTRY_CD'],
                            'I_PROGRESS_GUID': "Web201",
                            'I_REQUEST_IP_ADDRESS': "0.0.0.0",
                            'I_REQUEST_PROGRAM_ID': "PMG",
                            'I_REQUEST_USER_ID': "USER",
                            'rd_apdpDate': "O",
                        }),
                        headers={'Content-Type': 'application/json'},
                        meta={
                            'portPol': cn['COUNTRY_PLC_CD'],
                            'portNamePol': cn['PLC_ENM'],
                            'portPod': other['COUNTRY_PLC_CD'],
                            'portNamePod': other['PLC_ENM'],
                        },
                        dont_filter=True,
                        callback=self.parse_list)

        except Exception as e:
            logging.error('pancon error')
            logging.error(e)

    def parse_port(self, response, country):
        try:
            data = json.loads(response.text)
            if not data['list'] or not len(data['list']):
                return
            if country['name'] == 'CHINA':
                self.global_cn_port.extend(data['list'])
            elif country['name'] == 'HONG KONG':
                self.global_cn_port.extend(data['list'])
                self.global_other_port.extend(data['list'])
            else:
                self.global_other_port.extend(data['list'])
        except Exception as e:
            logging.error('pancon error')
            logging.error(e)

    def parse_list(self, response):
        data = json.loads(response.text)
        if not data['schedule'] or not data['schedule']['O_RESULT_CURSOR']:
            logging.info('查询列表无数据')
            return
        if (data['schedule']['O_ERROR_FLAG'] == 'Y'):
            logging.debug('查询接口返回错误日志')
            return
        Lists = data['schedule']['O_RESULT_CURSOR']

        def filter_seq2(li):
            return li['SEC_SEQ'] == 2

        def filter_seq3(li):
            return li['SEC_SEQ'] == 3

        def fitler_li(pod_t, list):
            for li in list:
                if pod_t <= li['POL_REVISED_APDP_DATE'] + li['POL_REVISED_APDP_TM']:
                    return li
            return {}

        SEC_SEQ2 = list(filter(filter_seq2, Lists))

        if len(SEC_SEQ2) > 0:
            SEC_SEQ2.sort(key=lambda x: x['POD_REVISED_APDP_DATE'] + x['POD_REVISED_APDP_TM'], reverse=False)

        SEC_SEQ3 = list(filter(filter_seq3, Lists))
        if len(SEC_SEQ3) > 0:
            logging.info('存在 SEQ == 3')
            SEC_SEQ3.sort(key=lambda x: x['POD_REVISED_APDP_DATE'] + x['POD_REVISED_APDP_TM'], reverse=False)

        logging.debug(SEC_SEQ2)
        logging.debug(SEC_SEQ3)

        gItem = GroupItem()
        row = {
            'pol': response.meta['portPol'],
            'pod': response.meta['portPod'],
            'polName': response.meta['portNamePol'],
            'podName': response.meta['portNamePod'],
        }
        for item in Lists:
            try:
                pol = item.get('POL', '')
                sp = pol.split(' / ')
                logging.info(sp)
                if item.get('SEC_SEQ') == 1:
                    # POL_REVISED_APDP_DATE = item.get('POL_REVISED_APDP_DATE', '')
                    # POL_REVISED_APDP_TM = item.get('POL_REVISED_APDP_TM', '')
                    # POD_REVISED_APDP_DATE = item.get('POD_REVISED_APDP_DATE', '')
                    # POD_REVISED_APDP_TM = item.get('POD_REVISED_APDP_TM', '')


                    row['ETD'] = item.get('POL_REVISED_APDP_DATE', '') + item.get('POL_REVISED_APDP_TM', '')
                    row['ETA'] = item.get('POD_REVISED_APDP_DATE', '') + item.get('POD_REVISED_APDP_TM', '')



                    row['POL_TERMINAL'] = item.get('POL', '').split(' / ')[1]
                    row['VESSEL'] = item.get('VSL_NM')
                    row['VOYAGE'] = item.get('IMP_VOY_NO')
                    # row['TRANSIT_TIME'] = int(item.get('TT', '0'))
                    row['TRANSIT_LIST'] = []
                    row['IS_TRANSIT'] = 0  # 确认为中转为1，直达为0, 默认为0
                    row['POD_TERMINAL'] = item.get('POD', '').split(' / ')[1]
                    if item.get('TS') == 'Y':
                        if len(SEC_SEQ2) > 0:
                            logging.info(item)

                            POD_item = fitler_li(item.get('POD_REVISED_APDP_DATE') + item.get('POD_REVISED_APDP_TM'),
                                                 SEC_SEQ2)
                            row['POD_TERMINAL'] = POD_item.get('POD', '').split(' / ')[1]
                            row['ETA'] = POD_item.get('POD_REVISED_APDP_DATE', '') + item.get('POD_REVISED_APDP_TM', '')
                            row['IS_TRANSIT'] = 1
                            # row['TRANSIT_TIME'] += int(POD_item.get('TT', '0'))
                            row['TRANSIT_LIST'].append({
                                'TRANSIT_PORT_EN': item.get('POD', '').split(' / ')[0],
                                'TRANS_VESSEL': POD_item.get('VSL_NM'),
                                'TRANS_VOYAGE': POD_item.get('IMP_VOY_NO'),
                            })
                        if len(SEC_SEQ3) > 0:
                            POD_item = fitler_li(item.get('POD_REVISED_APDP_DATE') + item.get('POD_REVISED_APDP_TM'),
                                                 SEC_SEQ3)
                            row['ETA'] = POD_item.get('POD_REVISED_APDP_DATE', '') + item.get('POD_REVISED_APDP_TM', '')
                            row['POD_TERMINAL'] = POD_item.get('POD', '').split(' / ')[1]
                            row['IS_TRANSIT'] = 1
                            # row['TRANSIT_TIME'] += int(POD_item.get('TT', '0'))
                            row['TRANSIT_LIST'].append({
                                'TRANSIT_PORT_EN': item.get('POD', '').split(' / ')[0],
                                'TRANS_VESSEL': POD_item.get('VSL_NM'),
                                'TRANS_VOYAGE': POD_item.get('IMP_VOY_NO'),
                            })
                    try:
                        etd_s = row['ETD']
                        eta_s = row['ETA']
                        date1 = datetime.datetime(int(etd_s[0:4]), int(etd_s[4:6]),
                                                  int(etd_s[6:8]))
                        date2 = datetime.datetime(int(eta_s[0:4]), int(eta_s[4:6]),
                                                  int(eta_s[6:8]))

                        row['ETD'] = f'{etd_s[0:4]}-{etd_s[4:6]}-{etd_s[6:8]} {etd_s[8:10]}:{etd_s[10:]}:00'
                        row['ETA'] = f'{eta_s[0:4]}-{eta_s[4:6]}-{eta_s[6:8]} {eta_s[8:10]}:{eta_s[10:]}:00'
                        row['TRANSIT_TIME'] = (date2 - date1).days
                    except Exception as e:
                        pass

                    for field in gItem.fields:
                        if field in row.keys():
                            gItem[field] = row.get(field)
                    yield gItem
                    row = {
                        'pol': response.meta['portPol'],
                        'pod': response.meta['portPod'],
                        'polName': response.meta['portNamePol'],
                        'podName': response.meta['portNamePod'],
                    }
            except Exception as e:
                logging.error('pancon error')
                logging.error(e)

# -*- coding: utf-8 -*-
import logging
import time

import scrapy
from scrapy import Request
from pyquery import PyQuery as pq

from RCL.items import PortGroupItem, PortItem, GroupItem


class GslSpider(scrapy.Spider):
    name = 'GOSU'
    allowed_domains = ['https://www.gslltd.com.hk']
    start_urls = ['https://www.gslltd.com.hk/point-to-point_g.php']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    # js 固定数据
    currencies = [
        {'name': 'ABU DHABI-U.A.E', 'value': 'AEABH'},
        {'name': 'Dubai-U.A.E', 'value': 'AEDBI'},
        {'name': 'Shenzhen-China (South)', 'value': 'CNSH1'},
        {'name': 'Chittagong-Bangladesh', 'value': 'BDCGP'},
        {'name': 'Dhaka-Bangladesh', 'value': 'BDDAC'},
        {'name': 'Manama-Bahrain', 'value': 'BHQLH'},
        {'name': 'Cotonou-Benin', 'value': 'BJCOO'},
        {'name': 'Abidjan-Ivory Coast', 'value': 'CIABI'},
        {'name': 'Beijing-China', 'value': 'CNBJI'},
        {'name': 'Dalian-China', 'value': 'CNDAL'},
        {'name': 'Fuzhou-China', 'value': 'CNFUZ'},
        {'name': 'GuangZhou-China', 'value': 'CNGZH'},
        {'name': 'Hangzhou-China', 'value': 'CNHAZ'},
        {'name': 'Hefei-China', 'value': 'CNHEF'},
        {'name': 'Shunde-China', 'value': 'CNIAU'},
        {'name': 'LianYunGang-China', 'value': 'CNLYU'},
        {'name': 'NanJing-China', 'value': 'CNNNJ'},
        {'name': 'NanNing-China', 'value': 'CNNNN'},
        {'name': 'NanTong-China', 'value': 'CNNTG'},
        {'name': 'ChongQing-China', 'value': 'CNOCQ'},
        {'name': 'Changsha-China', 'value': 'CNOHG'},
        {'name': 'Qingdao-China', 'value': 'CNQIN'},
        {'name': 'Shenzhen-China', 'value': 'CNSHH'},
        {'name': 'Shanghai-China', 'value': 'CNSNH'},
        {'name': 'TianJi-China', 'value': 'CNTIA'},
        {'name': 'Wuhan-China', 'value': 'CNWUH'},
        {'name': 'Xiamen-China', 'value': 'CNXIA'},
        {'name': 'ZhanJiang-China', 'value': 'CNZHJ'},
        {'name': 'ZhongShan-China', 'value': 'CNZSH'},
        {'name': 'Takoradi-Ghana', 'value': 'GHTDI'},
        {'name': 'Tema-Ghana', 'value': 'GHTEM'},
        {'name': 'Port of LEE LI-DICKY2019', 'value': 'LILEE'},
        {'name': 'Bandung-Indonesia', 'value': 'IDBNU'},
        {'name': 'Jakarta-Indonesia', 'value': 'IDJKT'},
        {'name': 'Medan-Indonesia', 'value': 'IDMEA'},
        {'name': 'Palembang-Indonesia', 'value': 'IDPAB'},
        {'name': 'Panjang-Indonesia', 'value': 'IDPJN'},
        {'name': 'Semarang-Indonesia', 'value': 'IDSEM'},
        {'name': 'Surabaya-Indonesia', 'value': 'IDSUB'},
        {'name': 'Ahmedabad-India', 'value': 'INAHM'},
        {'name': 'Bangalore-India', 'value': 'INBNR'},
        {'name': 'Mumbai-India', 'value': 'INBOM'},
        {'name': 'Kolkata-India', 'value': 'INCCU'},
        {'name': 'Cochin-India', 'value': 'INCOK'},
        {'name': 'Hyderabad-India', 'value': 'INHYX'},
        {'name': 'ICD Indore (ICD Pithampur)-India', 'value': 'INIDR'},
        {'name': 'New Delhi-India', 'value': 'INITG'},
        {'name': 'Kandla-India', 'value': 'INKND'},
        {'name': 'Ludhiana-India', 'value': 'INLDH'},
        {'name': 'Chennai-India', 'value': 'INMAA'},
        {'name': 'ICD Nagpur-India', 'value': 'INNAG'},
        {'name': 'Nhava Sheva-India', 'value': 'INNHV'},
        {'name': 'Mundra-India', 'value': 'INRQL'},
        {'name': 'Tuticorin-India', 'value': 'INTUT'},
        {'name': 'Kobe-Japan', 'value': 'JPKBE'},
        {'name': 'Nagoya-Japan', 'value': 'JPNGO'},
        {'name': 'Tokyo-Japan', 'value': 'JPTYO'},
        {'name': 'Yokohama-Japan', 'value': 'JPYOK'},
        {'name': 'Phnom Penh-Cambodia', 'value': 'KHPKH'},
        {'name': 'Incheon (Inchon)-Korea', 'value': 'KRICN'},
        {'name': 'Pusan-Korea', 'value': 'KRPUS'},
        {'name': 'Seoul-Korea', 'value': 'KRSEL'},
        {'name': 'Colombo-Sri Lanka', 'value': 'LKCMB'},
        {'name': 'Yangon-Myanmar', 'value': 'MMYAG'},
        {'name': 'Port Louis-Mauritius', 'value': 'MUREU'},
        {'name': 'Port Klang-Malaysia', 'value': 'MYPKL'},
        {'name': 'Penang-Malaysia', 'value': 'MYPNG'},
        {'name': 'Pasir Gudang (Johor)-Malaysia', 'value': 'MYPSG'},
        {'name': 'Lagos-Nigeria', 'value': 'NGLOS'},
        {'name': 'Muscat-Oman', 'value': 'OMSOH'},
        {'name': 'Cebu-Philippines', 'value': 'PHCEB'},
        {'name': 'Davao-Philippines', 'value': 'PHDVO'},
        {'name': 'Manila-Philippines', 'value': 'PHMNL'},
        {'name': 'Karachi-Pakistan', 'value': 'PKKHI'},
        {'name': 'DOHA-Qatar', 'value': 'QADOH'},
        {'name': 'Singapore-Singapore', 'value': 'SGSIN'},
        {'name': 'Lome-Togo', 'value': 'TGLME'},
        {'name': 'Bangkok-Thailand', 'value': 'THBKK'},
        {'name': 'Kaohsiung-Taiwan, China', 'value': 'TWKSG'},
        {'name': 'Taipei-Taiwan, China', 'value': 'TWTPE'},
        {'name': 'Haiphong-Vietnam', 'value': 'VNHAI'},
        {'name': 'Ho Chi Minh-Vietnam', 'value': 'VNHCM'},
        {'name': 'Durban-South Africa', 'value': 'ZADUR'},
        {'name': 'Johannesburg-South Africa', 'value': 'ZAJNB'},
        {'name': 'Port Elizabeth-South Africa', 'value': 'ZAPLZ'},
        {'name': 'Durban-SOUTH AFRICA', 'value': 'ZADUR'},
        {'name': 'Hong Kong-Hong Kong SAR, PRC', 'value': 'HKHKG'},
        {'name': 'MALE-MALDIVES', 'value': 'MVMLE'},
    ]

    global_cn_port = []
    global_other_port = []

    def parse(self, response):
        # logging.info(response.text)
        for item in self.currencies:
            # logging.debug(item['value'])
            if item['value'] == 'HKHKG':
                self.global_cn_port.append(item)
                self.global_other_port.append(item)
            elif item['value'][0:2] == 'CN':
                self.global_cn_port.append(item)
            else:
                self.global_other_port.append(item)

        logging.info('完成所有港口处理')
        logging.info(self.global_cn_port)
        logging.info(self.global_other_port)

        pgItem = PortGroupItem()
        pItem = PortItem()

        localtime = time.localtime(time.time())
        year = str(localtime.tm_year)
        month = str(localtime.tm_mon)
        day = str(localtime.tm_mday)
        if len(day) < 2:
            day = '0' + day

        for cnindex, cn in enumerate(self.global_cn_port):
            # 测试
            if cnindex != 3:
                continue
            pItem['port'] = cn['name']
            pItem['portCode'] = cn['value']
            yield pItem
            for oincex, other in enumerate(self.global_other_port):
                #测试
                if oincex > 2:
                    continue
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

                url = 'https://www.shipcont.com/p2p.aspx?hidSearch=true&hidFromHomePage=false&hidSearchType=4&id=166&l=4&txtPOL={}&txtPOD={}&rb=Dep&txtDateFrom={}&txtDateTo={}'
                dataFormat = '{}/{}/{}'

                next2_month = str((int(month) + 2) % 12)
                if len(next2_month) < 2:
                    next2_month = '0' + next2_month
                next2_year = (int((int(month) + 2) / 12) + int(year))

                yield Request(
                    url=url.format(
                        cn['value'],
                        other['value'],
                        dataFormat.format(day, month, year),
                        dataFormat.format('01', next2_month, next2_year),
                    ),
                    method='GET',
                    meta={
                        'pol': cn['value'],
                        'polName': cn['name'],
                        'pod': other['value'],
                        'podName': other['name'],
                    },
                    dont_filter=True,
                    callback=self.parse_list)

    def parse_list(self, response):
        doc = pq(response.text)
        table = doc('#resultsTable')
        logging.info(table)

        if not table:
            logging.info('查询无数据{} , {}'.format(response.meta['polName'], response.meta['podName']))
            return

        tbody = table.children('tbody')
        trsA = tbody.children('tr')
        gItem = GroupItem()

        for aindex, trA in enumerate(trsA.items()):
            # if aindex == 0:
            #     continue
            try:
                row = {}
                if trA.find('table'):
                    trsB = trA.find('table tr')
                    isTs = True if len(trsB) > 1 else False

                    if isTs == False:
                        for trB in trsB.items():
                            tds = trB.find('td')

                            tmp = tds.eq(7).text()

                            row = {
                                'ETD': tds.eq(4).text().text().split(' , ')[0],
                                'VESSEL': tds.eq(0).text(),
                                'VOYAGE': tds.eq(2).text(),
                                'ETA': tds.eq(5).text().text().split(' , ')[0],
                                'ROUTE_CODE': tds.eq(6).text(),
                                'TRANSIT_TIME': int(tds.eq(7).text().split(' ')[0]),
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
                    else:
                        row = {}
                        for bindex, trB in enumerate(trsB.items()):
                            tds = trB.find('td')
                            if bindex == 0:
                                row = {
                                    'ETD': tds.eq(4).text().split(' , ')[0],
                                    'VESSEL': tds.eq(0).text(),
                                    'VOYAGE': tds.eq(2).text(),
                                    # 'ETA': tds.eq(5).text(),
                                    'ROUTE_CODE': tds.eq(6).text(),
                                    'TRANSIT_TIME': int(tds.eq(7).text().split(' ')[0]),
                                    'TRANSIT_LIST': [],
                                    'IS_TRANSIT': 1,  # 确认为中转为1，直达为0, 默认为0
                                    'pol': response.meta['pol'],
                                    'pod': response.meta['pod'],
                                    'polName': response.meta['polName'],
                                    'podName': response.meta['podName'],
                                }
                            else:
                                row['ETA'] = tds.eq(5).text().split(' , ')[0]
                                row['TRANSIT_LIST'].append({
                                    'TRANSIT_PORT_EN': tds.eq(4).text().split(' , ')[1],
                                    'TRANS_VESSEL': '',
                                    'TRANS_VOYAGE': '',
                                })
                        logging.info(row)
                        for field in gItem.fields:
                            if field in row.keys():
                                gItem[field] = row.get(field)
                        yield gItem

            except Exception as e:
                logging.error(e)

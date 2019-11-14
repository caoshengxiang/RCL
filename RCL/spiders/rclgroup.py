# -*- coding: utf-8 -*-
import math

import scrapy
from scrapy import Request
from pyquery import PyQuery as pq
import time
from RCL.items import PortItem, GroupItem, PortGroupItem
import logging


class RclgroupSpider(scrapy.Spider):
    name = 'rclgroup'
    allowed_domains = ['rclgroup.com']
    start_urls = ['https://www.rclgroup.com/Home']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': '_ga=GA1.2.383328044.1572849733; _gid=GA1.2.1319479703.1573436902; cookiesession1=4860C136QSBUT4QBQNC3W4QSTSMTA652',
        'Host': 'www.rclgroup.com',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': 1,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.62 Safari/537.36'
    }
    currentDate = time.strftime('%d/%m/%Y', time.localtime())
    groupUrl = 'https://www.rclgroup.com/210Sailing_Schedule019'

    data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': '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',
        '__VIEWSTATEGENERATOR': 'CA0B0334',
        '__PREVIOUSPAGE': 'KNiZiHexPoXoEWQbw2sSE94IyNctD0ZhTzodkhlRimbTVnE-iIQi801ni8gfOWrEouX9QqBMVCugEjenI5OWMQ2',
        '__EVENTVALIDATION': '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',
        'ctl00$ContentPlaceHolder1$captchavalue': '9ba',
        'ctl00$ContentPlaceHolder1$ctracking': '',
        'ctl00$ContentPlaceHolder1$cCaptcha': '',
        'ctl00$ContentPlaceHolder1$vsdate': currentDate,
        'ctl00$ContentPlaceHolder1$vsduration': '42',
        'ctl00$ContentPlaceHolder1$vsLoading': 'HKHKG',  # CNDLC
        'ctl00$ContentPlaceHolder1$vsDischarge': 'PKQCT',  # AEDXB
        'ctl00$ContentPlaceHolder1$sCaptcha': '9ba',
        'ctl00$ContentPlaceHolder1$submitVS': 'Submit',
        'ctl00$ContentPlaceHolder1$ltService': 'ALO',
        'ctl00$ContentPlaceHolder1$ltduration': '1',
        'ctl00$ContentPlaceHolder1$RdoMonth': '2',
        'ctl00$ContentPlaceHolder1$ltDate': currentDate,
        'ctl00$ContentPlaceHolder1$lCaptcha': ''
    }

    def start_requests(self):
        # yield Request(url=self.start_urls[0], callback=self.parse_port, headers=self.headers)
        yield scrapy.FormRequest(url=self.groupUrl, method='POST',
                                 meta={
                                     # 'polName': 'DALIAN',
                                     # 'podName': 'JEBEL ALI, U.A.E'
                                     'pol': self.data['ctl00$ContentPlaceHolder1$vsLoading'],
                                     'pod': self.data['ctl00$ContentPlaceHolder1$vsDischarge'],
                                     'polName': 'HONG KONG',
                                     'podName': 'QASIM'
                                 },
                                 formdata=self.data,
                                 callback=self.parse_group,
                                 headers=self.headers)

    def parse_port(self, response):
        doc = pq(response.text)
        list = doc('#ContentPlaceHolder1_vsLoading option')
        CNARR = []
        OTHERARR = []
        for li in list.items():  # 注意这里遍历需要 .items()
            pitem = PortItem()
            arr = li.text().split(' - ')
            pitem['portCode'] = arr[0]
            pitem['port'] = arr[1]
            pitem['date'] = self.currentDate
            if arr[0] == 'HKHKG':
                CNARR.append({'code': arr[0], 'name': arr[1]})
                OTHERARR.append({'code': arr[0], 'name': arr[1]})
            elif arr[0][0:2] == 'CN':
                CNARR.append({'code': arr[0], 'name': arr[1]})
            else:
                OTHERARR.append({'code': arr[0], 'name': arr[1]})
            yield pitem
        logging.info('港口数据获取完成, 开始请求港口组合')
        for cn in CNARR:
            for other in OTHERARR:
                self.data['ctl00$ContentPlaceHolder1$vsLoading'] = cn['code']
                self.data['ctl00$ContentPlaceHolder1$vsDischarge'] = other['code']
                # logging.info(self.data)
                yield scrapy.FormRequest(url=self.groupUrl, method='POST',
                                         meta={
                                             'pol': cn['code'],
                                             'pod': other['code'],
                                             'polName': cn['name'],
                                             'podName': other['name']
                                         },
                                         formdata=self.data,
                                         callback=self.parse_group,
                                         headers=self.headers)

    def get_row(self, ele):
        tds = ele.find('td')
        row = {}
        for td in tds.items():
            dataLabel = td.attr('data-label')
            if dataLabel == 'Vessel Name':
                row['VESSEL'] = td.text()
            if dataLabel == 'Voy No':
                row['VOYAGE'] = td.text()
            if dataLabel == 'Port of Loading':
                row['POL_NAME_EN'] = td.text()
            if dataLabel == 'Loading Port(Arrival)':
                row['LPA'] = td.text()
            if dataLabel == 'Loading Port(Departure)':
                row['ETD'] = td.text()
            if dataLabel == 'Port of Discharge':
                row['POD_NAME_EN'] = td.text()
            if dataLabel == 'Destination Arrival':
                row['ETA'] = td.text()
            if dataLabel == 'Transit Time':
                row['TRANSIT_TIME'] = td.text()
            if dataLabel == 'Vessel Flag':
                row['FLAG'] = td.text()
        return row

    def parse_group(self, response):
        doc = pq(response.text)
        trs = doc('#vesseltable tr')
        pgItem = PortGroupItem()
        pgItem['date'] = self.currentDate
        pgItem['portPol'] = response.meta['pol']
        pgItem['portNamePol'] = response.meta['polName']
        pgItem['portPod'] = response.meta['pod']
        pgItem['portNamePod'] = response.meta['podName']
        pgItem['content'] = response.text
        pgItem['status'] = 1 if trs.length else 2
        # pgItem['userTime'] = ''
        logging.info('港口组合：')
        yield pgItem

        itemObj = {}
        gItem = GroupItem()
        for index, tr in enumerate(trs.items()):  # 使用 enumerate 函数 获取索引
            try:
                className = tr.attr('class')
                if className == 'rowg' or className == 'rowb':
                    currentRowPolName = tr.find('td[data-label="Port of Loading"]').text()
                    currentRowPodName = tr.find('td[data-label="Port of Discharge"]').text()
                    logging.debug('查询起止：' + response.meta['polName'] + ' - ' + response.meta['podName'])
                    logging.debug('当前行起止：' + currentRowPolName + ' - ' + currentRowPodName)
                    row = self.get_row(tr)
                    if currentRowPolName == response.meta['polName']:
                        # 处理异常数据
                        if itemObj['polName']:
                            pass
                        itemObj = {
                            'pol': response.meta['pol'],
                            'pod': response.meta['pod'],
                            'polName': response.meta['polName'],
                            'podName': response.meta['podName'],
                            'date': self.currentDate,
                            'VESSEL': row['VESSEL'],
                            'VOYAGE': row['VOYAGE'],
                            'ETD': row['ETD'],
                            'TRANSIT_TIME': float(row['TRANSIT_TIME']),
                            'TRANSIT_LIST': [],
                            'IS_TRANSIT': 0  # 确认为中转为1，直达为0, 默认为0
                        }
                    else:
                        itemObj['IS_TRANSIT'] = 1
                        itemObj['TRANSIT_TIME'] += float(row['TRANSIT_TIME'])
                        itemObj['TRANSIT_LIST'].append({
                            'TRANSIT_PORT_EN': row['POL_NAME_EN'],
                            'TRANS_VESSEL': row['VESSEL'],
                            'TRANS_VOYAGE': row['VOYAGE'],
                        })
                    if currentRowPodName == response.meta['podName']:
                        itemObj['ETA'] = row['ETA']
                        itemObj['TRANSIT_TIME'] = math.ceil(itemObj['TRANSIT_TIME'])
                        for field in gItem.fields:
                            if field in itemObj.keys():
                                gItem[field] = itemObj.get(field)
                        yield gItem
                        itemObj = {}
            except Exception as e:
                logging.error('错误组合：' + response.meta['polName'] + ' - ' + response.meta['podName'])
                logging.error(e)
                logging.error(doc('#vesseltable'))
                continue

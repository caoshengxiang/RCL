# -*- coding: utf-8 -*-
import json
import logging
import math
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options

import requests
import scrapy

from pyquery import PyQuery as pq
from scrapy import Request, FormRequest

from RCL.items import PortItem, PortGroupItem, GroupItem


def get_ports(options):
    ports = []
    for option in options:
        value = option.get_attribute('value')
        name = option.text
        if value == '0':
            continue
        ports.append({'value': value, 'name': name})
    return ports


class IalSpider(scrapy.Spider):
    name = 'IALU'
    allowed_domains = ['www.interasia.cc']
    start_urls = ['http://www.interasia.cc/content/c_service/sailing_schedule.aspx?SiteID=1']
    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        No_Image_loading = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", No_Image_loading)
        epath = "/usr/bin/chromedriver"
        # chrome_options.binary_location = r"D:\soft\googlechrome\Application\77.0.3865.120\chrome.exe"
        # epath = "D:/work/chromedriver.exe"
        self.driver = webdriver.Chrome(executable_path=epath, chrome_options=chrome_options)

        # chrome_options = Options()
        # # chrome_options.add_argument('--headless')
        # No_Image_loading = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", No_Image_loading)
        # self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def parse(self, response):
        pgItem = PortGroupItem()
        pItem = PortItem()
        gItem = GroupItem()
        doc = pq(response.text)
        countryOptions = doc('#ctl00_CPHContent_ddlDepartureC').find('option')
        c_h_c = []
        o_h_c = []
        for option in countryOptions.items():
            va = option.attr('value')
            name = option.text()
            if va != '0':
                if name == 'CHINA':
                    c_h_c.append({'value': va, 'name': name})
                elif name == 'HONG KONG':
                    c_h_c.append({'value': va, 'name': name})
                    o_h_c.append({'value': va, 'name': name})
                else:
                    o_h_c.append({'value': va, 'name': name})
        logging.info('国家解析完成。')

        self.driver.get(self.start_urls[0])
        for c_h in c_h_c:
            time.sleep(1)
            Select(self.driver.find_element_by_id('ctl00_CPHContent_ddlDepartureC')).select_by_value(c_h['value'])
            time.sleep(1)
            c_h_options = self.driver.find_elements_by_css_selector('#ctl00_CPHContent_ddlDepartureL option')

            c_h_ports = get_ports(c_h_options)

            logging.info(c_h_ports)
            for c_h_port in c_h_ports:
                pItem['port'] = c_h_port['name']
                pItem['portCode'] = c_h_port['name']
                yield pItem
                try:
                    logging.info('港口数据:{}'.format(c_h_port))
                    Select(self.driver.find_element_by_id('ctl00_CPHContent_ddlDepartureL')).select_by_value(
                        c_h_port['value'])
                    time.sleep(1)
                except Exception as e:
                    logging.error('ial error 1')
                    logging.error(e)

                for o_h in o_h_c:
                    try:
                        Select(self.driver.find_element_by_id('ctl00_CPHContent_ddlDestinationC')).select_by_value(
                            o_h['value'])
                        time.sleep(1)
                        o_h_options = self.driver.find_elements_by_css_selector(
                            '#ctl00_CPHContent_ddlDestinationL option')
                        o_h_ports = get_ports(o_h_options)
                        for o_h_port in o_h_ports:
                            # 港口
                            pItem['port'] = o_h_port['name']
                            pItem['portCode'] = o_h_port['name']
                            yield pItem

                            # 港口组合
                            pgItem['portPol'] = c_h_port['name']
                            pgItem['portNamePol'] = c_h_port['name']
                            pgItem['portPod'] = o_h_port['name']
                            pgItem['portNamePod'] = o_h_port['name']
                            yield pgItem
                            try:
                                logging.info('港口数据:{}'.format(o_h_port))
                                Select(
                                    self.driver.find_element_by_id('ctl00_CPHContent_ddlDestinationL')).select_by_value(
                                    o_h_port['value'])
                                time.sleep(1)
                                code = self.driver.find_element_by_id('ctl00_CPHContent_imgCode').get_attribute('src')
                                code = code[-4:]
                                ele = self.driver.find_element_by_id('ctl00_CPHContent_txtCode')
                                ele.clear()
                                ele.send_keys(code)
                                self.driver.find_element_by_id('ctl00_CPHContent_btnSend').click()
                                time.sleep(1)
                                source = self.driver.page_source
                                listDoc = pq(source)

                                # 解析
                                trs = listDoc('#ctl00_CPHContent_Panel2 .table_style2').find('tr')
                                # logging.warning(response.text)
                                for index, tr in enumerate(trs.items()):
                                    logging.info('数据长度：{}'.format(tr.find('td').length))
                                    if tr.find('td').length > 1:
                                        timeS = tr.find('td').eq(8).text()
                                        if timeS:
                                            timeI = math.ceil(float(timeS))
                                        else:
                                            timeI = 0
                                        row = {
                                            'ROUTE_CODE': tr.find('td').eq(3).text(),
                                            'ETD': tr.find('td').eq(0).text(),
                                            'VESSEL': tr.find('td').eq(1).text(),
                                            'VOYAGE': tr.find('td').eq(2).text(),
                                            'ETA': tr.find('td').eq(4).text(),
                                            'TRANSIT_TIME': timeI,
                                            'TRANSIT_LIST': [],
                                            'IS_TRANSIT': 0,  # 确认为中转为1，直达为0, 默认为0
                                            'pol': c_h_port['name'],
                                            'pod': o_h_port['name'],
                                            'polName': c_h_port['name'],
                                            'podName': o_h_port['name'],
                                        }
                                        for field in gItem.fields:
                                            if field in row.keys():
                                                gItem[field] = row.get(field)
                                        yield gItem
                                        logging.info('{}列数据：'.format(index + 1))

                                self.driver.back()
                                time.sleep(1)
                            except Exception as e:
                                logging.error('ial error 2')
                                logging.error(e)
                    except Exception as e:
                        logging.error('ial error 3')
                        logging.error(e)

    @staticmethod
    def close(spider, reason):
        """
        关闭chrome
        :param spider:
        :param reason:
        :return:
        """
        if spider.driver:
            spider.driver.quit()
        super().close(spider, reason)

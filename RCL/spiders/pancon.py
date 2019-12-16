# -*- coding: utf-8 -*-
import json
import logging
import time

import requests
import scrapy
from pyquery import PyQuery as pq
from scrapy import FormRequest, Request
from selenium.common.exceptions import NoAlertPresentException

from RCL.items import PortGroupItem, PortItem, GroupItem
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options


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

    def __init__(self):
        # chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        # No_Image_loading = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", No_Image_loading)
        # epath = "/usr/bin/chromedriver"
        # # chrome_options.binary_location = r"D:\soft\googlechrome\Application\77.0.3865.120\chrome.exe"
        # # epath = "D:/work/chromedriver.exe"
        # self.driver = webdriver.Chrome(executable_path=epath, chrome_options=chrome_options)

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        No_Image_loading = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", No_Image_loading)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

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

    @staticmethod
    def get_ports(options):
        ports = []
        for option in options:
            value = option.get_attribute('value')
            name = option.text
            if not value:
                continue
            ports.append({'value': value, 'name': name})
        return ports

    def parse(self, response):
        try:
            data = json.loads(response.text)
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

            self.driver.get(self.start_urls[0])
            time.sleep(1)

            # global_cn_port 数据结构
            # {'PORT_NM': 'BEIHAI(CNBHY) / CHINA', 'PLC_ENM': 'BEIHAI', 'PLC_NM': 'BEIHAI', 'COUNTRY_PLC_CD': 'CNBHY', 'KIND': 'PORT', 'PLC_CD': 'BHY', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'}

            for cnindex, c_h_p in enumerate(self.global_cn_port):
                # 测试
                if cnindex != 7:  # DALIAN
                    continue

                self.driver.find_element_by_id('btn_pol_port').click()
                # 可删除 next line
                # time.sleep(1)
                self.driver.find_element_by_id('pol_country_cd').click()
                # time.sleep(2)
                Select(self.driver.find_element_by_id('pol_country_cd')).select_by_value(
                    c_h_p['COUNTRY_CD'])  # 选择国家
                time.sleep(2)  # 接口渲染 todo

                # 可删除 next 2 line
                self.driver.find_element_by_id('pol_port_cd').click()
                # time.sleep(3)

                Select(self.driver.find_element_by_id('pol_port_cd')).select_by_value(c_h_p['PLC_CD'])
                # 可删除 next line
                # time.sleep(3)

                for ohindex, o_h_p in enumerate(self.global_other_port):
                    if ohindex != 34:  # HAIPHONG
                        continue

                    self.driver.find_element_by_id('btn_pod_port').click()
                    # 可删除 next line
                    # time.sleep(1)
                    self.driver.find_element_by_id('pod_country_cd').click()
                    # time.sleep(2)
                    Select(self.driver.find_element_by_id('pod_country_cd')).select_by_value(
                        o_h_p['COUNTRY_CD'])  # 选择国家
                    time.sleep(2)  # 接口渲染 todo

                    # 可删除 next 2 line
                    self.driver.find_element_by_id('pod_port_cd').click()
                    # time.sleep(3)

                    Select(self.driver.find_element_by_id('pod_port_cd')).select_by_value(o_h_p['PLC_CD'])

                    self.driver.find_element_by_id('WEB_201_INQ').click()
                    time.sleep(5)  # todo

                    try:
                        # 获取alert对话框
                        dig_alert = self.driver.switch_to.alert
                        time.sleep(1)
                        t = dig_alert.text
                        dig_alert.accept()
                        time.sleep(1)
                        continue
                    except NoAlertPresentException:
                        doc_1 = pq(self.driver.page_source)
                        calTable = doc_1('#calTable')
                        logging.info('日历')

                        lis = calTable.find('li')
                        for li in lis.items():
                            li_id = li.attr('id')
                            self.driver.find_element_by_id(li_id).click()
                            time.sleep(1)
                            source_2 = self.driver.page_source
                            doc_2 = pq(self.driver.page_source)
                            ex_detail = doc_2('#ex_detail')
                            logging.info()









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
        try:
            pass
        except Exception as e:
            logging.error('pancon error')
            logging.error(e)

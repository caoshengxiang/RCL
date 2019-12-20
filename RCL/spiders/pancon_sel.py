# -*- coding: utf-8 -*-
import datetime
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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PanconSpider(scrapy.Spider):
    name = 'PASU_sel'
    allowed_domains = ['pancon.co.kr']
    start_urls = ['http://www.pancon.co.kr/pan/pageLink.pcl?link=COM/WEB_201&nationals=EN#none']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            # 'RCL.pipelines.MongoPipeline': 300
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    start_url = 'http://www.pancon.co.kr/pan/common/selectWeb252.pcl'
    global_cn_port = []
    global_other_port = []
    pol_current_country = ''
    pod_current_country = ''

    localtime = time.localtime(time.time())
    year = str(localtime.tm_year)
    month = str(localtime.tm_mon)
    # next month
    nextYear = year
    if int(month) + 1 > 12:
        nextYear = str(int(nextYear) + 1)
        nextMonth = '1'
    else:
        nextMonth = str(int(month) + 1)
    date = [{'y': year, 'm': month}, {'y': nextYear, 'm': nextMonth}]
    # 测试
    # date = [{'y': year, 'm': month}]

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

    def has_alert(self):
        try:
            alert = self.driver.switch_to.alert
            return True
        except NoAlertPresentException:
            return False

    def has_ele(self, className):
        # noinspection PyBroadException
        try:
            self.driver.find_element_by_class_name(className)
            return True
        except Exception as e:
            return False

    def fresh_page(self):
        self.driver.refresh()  # 刷新方法 refresh
        time.sleep(1)
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#pol_country_cd > option:nth-child(2)')))

    def parse(self, response):
        try:

            self.driver.get(self.start_urls[0])

            gItem = GroupItem()
            pgItem = PortGroupItem()
            pItem = PortItem()
            # # 写死
            # data = json.loads(response.text)
            # for item in data['list']:
            #     country = {
            #         'value': item['COUNTRY_CD'],
            #         'name': item['COUNTRY_ENM'],
            #     }
            #     res = requests.post('http://www.pancon.co.kr/pan/common/plc_cd.pcl',
            #                         headers={'Content-Type': 'application/json'},
            #                         data=json.dumps({
            #                             'I_AS_COUNTRY_CD': country['value'],
            #                             'I_AS_PLC_CAT_CD': "",
            #                             'I_AS_PLC_NM': "",
            #                             'I_PROGRESS_GUID': "Web251",
            #                             'I_REQUEST_IP_ADDRESS': "0.0.0.0",
            #                             'I_REQUEST_PROGRAM_ID': "PMG",
            #                             'I_REQUEST_USER_ID': "USER",
            #                         }))
            #     self.parse_port(res, country)

            self.global_cn_port = [
                {'PORT_NM': 'BEIHAI(CNBHY) / CHINA', 'PLC_ENM': 'BEIHAI', 'PLC_NM': 'BEIHAI', 'COUNTRY_PLC_CD': 'CNBHY',
                 'KIND': 'PORT', 'PLC_CD': 'BHY', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'BEIJIAO(CNBIJ) / CHINA', 'PLC_ENM': 'BEIJIAO', 'PLC_NM': 'BEIJIAO',
                 'COUNTRY_PLC_CD': 'CNBIJ', 'KIND': 'INLAND', 'PLC_CD': 'BIJ', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'}, {'PORT_NM': 'BEIJING(CNBJS) / CHINA', 'PLC_ENM': 'BEIJING', 'PLC_NM': 'BEIJING',
                                       'COUNTRY_PLC_CD': 'CNBJS', 'KIND': 'INLAND', 'PLC_CD': 'BJS',
                                       'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'CHANGSHA(CNCSX) / CHINA', 'PLC_ENM': 'CHANGSHA', 'PLC_NM': 'CHANGSHA',
                 'COUNTRY_PLC_CD': 'CNCSX', 'KIND': 'PORT', 'PLC_CD': 'CSX', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'CHANGSHOU(CNCGS) / CHINA', 'PLC_ENM': 'CHANGSHOU', 'PLC_NM': 'CHANGSHOU',
                 'COUNTRY_PLC_CD': 'CNCGS', 'KIND': 'INLAND', 'PLC_CD': 'CGS', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'CHANGZHOU(CNCZX) / CHINA', 'PLC_ENM': 'CHANGZHOU', 'PLC_NM': 'CHANGZHOU',
                 'COUNTRY_PLC_CD': 'CNCZX', 'KIND': 'INLAND', 'PLC_CD': 'CZX', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'CHONGQING(CNCQI) / CHINA', 'PLC_ENM': 'CHONGQING', 'PLC_NM': 'CHONGQING',
                 'COUNTRY_PLC_CD': 'CNCQI', 'KIND': 'INLAND', 'PLC_CD': 'CQI', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'DALIAN(CNDLC) / CHINA', 'PLC_ENM': 'DALIAN', 'PLC_NM': 'DALIAN', 'COUNTRY_PLC_CD': 'CNDLC',
                 'KIND': 'PORT', 'PLC_CD': 'DLC', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'FOSHAN(CNFRT) / CHINA', 'PLC_ENM': 'FOSHAN', 'PLC_NM': 'FOSHAN', 'COUNTRY_PLC_CD': 'CNFRT',
                 'KIND': 'PORT', 'PLC_CD': 'FRT', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'GAOMING(CNGOM) / CHINA', 'PLC_ENM': 'GAOMING', 'PLC_NM': 'GAOMING',
                 'COUNTRY_PLC_CD': 'CNGOM', 'KIND': 'PORT', 'PLC_CD': 'GOM', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'GAOSHA(CNGSH) / CHINA', 'PLC_ENM': 'GAOSHA', 'PLC_NM': 'GAOSHA', 'COUNTRY_PLC_CD': 'CNGSH',
                 'KIND': 'INLAND', 'PLC_CD': 'GSH', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'HAIKOU(CNHAK) / CHINA', 'PLC_ENM': 'HAIKOU', 'PLC_NM': 'HAIKOU', 'COUNTRY_PLC_CD': 'CNHAK',
                 'KIND': 'INLAND', 'PLC_CD': 'HAK', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'HAIMEN(CNHME) / CHINA', 'PLC_ENM': 'HAIMEN', 'PLC_NM': 'HAIMEN', 'COUNTRY_PLC_CD': 'CNHME',
                 'KIND': 'PORT', 'PLC_CD': 'HME', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'HANGZHOU(CNHAN) / CHINA', 'PLC_ENM': 'HANGZHOU', 'PLC_NM': 'HANGZHOU',
                 'COUNTRY_PLC_CD': 'CNHAN', 'KIND': 'INLAND', 'PLC_CD': 'HAN', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'}, {'PORT_NM': 'HUANGPU(CNHUA) / CHINA', 'PLC_ENM': 'HUANGPU', 'PLC_NM': 'HUANGPU',
                                       'COUNTRY_PLC_CD': 'CNHUA', 'KIND': 'PORT', 'PLC_CD': 'HUA',
                                       'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'JIANG YIN(CNJIA) / CHINA', 'PLC_ENM': 'JIANG YIN', 'PLC_NM': 'JIANG YIN',
                 'COUNTRY_PLC_CD': 'CNJIA', 'KIND': 'PORT', 'PLC_CD': 'JIA', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'JIANGMEN (CNJMN) / CHINA', 'PLC_ENM': 'JIANGMEN ', 'PLC_NM': 'JIANGMEN ',
                 'COUNTRY_PLC_CD': 'CNJMN', 'KIND': 'PORT', 'PLC_CD': 'JMN', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'JIAOXIN(CNJXN) / CHINA', 'PLC_ENM': 'JIAOXIN', 'PLC_NM': 'JIAOXIN',
                 'COUNTRY_PLC_CD': 'CNJXN', 'KIND': 'INLAND', 'PLC_CD': 'JXN', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'}, {'PORT_NM': 'JIAXING(CNJAX) / CHINA', 'PLC_ENM': 'JIAXING', 'PLC_NM': 'JIAXING',
                                       'COUNTRY_PLC_CD': 'CNJAX', 'KIND': 'INLAND', 'PLC_CD': 'JAX',
                                       'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'JIUJIANG(CNJIU) / CHINA', 'PLC_ENM': 'JIUJIANG', 'PLC_NM': 'JIUJIANG',
                 'COUNTRY_PLC_CD': 'CNJIU', 'KIND': 'PORT', 'PLC_CD': 'JIU', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'KUNSHAN(CNKUS) / CHINA', 'PLC_ENM': 'KUNSHAN', 'PLC_NM': 'KUNSHAN',
                 'COUNTRY_PLC_CD': 'CNKUS', 'KIND': 'INLAND', 'PLC_CD': 'KUS', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'LELIU(CNLUU) / CHINA', 'PLC_ENM': 'LELIU', 'PLC_NM': 'LELIU', 'COUNTRY_PLC_CD': 'CNLUU',
                 'KIND': 'PORT', 'PLC_CD': 'LUU', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'LIANHUASHAN(CNLIH) / CHINA', 'PLC_ENM': 'LIANHUASHAN', 'PLC_NM': 'LIANHUASHAN',
                 'COUNTRY_PLC_CD': 'CNLIH', 'KIND': 'PORT', 'PLC_CD': 'LIH', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'LIANYUNGANG(CNLYG) / CHINA', 'PLC_ENM': 'LIANYUNGANG', 'PLC_NM': 'LIANYUNGANG',
                 'COUNTRY_PLC_CD': 'CNLYG', 'KIND': 'PORT', 'PLC_CD': 'LYG', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'NANJING(CNNJI) / CHINA', 'PLC_ENM': 'NANJING', 'PLC_NM': 'NANJING',
                 'COUNTRY_PLC_CD': 'CNNJI', 'KIND': 'PORT', 'PLC_CD': 'NJI', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'NANSHA(CNNSA) / CHINA', 'PLC_ENM': 'NANSHA', 'PLC_NM': 'NANSHA', 'COUNTRY_PLC_CD': 'CNNSA',
                 'KIND': 'INLAND', 'PLC_CD': 'NSA', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'NANSHAN(CNNSH) / CHINA', 'PLC_ENM': 'NANSHAN', 'PLC_NM': 'NANSHAN',
                 'COUNTRY_PLC_CD': 'CNNSH', 'KIND': 'INLAND', 'PLC_CD': 'NSH', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'}, {'PORT_NM': 'NANTONG(CNNTG) / CHINA', 'PLC_ENM': 'NANTONG', 'PLC_NM': 'NANTONG',
                                       'COUNTRY_PLC_CD': 'CNNTG', 'KIND': 'INLAND', 'PLC_CD': 'NTG',
                                       'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'NINGBO(CNNGB) / CHINA', 'PLC_ENM': 'NINGBO', 'PLC_NM': 'NINGBO', 'COUNTRY_PLC_CD': 'CNNGB',
                 'KIND': 'PORT', 'PLC_CD': 'NGB', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'QINGDAO(CNTAO) / CHINA', 'PLC_ENM': 'QINGDAO', 'PLC_NM': 'QINGDAO',
                 'COUNTRY_PLC_CD': 'CNTAO', 'KIND': 'PORT', 'PLC_CD': 'TAO', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'RONGQI(CNROQ) / CHINA', 'PLC_ENM': 'RONGQI', 'PLC_NM': 'RONGQI', 'COUNTRY_PLC_CD': 'CNROQ',
                 'KIND': 'PORT', 'PLC_CD': 'ROQ', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'SANSHAN(CNNHS) / CHINA', 'PLC_ENM': 'SANSHAN', 'PLC_NM': 'SANSHAN',
                 'COUNTRY_PLC_CD': 'CNNHS', 'KIND': 'PORT', 'PLC_CD': 'NHS', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'SANSHUI(CNSJQ) / CHINA', 'PLC_ENM': 'SANSHUI', 'PLC_NM': 'SANSHUI',
                 'COUNTRY_PLC_CD': 'CNSJQ', 'KIND': 'PORT', 'PLC_CD': 'SJQ', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'SHANGHAI(CNSHA) / CHINA', 'PLC_ENM': 'SHANGHAI', 'PLC_NM': 'SHANGHAI',
                 'COUNTRY_PLC_CD': 'CNSHA', 'KIND': 'PORT', 'PLC_CD': 'SHA', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'SHANTOU(CNSWA) / CHINA', 'PLC_ENM': 'SHANTOU', 'PLC_NM': 'SHANTOU',
                 'COUNTRY_PLC_CD': 'CNSWA', 'KIND': 'PORT', 'PLC_CD': 'SWA', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'SHEKOU(CNSHK) / CHINA', 'PLC_ENM': 'SHEKOU', 'PLC_NM': 'SHEKOU', 'COUNTRY_PLC_CD': 'CNSHK',
                 'KIND': 'PORT', 'PLC_CD': 'SHK', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'SHENWAN(CNSNW) / CHINA', 'PLC_ENM': 'SHENWAN', 'PLC_NM': 'SHENWAN',
                 'COUNTRY_PLC_CD': 'CNSNW', 'KIND': 'PORT', 'PLC_CD': 'SNW', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'SUZHOU(CNSUH) / CHINA', 'PLC_ENM': 'SUZHOU', 'PLC_NM': 'SUZHOU', 'COUNTRY_PLC_CD': 'CNSUH',
                 'KIND': 'INLAND', 'PLC_CD': 'SUH', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'TAI PING(CNTAI) / CHINA', 'PLC_ENM': 'TAI PING', 'PLC_NM': 'TAI PING',
                 'COUNTRY_PLC_CD': 'CNTAI', 'KIND': 'PORT', 'PLC_CD': 'TAI', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'TAICANG(CNTAC) / CHINA', 'PLC_ENM': 'TAICANG', 'PLC_NM': 'TAICANG',
                 'COUNTRY_PLC_CD': 'CNTAC', 'KIND': 'PORT', 'PLC_CD': 'TAC', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'TAIZHOU(CNTZO) / CHINA', 'PLC_ENM': 'TAIZHOU', 'PLC_NM': 'TAIZHOU',
                 'COUNTRY_PLC_CD': 'CNTZO', 'KIND': 'INLAND', 'PLC_CD': 'TZO', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'}, {'PORT_NM': 'TIANJIN(CNTSN) / CHINA', 'PLC_ENM': 'TIANJIN', 'PLC_NM': 'TIANJIN',
                                       'COUNTRY_PLC_CD': 'CNTSN', 'KIND': 'INLAND', 'PLC_CD': 'TSN',
                                       'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'WEIHAI(CNWEI) / CHINA', 'PLC_ENM': 'WEIHAI', 'PLC_NM': 'WEIHAI', 'COUNTRY_PLC_CD': 'CNWEI',
                 'KIND': 'INLAND', 'PLC_CD': 'WEI', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'WENZHOU(CNWNZ) / CHINA', 'PLC_ENM': 'WENZHOU', 'PLC_NM': 'WENZHOU',
                 'COUNTRY_PLC_CD': 'CNWNZ', 'KIND': 'PORT', 'PLC_CD': 'WNZ', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'WUHAN(CNWUP) / CHINA', 'PLC_ENM': 'WUHAN', 'PLC_NM': 'WUHAN', 'COUNTRY_PLC_CD': 'CNWUP',
                 'KIND': 'PORT', 'PLC_CD': 'WUP', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'WUHU(CNWHI) / CHINA', 'PLC_ENM': 'WUHU', 'PLC_NM': 'WUHU', 'COUNTRY_PLC_CD': 'CNWHI',
                 'KIND': 'PORT', 'PLC_CD': 'WHI', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'WUJIANG(CNWUJ) / CHINA', 'PLC_ENM': 'WUJIANG', 'PLC_NM': 'WUJIANG',
                 'COUNTRY_PLC_CD': 'CNWUJ', 'KIND': 'INLAND', 'PLC_CD': 'WUJ', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'WUXI(CNWUX) / CHINA', 'PLC_ENM': 'WUXI', 'PLC_NM': 'WUXI', 'COUNTRY_PLC_CD': 'CNWUX',
                 'KIND': 'INLAND', 'PLC_CD': 'WUX', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'XIAMEN(CNXMN) / CHINA', 'PLC_ENM': 'XIAMEN', 'PLC_NM': 'XIAMEN', 'COUNTRY_PLC_CD': 'CNXMN',
                 'KIND': 'PORT', 'PLC_CD': 'XMN', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'XIAOLAN(CNXAO) / CHINA', 'PLC_ENM': 'XIAOLAN', 'PLC_NM': 'XIAOLAN',
                 'COUNTRY_PLC_CD': 'CNXAO', 'KIND': 'PORT', 'PLC_CD': 'XAO', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'XIAOSHAN(CNXAS) / CHINA', 'PLC_ENM': 'XIAOSHAN', 'PLC_NM': 'XIAOSHAN',
                 'COUNTRY_PLC_CD': 'CNXAS', 'KIND': 'INLAND', 'PLC_CD': 'XAS', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'}, {'PORT_NM': 'XINGANG(CNTXG) / CHINA', 'PLC_ENM': 'XINGANG', 'PLC_NM': 'XINGANG',
                                       'COUNTRY_PLC_CD': 'CNTXG', 'KIND': 'PORT', 'PLC_CD': 'TXG',
                                       'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'YANGZHOU(CNYZH) / CHINA', 'PLC_ENM': 'YANGZHOU', 'PLC_NM': 'YANGZHOU',
                 'COUNTRY_PLC_CD': 'CNYZH', 'KIND': 'INLAND', 'PLC_CD': 'YZH', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'YANTAI(CNYNT) / CHINA', 'PLC_ENM': 'YANTAI', 'PLC_NM': 'YANTAI', 'COUNTRY_PLC_CD': 'CNYNT',
                 'KIND': 'PORT', 'PLC_CD': 'YNT', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'YICHANG(CNYIC) / CHINA', 'PLC_ENM': 'YICHANG', 'PLC_NM': 'YICHANG',
                 'COUNTRY_PLC_CD': 'CNYIC', 'KIND': 'PORT', 'PLC_CD': 'YIC', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'ZHANGJIAGANG(CNZJG) / CHINA', 'PLC_ENM': 'ZHANGJIAGANG', 'PLC_NM': 'ZHANGJIAGANG',
                 'COUNTRY_PLC_CD': 'CNZJG', 'KIND': 'PORT', 'PLC_CD': 'ZJG', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'ZHENJIANG(CNZHE) / CHINA', 'PLC_ENM': 'ZHENJIANG', 'PLC_NM': 'ZHENJIANG',
                 'COUNTRY_PLC_CD': 'CNZHE', 'KIND': 'INLAND', 'PLC_CD': 'ZHE', 'COUNTRY_NM': 'CHINA',
                 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'ZHONGSHAN(CNZSN) / CHINA', 'PLC_ENM': 'ZHONGSHAN', 'PLC_NM': 'ZHONGSHAN',
                 'COUNTRY_PLC_CD': 'CNZSN', 'KIND': 'PORT', 'PLC_CD': 'ZSN', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'},
                {'PORT_NM': 'ZHUHAI PT  (CNZUH) / CHINA', 'PLC_ENM': 'ZHUHAI PT  ', 'PLC_NM': 'ZHUHAI PT  ',
                 'COUNTRY_PLC_CD': 'CNZUH', 'KIND': 'PORT', 'PLC_CD': 'ZUH', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'}]
            self.global_other_port = [
                {'PORT_NM': 'HONGKONG(HKHKG) / HONGKONG', 'PLC_ENM': 'HONGKONG', 'PLC_NM': 'HONGKONG',
                 'COUNTRY_PLC_CD': 'HKHKG', 'KIND': 'PORT', 'PLC_CD': 'HKG', 'COUNTRY_NM': 'HONGKONG',
                 'COUNTRY_CD': 'HK'},
                {'PORT_NM': 'CHIBA(JPCHB) / JAPAN', 'PLC_ENM': 'CHIBA', 'PLC_NM': 'CHIBA', 'COUNTRY_PLC_CD': 'JPCHB',
                 'KIND': 'PORT', 'PLC_CD': 'CHB', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'HAKATA(JPHKT) / JAPAN', 'PLC_ENM': 'HAKATA', 'PLC_NM': 'HAKATA', 'COUNTRY_PLC_CD': 'JPHKT',
                 'KIND': 'PORT', 'PLC_CD': 'HKT', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'HIROSHIMA(JPHIJ) / JAPAN', 'PLC_ENM': 'HIROSHIMA', 'PLC_NM': 'HIROSHIMA',
                 'COUNTRY_PLC_CD': 'JPHIJ', 'KIND': 'PORT', 'PLC_CD': 'HIJ', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'KANAZAWA(JPKNZ) / JAPAN', 'PLC_ENM': 'KANAZAWA', 'PLC_NM': 'KANAZAWA',
                 'COUNTRY_PLC_CD': 'JPKNZ', 'KIND': 'PORT', 'PLC_CD': 'KNZ', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'KOBE(JPUKB) / JAPAN', 'PLC_ENM': 'KOBE', 'PLC_NM': 'KOBE', 'COUNTRY_PLC_CD': 'JPUKB',
                 'KIND': 'PORT', 'PLC_CD': 'UKB', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'MIZUSHIMA(JPMIZ) / JAPAN', 'PLC_ENM': 'MIZUSHIMA', 'PLC_NM': 'MIZUSHIMA',
                 'COUNTRY_PLC_CD': 'JPMIZ', 'KIND': 'PORT', 'PLC_CD': 'MIZ', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'MOJI(JPMOJ) / JAPAN', 'PLC_ENM': 'MOJI', 'PLC_NM': 'MOJI', 'COUNTRY_PLC_CD': 'JPMOJ',
                 'KIND': 'PORT', 'PLC_CD': 'MOJ', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'NAGOYA(JPNGO) / JAPAN', 'PLC_ENM': 'NAGOYA', 'PLC_NM': 'NAGOYA', 'COUNTRY_PLC_CD': 'JPNGO',
                 'KIND': 'PORT', 'PLC_CD': 'NGO', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'NIIGATA(JPKIJ) / JAPAN', 'PLC_ENM': 'NIIGATA', 'PLC_NM': 'NIIGATA',
                 'COUNTRY_PLC_CD': 'JPKIJ', 'KIND': 'PORT', 'PLC_CD': 'KIJ', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'OSAKA(JPOSA) / JAPAN', 'PLC_ENM': 'OSAKA', 'PLC_NM': 'OSAKA', 'COUNTRY_PLC_CD': 'JPOSA',
                 'KIND': 'PORT', 'PLC_CD': 'OSA', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'SHIMIZU(JPSMZ) / JAPAN', 'PLC_ENM': 'SHIMIZU', 'PLC_NM': 'SHIMIZU',
                 'COUNTRY_PLC_CD': 'JPSMZ', 'KIND': 'PORT', 'PLC_CD': 'SMZ', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'TAKAMATSU(JPTAK) / JAPAN', 'PLC_ENM': 'TAKAMATSU', 'PLC_NM': 'TAKAMATSU',
                 'COUNTRY_PLC_CD': 'JPTAK', 'KIND': 'PORT', 'PLC_CD': 'TAK', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'TOKYO(JPTYO) / JAPAN', 'PLC_ENM': 'TOKYO', 'PLC_NM': 'TOKYO', 'COUNTRY_PLC_CD': 'JPTYO',
                 'KIND': 'PORT', 'PLC_CD': 'TYO', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'TOYAMASHINKO(JPTOS) / JAPAN', 'PLC_ENM': 'TOYAMASHINKO', 'PLC_NM': 'TOYAMASHINKO',
                 'COUNTRY_PLC_CD': 'JPTOS', 'KIND': 'PORT', 'PLC_CD': 'TOS', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'TOYOHASHI(JPTHS) / JAPAN', 'PLC_ENM': 'TOYOHASHI', 'PLC_NM': 'TOYOHASHI',
                 'COUNTRY_PLC_CD': 'JPTHS', 'KIND': 'PORT', 'PLC_CD': 'THS', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'TSURUGA(JPTRG) / JAPAN', 'PLC_ENM': 'TSURUGA', 'PLC_NM': 'TSURUGA',
                 'COUNTRY_PLC_CD': 'JPTRG', 'KIND': 'PORT', 'PLC_CD': 'TRG', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'YOKKAICHI(JPYKK) / JAPAN', 'PLC_ENM': 'YOKKAICHI', 'PLC_NM': 'YOKKAICHI',
                 'COUNTRY_PLC_CD': 'JPYKK', 'KIND': 'PORT', 'PLC_CD': 'YKK', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'YOKOHAMA(JPYOK) / JAPAN', 'PLC_ENM': 'YOKOHAMA', 'PLC_NM': 'YOKOHAMA',
                 'COUNTRY_PLC_CD': 'JPYOK', 'KIND': 'PORT', 'PLC_CD': 'YOK', 'COUNTRY_NM': 'JAPAN', 'COUNTRY_CD': 'JP'},
                {'PORT_NM': 'BUSAN(KRPUS) / KOREA', 'PLC_ENM': 'BUSAN', 'PLC_NM': 'BUSAN', 'COUNTRY_PLC_CD': 'KRPUS',
                 'KIND': 'PORT', 'PLC_CD': 'PUS', 'COUNTRY_NM': 'KOREA', 'COUNTRY_CD': 'KR'},
                {'PORT_NM': 'BUSAN NEW PORT(KRBNP) / KOREA', 'PLC_ENM': 'BUSAN NEW PORT', 'PLC_NM': 'BUSAN NEW PORT',
                 'COUNTRY_PLC_CD': 'KRBNP', 'KIND': 'PORT', 'PLC_CD': 'BNP', 'COUNTRY_NM': 'KOREA', 'COUNTRY_CD': 'KR'},
                {'PORT_NM': 'INCHEON(KRINC) / KOREA', 'PLC_ENM': 'INCHEON', 'PLC_NM': 'INCHEON',
                 'COUNTRY_PLC_CD': 'KRINC', 'KIND': 'PORT', 'PLC_CD': 'INC', 'COUNTRY_NM': 'KOREA', 'COUNTRY_CD': 'KR'},
                {'PORT_NM': 'KWANGYANG(KRKAN) / KOREA', 'PLC_ENM': 'KWANGYANG', 'PLC_NM': 'KWANGYANG',
                 'COUNTRY_PLC_CD': 'KRKAN', 'KIND': 'PORT', 'PLC_CD': 'KAN', 'COUNTRY_NM': 'KOREA', 'COUNTRY_CD': 'KR'},
                {'PORT_NM': 'PYEONGTAEK(KRPTK) / KOREA', 'PLC_ENM': 'PYEONGTAEK', 'PLC_NM': 'PYEONGTAEK',
                 'COUNTRY_PLC_CD': 'KRPTK', 'KIND': 'PORT', 'PLC_CD': 'PTK', 'COUNTRY_NM': 'KOREA', 'COUNTRY_CD': 'KR'},
                {'PORT_NM': 'SEOUL(KRSEL) / KOREA', 'PLC_ENM': 'SEOUL', 'PLC_NM': 'SEOUL', 'COUNTRY_PLC_CD': 'KRSEL',
                 'KIND': 'INLAND', 'PLC_CD': 'SEL', 'COUNTRY_NM': 'KOREA', 'COUNTRY_CD': 'KR'},
                {'PORT_NM': 'ULSAN(KRUSN) / KOREA', 'PLC_ENM': 'ULSAN', 'PLC_NM': 'ULSAN', 'COUNTRY_PLC_CD': 'KRUSN',
                 'KIND': 'PORT', 'PLC_CD': 'USN', 'COUNTRY_NM': 'KOREA', 'COUNTRY_CD': 'KR'},
                {'PORT_NM': 'BANGKOK(THBKK) / THAILAND', 'PLC_ENM': 'BANGKOK', 'PLC_NM': 'BANGKOK',
                 'COUNTRY_PLC_CD': 'THBKK', 'KIND': 'PORT', 'PLC_CD': 'BKK', 'COUNTRY_NM': 'THAILAND',
                 'COUNTRY_CD': 'TH'},
                {'PORT_NM': 'BANGKOK MODERN TERMINAL(THBMT) / THAILAND', 'PLC_ENM': 'BANGKOK MODERN TERMINAL',
                 'PLC_NM': 'BANGKOK MODERN TERMINAL', 'COUNTRY_PLC_CD': 'THBMT', 'KIND': 'INLAND', 'PLC_CD': 'BMT',
                 'COUNTRY_NM': 'THAILAND', 'COUNTRY_CD': 'TH'},
                {'PORT_NM': 'LAEM CHABANG(THLCH) / THAILAND', 'PLC_ENM': 'LAEM CHABANG', 'PLC_NM': 'LAEM CHABANG',
                 'COUNTRY_PLC_CD': 'THLCH', 'KIND': 'PORT', 'PLC_CD': 'LCH', 'COUNTRY_NM': 'THAILAND',
                 'COUNTRY_CD': 'TH'},
                {'PORT_NM': 'LAT KRABANG(THLKR) / THAILAND', 'PLC_ENM': 'LAT KRABANG', 'PLC_NM': 'LAT KRABANG',
                 'COUNTRY_PLC_CD': 'THLKR', 'KIND': 'INLAND', 'PLC_CD': 'LKR', 'COUNTRY_NM': 'THAILAND',
                 'COUNTRY_CD': 'TH'},
                {'PORT_NM': 'PHRAPRADAENG(THPRG) / THAILAND', 'PLC_ENM': 'PHRAPRADAENG', 'PLC_NM': 'PHRAPRADAENG',
                 'COUNTRY_PLC_CD': 'THPRG', 'KIND': 'INLAND', 'PLC_CD': 'PRG', 'COUNTRY_NM': 'THAILAND',
                 'COUNTRY_CD': 'TH'},
                {'PORT_NM': 'SAHATHAI(THSHT) / THAILAND', 'PLC_ENM': 'SAHATHAI', 'PLC_NM': 'SAHATHAI',
                 'COUNTRY_PLC_CD': 'THSHT', 'KIND': 'INLAND', 'PLC_CD': 'SHT', 'COUNTRY_NM': 'THAILAND',
                 'COUNTRY_CD': 'TH'},
                {'PORT_NM': 'SIAM CONTAINER TERMINAL-SCT(THSCT) / THAILAND', 'PLC_ENM': 'SIAM CONTAINER TERMINAL-SCT',
                 'PLC_NM': 'SIAM CONTAINER TERMINAL-SCT', 'COUNTRY_PLC_CD': 'THSCT', 'KIND': 'INLAND', 'PLC_CD': 'SCT',
                 'COUNTRY_NM': 'THAILAND', 'COUNTRY_CD': 'TH'},
                {'PORT_NM': 'THAI PROSPERITY TERMINAL(THTPT) / THAILAND', 'PLC_ENM': 'THAI PROSPERITY TERMINAL',
                 'PLC_NM': 'THAI PROSPERITY TERMINAL', 'COUNTRY_PLC_CD': 'THTPT', 'KIND': 'INLAND', 'PLC_CD': 'TPT',
                 'COUNTRY_NM': 'THAILAND', 'COUNTRY_CD': 'TH'},
                {'PORT_NM': 'HAIPHONG(VNHPH) / VIETNAM', 'PLC_ENM': 'HAIPHONG', 'PLC_NM': 'HAIPHONG',
                 'COUNTRY_PLC_CD': 'VNHPH', 'KIND': 'PORT', 'PLC_CD': 'HPH', 'COUNTRY_NM': 'VIETNAM',
                 'COUNTRY_CD': 'VN'},
                {'PORT_NM': 'HANOI(VNHAN) / VIETNAM', 'PLC_ENM': 'HANOI', 'PLC_NM': 'HANOI', 'COUNTRY_PLC_CD': 'VNHAN',
                 'KIND': 'INLAND', 'PLC_CD': 'HAN', 'COUNTRY_NM': 'VIETNAM', 'COUNTRY_CD': 'VN'},
                {'PORT_NM': 'HOCHIMINH CITY(VNSGN) / VIETNAM', 'PLC_ENM': 'HOCHIMINH CITY', 'PLC_NM': 'HOCHIMINH CITY',
                 'COUNTRY_PLC_CD': 'VNSGN', 'KIND': 'PORT', 'PLC_CD': 'SGN', 'COUNTRY_NM': 'VIETNAM',
                 'COUNTRY_CD': 'VN'},
                {'PORT_NM': 'ICD GIALAM(VNGIA) / VIETNAM', 'PLC_ENM': 'ICD GIALAM', 'PLC_NM': 'ICD GIALAM',
                 'COUNTRY_PLC_CD': 'VNGIA', 'KIND': 'INLAND', 'PLC_CD': 'GIA', 'COUNTRY_NM': 'VIETNAM',
                 'COUNTRY_CD': 'VN'}, {'PORT_NM': 'ICD PHUOCLONG 1(VNPLF) / VIETNAM', 'PLC_ENM': 'ICD PHUOCLONG 1',
                                       'PLC_NM': 'ICD PHUOCLONG 1', 'COUNTRY_PLC_CD': 'VNPLF', 'KIND': 'INLAND',
                                       'PLC_CD': 'PLF', 'COUNTRY_NM': 'VIETNAM', 'COUNTRY_CD': 'VN'},
                {'PORT_NM': 'ICD PHUOCLONG 3(VNPLT) / VIETNAM', 'PLC_ENM': 'ICD PHUOCLONG 3',
                 'PLC_NM': 'ICD PHUOCLONG 3', 'COUNTRY_PLC_CD': 'VNPLT', 'KIND': 'INLAND', 'PLC_CD': 'PLT',
                 'COUNTRY_NM': 'VIETNAM', 'COUNTRY_CD': 'VN'},
                {'PORT_NM': 'ICD SOTRANS(VNSOT) / VIETNAM', 'PLC_ENM': 'ICD SOTRANS', 'PLC_NM': 'ICD SOTRANS',
                 'COUNTRY_PLC_CD': 'VNSOT', 'KIND': 'INLAND', 'PLC_CD': 'SOT', 'COUNTRY_NM': 'VIETNAM',
                 'COUNTRY_CD': 'VN'},
                {'PORT_NM': 'ICD TIEN SON(VNTSO) / VIETNAM', 'PLC_ENM': 'ICD TIEN SON', 'PLC_NM': 'ICD TIEN SON',
                 'COUNTRY_PLC_CD': 'VNTSO', 'KIND': 'INLAND', 'PLC_CD': 'TSO', 'COUNTRY_NM': 'VIETNAM',
                 'COUNTRY_CD': 'VN'}, {'PORT_NM': 'ICD TRANSIMEX SG(VNFAD) / VIETNAM', 'PLC_ENM': 'ICD TRANSIMEX SG',
                                       'PLC_NM': 'ICD TRANSIMEX SG', 'COUNTRY_PLC_CD': 'VNFAD', 'KIND': 'INLAND',
                                       'PLC_CD': 'FAD', 'COUNTRY_NM': 'VIETNAM', 'COUNTRY_CD': 'VN'},
                {'PORT_NM': 'TAN CANG HIEP PHUOC PORT  (VNTCH) / VIETNAM', 'PLC_ENM': 'TAN CANG HIEP PHUOC PORT  ',
                 'PLC_NM': 'TAN CANG HIEP PHUOC PORT  ', 'COUNTRY_PLC_CD': 'VNTCH', 'KIND': 'INLAND', 'PLC_CD': 'TCH',
                 'COUNTRY_NM': 'VIETNAM', 'COUNTRY_CD': 'VN'},
                {'PORT_NM': 'TANAMEXCO ICD (VNTAM) / VIETNAM', 'PLC_ENM': 'TANAMEXCO ICD ', 'PLC_NM': 'TANAMEXCO ICD ',
                 'COUNTRY_PLC_CD': 'VNTAM', 'KIND': 'INLAND', 'PLC_CD': 'TAM', 'COUNTRY_NM': 'VIETNAM',
                 'COUNTRY_CD': 'VN'},
                {'PORT_NM': 'VUNG TAU (VNVUN) / VIETNAM', 'PLC_ENM': 'VUNG TAU ', 'PLC_NM': 'VUNG TAU ',
                 'COUNTRY_PLC_CD': 'VNVUN', 'KIND': 'PORT', 'PLC_CD': 'VUN', 'COUNTRY_NM': 'VIETNAM',
                 'COUNTRY_CD': 'VN'}]

            logging.info('完成所有港口请求')
            logging.info(self.global_cn_port)
            logging.info(self.global_other_port)

            # global_cn_port 数据结构
            # {'PORT_NM': 'BEIHAI(CNBHY) / CHINA', 'PLC_ENM': 'BEIHAI', 'PLC_NM': 'BEIHAI', 'COUNTRY_PLC_CD': 'CNBHY', 'KIND': 'PORT', 'PLC_CD': 'BHY', 'COUNTRY_NM': 'CHINA', 'COUNTRY_CD': 'CN'}
            time.sleep(1)
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#pol_country_cd > option:nth-child(2)')))

            for cnindex, c_h_p in enumerate(self.global_cn_port):


                # # 测试
                # if cnindex != 7:  # DALIAN
                #     continue
                if cnindex < 3:  # DALIAN
                    continue

                pItem['port'] = c_h_p['PLC_NM']
                pItem['portCode'] = c_h_p['COUNTRY_PLC_CD']
                yield pItem

                for ohindex, o_h_p in enumerate(self.global_other_port):
                    # # 测试
                    # if ohindex != 34:  # HAIPHONG
                    #     continue

                    #######################################
                    try:
                        self.driver.find_element_by_id('btn_pol_port').click()
                        # 可删除 next line
                        # time.sleep(1)
                        self.driver.find_element_by_id('pol_country_cd').click()
                        # time.sleep(1)
                        Select(self.driver.find_element_by_id('pol_country_cd')).select_by_value(
                            c_h_p['COUNTRY_CD'])  # 选择国家
                        if self.pol_current_country == c_h_p['COUNTRY_CD']:
                            time.sleep(1)
                        else:
                            time.sleep(10)  # 接口渲染
                            self.pol_current_country = c_h_p['COUNTRY_CD']
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '#pol_port_cd > option:nth-child(2)')))

                        # 可删除 next 2 line
                        self.driver.find_element_by_id('pol_port_cd').click()
                        # time.sleep(3)

                        Select(self.driver.find_element_by_id('pol_port_cd')).select_by_value(c_h_p['PLC_CD'])
                        # 可删除 next line
                        time.sleep(1)
                    except Exception as e:
                        logging.error(e) #todo
                        continue
                    ###############################################
                    pItem['port'] = o_h_p['PLC_NM']
                    pItem['portCode'] = o_h_p['COUNTRY_PLC_CD']
                    yield pItem

                    # 港口组合
                    pgItem['portPol'] = c_h_p['COUNTRY_PLC_CD']
                    pgItem['portNamePol'] = c_h_p['PLC_NM']
                    pgItem['portPod'] = o_h_p['COUNTRY_PLC_CD']
                    pgItem['portNamePod'] = o_h_p['PLC_NM']
                    yield pgItem

                    try:
                        try:
                            self.driver.find_element_by_id('btn_pod_port').click()
                            # 可删除 next line
                            # time.sleep(1)
                            self.driver.find_element_by_id('pod_country_cd').click()
                            time.sleep(0.5)
                        except Exception as e:
                            logging.error(e) #todo
                            continue
                        try:
                            Select(self.driver.find_element_by_id('pod_country_cd')).select_by_value(
                                o_h_p['COUNTRY_CD'])  # 选择国家
                            if self.pod_current_country == o_h_p['COUNTRY_CD']:
                                time.sleep(1)
                            else:
                                time.sleep(10)  # 接口渲染
                                self.pod_current_country = o_h_p['COUNTRY_CD']
                        except Exception as e:
                            logging.error(e)
                            continue
                        try:
                            WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '#pod_port_cd > option:nth-child(2)')))
                            # 可删除 next 2 line
                            self.driver.find_element_by_id('pod_port_cd').click()
                            time.sleep(1)
                        except Exception as e:
                            logging.error(e)
                            continue

                        Select(self.driver.find_element_by_id('pod_port_cd')).select_by_value(o_h_p['PLC_CD'])
                    except Exception as e:
                        logging.error(e)
                        continue

                    for date_item in self.date:
                        try:
                            Select(self.driver.find_element_by_id('sYear')).select_by_value(date_item['y'])  # 年份
                            Select(self.driver.find_element_by_id('sMonth')).select_by_value(date_item['m'])  # 月份

                            # 判断下拉未关闭
                            # pol_sel_vi = EC.invisibility_of_element_located((By.ID, 'div_pol_search'))
                            pol_sel_vi = self.driver.find_element_by_id('div_pol_search').is_displayed()
                            if pol_sel_vi:
                                self.driver.find_element_by_id('btn_pol_port').click()

                            # pod_sel_vi = EC.invisibility_of_element_located((By.ID, 'div_pod_search'))
                            pod_sel_vi = self.driver.find_element_by_id('div_pod_search').is_displayed()
                            if pod_sel_vi:
                                self.driver.find_element_by_id('btn_pod_port').click()

                            self.driver.find_element_by_id('WEB_201_INQ').click()

                            time.sleep(2)
                        except Exception as e:
                            logging.error(e)
                            break

                        try:
                            # 检测查询
                            wil_i = 1
                            # while wil_i < 50000:
                            while wil_i:
                                wil_i += 1
                                has_alert = self.has_alert()
                                if has_alert:
                                    break
                                else:
                                    pass

                                has_detail = self.has_ele('calendar-list')
                                if has_detail:
                                    break
                                else:
                                    time.sleep(0.5)
                                    continue
                            if wil_i >= 10000:
                                self.fresh_page()
                                continue
                        except Exception as e:
                            logging.log(e)
                            self.fresh_page()
                            break

                        try:
                            # 获取alert对话框
                            dig_alert = self.driver.switch_to.alert
                            time.sleep(1)
                            t = dig_alert.text
                            dig_alert.accept()
                            time.sleep(1)  # 不等弹框不会消失
                            continue
                        except NoAlertPresentException:
                            try:
                                # wait
                                WebDriverWait(self.driver, 120).until(
                                    EC.invisibility_of_element_located((By.ID, 'loading-bar')))
                                # WebDriverWait(self.driver, 50).until(
                                #     EC.visibility_of_any_elements_located((By.CLASS_NAME, 'calendar-list')))
                            except Exception as e:
                                self.fresh_page()
                                continue

                            doc_1 = pq(self.driver.page_source)
                            # calTable = doc_1('#calTable')
                            # logging.info('日历')

                            lis = self.driver.find_elements_by_css_selector('li.calendar-list')
                            li_len = len(lis)
                            for index in range(li_len):
                                try:
                                    lis[index].click()
                                    time.sleep(1)
                                    source_2 = self.driver.page_source
                                    doc_2 = pq(self.driver.page_source)
                                    ex_detail = doc_2('div[class="detail-cont"][style="display: block;"]')
                                    div_ele = ex_detail.find('.detail-cont-sub')

                                    row = {
                                        'pol': c_h_p['COUNTRY_PLC_CD'],
                                        'podName': o_h_p['PLC_NM'],
                                        'pod': o_h_p['COUNTRY_PLC_CD'],
                                        'polName': c_h_p['PLC_NM'],
                                        'TRANSIT_LIST': []
                                    }
                                    for div_index, div_item in enumerate(div_ele.items()):
                                        vsl_nm = div_item.find('#vsl_nm').text()
                                        if not vsl_nm:
                                            continue
                                        vsl_nm_arr = vsl_nm.rsplit(' ', 1)
                                        if div_index == 0:
                                            row['VESSEL'] = vsl_nm_arr[0]
                                            row['VOYAGE'] = vsl_nm_arr[1] if len(vsl_nm_arr) > 1 else ''
                                            row['ETD'] = div_item.find('#pol_etd_tm').text().split(' ')[0]
                                            row['ETA'] = div_item.find('#pod_eta_tm').text().split(' ')[0]
                                            row['POL_TERMINAL'] = div_item.find('#pol_tmn').text()
                                            row['POD_TERMINAL'] = div_item.find('#pod_tmn').text()
                                            row['TRANSIT_TIME'] = ''
                                            row['TRANSIT_LIST'] = []
                                            row['IS_TRANSIT'] = 0  # 确认为中转为1，直达为0, 默认为0
                                        else:
                                            row['POD_TERMINAL'] = div_item.find('#pod_tmn').text()
                                            row['ETA'] = div_item.find('#pod_eta_tm').text().split(' ')[0]

                                            row['IS_TRANSIT'] = 1
                                            row['TRANSIT_TIME'] = ''
                                            row['TRANSIT_LIST'].append({
                                                'TRANSIT_PORT_EN': div_item.find('#pol').text(),
                                                'TRANS_VESSEL': vsl_nm_arr[0],
                                                'TRANS_VOYAGE': vsl_nm_arr[1] if len(vsl_nm_arr) > 1 else '',
                                            })
                                    etd_s = row['ETD']
                                    eta_s = row['ETA']
                                    date1 = datetime.datetime(int(etd_s[0:4]), int(etd_s[5:7]),
                                                              int(etd_s[8:10]))
                                    date2 = datetime.datetime(int(eta_s[0:4]), int(eta_s[5:7]),
                                                              int(eta_s[8:10]))
                                    logging.info(date1)
                                    logging.info(date2)
                                    row['TRANSIT_TIME'] = (date2 - date1).days
                                    logging.info(row)
                                    for field in gItem.fields:
                                        if field in row.keys():
                                            gItem[field] = row.get(field)
                                    yield gItem

                                    links = self.driver.find_elements_by_partial_link_text('Close')
                                    for link in links:
                                        try:
                                            link.click()
                                        except Exception as e:
                                            pass
                                    time.sleep(1)
                                    # 重新获取
                                    lis = self.driver.find_elements_by_css_selector('li.calendar-list')
                                except Exception as e:
                                    logging.error(e)
                                    continue
                        finally:
                            pass
                            # # 判断下拉未关闭
                            # # pol_sel_vi = EC.invisibility_of_element_located((By.ID, 'div_pol_search'))
                            # pol_sel_vi = self.driver.find_element_by_id('div_pol_search').is_displayed()
                            # if pol_sel_vi:
                            #     self.driver.find_element_by_id('btn_pol_port').click()
                            #
                            # # pod_sel_vi = EC.invisibility_of_element_located((By.ID, 'div_pod_search'))
                            # pod_sel_vi = self.driver.find_element_by_id('div_pod_search').is_displayed()
                            # if pod_sel_vi:
                            #     self.driver.find_element_by_id('btn_pod_port').click()

            self.driver.quit()  # 关闭
        except Exception as e:
            self.driver.quit()  # 关闭
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

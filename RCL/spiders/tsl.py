# -*- coding: utf-8 -*-
import logging
import time

import requests
import scrapy
from pyquery import PyQuery as pq
from scrapy import FormRequest

from RCL.items import PortGroupItem, PortItem, GroupItem

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options


def get_ports(options):
    ports = []
    for option in options:
        value = option.get_attribute('value')
        name = option.text
        ports.append({'value': value, 'name': name})
    return ports


class TslSpider(scrapy.Spider):
    name = 'TSQD'
    allowed_domains = ['http://vgm.tslines.com']
    start_urls = ['http://vgm.tslines.com/VSM/LineServiceByPort.aspx']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            'RCL.pipelines.MysqlPipeline': 300
        }
    }

    global_cn_port = []
    global_other_port = []

    localtime = time.localtime(time.time())
    year = str(localtime.tm_year)
    month = str(localtime.tm_mon)
    day = str(localtime.tm_mday)
    if len(day) < 2:
        day = '0' + day

    next2_month = str((int(month) + 2) % 12)
    if len(next2_month) < 2:
        next2_month = '0' + next2_month
    next2_year = (int((int(month) + 2) / 12) + int(year))

    def __init__(self,**kwargs):
        self._init_brower()

    def _init_brower(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        No_Image_loading = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", No_Image_loading)
        # chrome_options.binary_location = r"D:\soft\googlechrome\Application\77.0.3865.120\chrome.exe"
        # epath = "D:/work/chromedriver.exe"
        epath = "/usr/bin/chromedriver"
        self.driver = webdriver.Chrome(executable_path=epath, chrome_options=chrome_options)
        # 设置超时，双重保险,设置后derver 就死了
        self.driver.set_page_load_timeout(30)
        self.driver.set_script_timeout(30)

    def parse(self, response):
        doc = pq(response.text)
        options = doc('#DropDownList3 option')
        pgItem = PortGroupItem()
        pItem = PortItem()
        gItem = GroupItem()
        c_h_c = []
        o_h_c = []
        for option in options.items():
            va = option.attr('value')
            name = option.text()
            country = {
                'value': va,
                'name': name
            }
            if va != '0':
                if name == 'CHINA':
                    c_h_c.append({'value': va, 'name': name})
                elif name == 'HONGKONG':
                    c_h_c.append({'value': va, 'name': name})
                    o_h_c.append({'value': va, 'name': name})
                else:
                    o_h_c.append({'value': va, 'name': name})

        self.driver.get(self.start_urls[0])
        time.sleep(1)
        for c_h in c_h_c:
            # self.driver.find_element_by_id('DropDownList3').click()
            # time.sleep(1)
            try:
                Select(self.driver.find_element_by_id('DropDownList3')).select_by_value(c_h['value'])

                time.sleep(1)

                c_h_options = self.driver.find_elements_by_css_selector('#DropDownList1 option')

                c_h_ports = get_ports(c_h_options)
            except Exception as e:
                continue
            for c_h_port in c_h_ports:
                pItem['port'] = c_h_port['value']
                pItem['portCode'] = c_h_port['name']
                yield pItem
                # # 测试
                # if c_h_port['name'] != 'DALIAN':
                #     continue
                try:
                    # self.driver.find_element_by_id('DropDownList1').click()
                    # time.sleep(1)
                    Select(self.driver.find_element_by_id('DropDownList1')).select_by_value(
                        c_h_port['value'])
                    time.sleep(1)
                except Exception as e:
                    logging.error('tsl error')
                    logging.error(e)
                    continue

                for o_h in o_h_c:
                    # # 测试
                    # if o_h['name'] != 'HONGKONG':
                    #     continue
                    try:
                        # self.driver.find_element_by_id('DropDownList4').click()
                        # time.sleep(1)
                        Select(self.driver.find_element_by_id('DropDownList4')).select_by_value(
                            o_h['value'])
                        time.sleep(1)
                        o_h_options = self.driver.find_elements_by_css_selector(
                            '#DropDownList2 option')
                        o_h_ports = get_ports(o_h_options)
                        for o_h_port in o_h_ports:
                            # 港口
                            pItem['port'] = o_h_port['value']
                            pItem['portCode'] = o_h_port['name']
                            yield pItem

                            # 港口组合
                            pgItem['portPol'] = c_h_port['value']
                            pgItem['portNamePol'] = c_h_port['name']
                            pgItem['portPod'] = o_h_port['value']
                            pgItem['portNamePod'] = o_h_port['name']
                            yield pgItem
                            try:
                                logging.info('港口数据:{}'.format(o_h_port))
                                # self.driver.find_element_by_id('DropDownList2').click()
                                # time.sleep(1)
                                Select(
                                    self.driver.find_element_by_id('DropDownList2')).select_by_value(
                                    o_h_port['value'])
                                time.sleep(1)

                                pol_start_el = self.driver.find_element_by_id('TextBox3')
                                pol_start_el.clear()
                                pol_start_el.send_keys("{}/{}/{}".format(self.year, self.month, self.day))
                                pol_end_el = self.driver.find_element_by_id('TextBox5')
                                pol_end_el.clear()
                                pol_end_el.send_keys("{}/{}/{}".format(self.next2_year, self.next2_month, '01'))
                                try:
                                    self.driver.find_element_by_id('Button2').click()
                                except Exception as e:
                                    logging.debug('网站超时')
                                    self.driver.quit()
                                    self._init_brower()
                                    self.driver.get(self.start_urls[0])
                                    time.sleep(1)
                                    Select(self.driver.find_element_by_id('DropDownList3')).select_by_value(
                                        c_h['value'])
                                    time.sleep(1)
                                    Select(self.driver.find_element_by_id('DropDownList1')).select_by_value(
                                        c_h_port['value'])
                                    Select(self.driver.find_element_by_id('DropDownList4')).select_by_value(
                                        o_h['value'])
                                    time.sleep(1)
                                    continue
                                time.sleep(1)
                                source = self.driver.page_source
                                listDoc = pq(source)
                                trs = listDoc('#GridView2 tr')

                                for tr in trs.items():
                                    tds = tr.find('td')
                                    if not tds:
                                        continue
                                    time_s = tds.eq(14).text()
                                    if time_s:
                                        time_i = int(time_s)
                                    else:
                                        time_i = 0
                                    row = {
                                        'ETD': tds.eq(10).text(),
                                        'VESSEL': tds.eq(1).text(),
                                        'VOYAGE': tds.eq(2).text(),
                                        'ETA': tds.eq(13).text(),
                                        'ROUTE_CODE': tds.eq(0).text(),
                                        'TRANSIT_TIME': time_i,
                                        'POL_TERMINAL': tds.eq(4).text(),
                                        'POD_TERMINAL': tds.eq(12).text(),
                                        'TRANSIT_LIST': [],
                                        'IS_TRANSIT': 0,  # 确认为中转为1，直达为0, 默认为0
                                        'pol': c_h_port['value'],
                                        'pod': o_h_port['value'],
                                        'polName': c_h_port['name'],
                                        'podName': o_h_port['name'],
                                    }
                                    logging.info(row)
                                    for field in gItem.fields:
                                        if field in row.keys():
                                            gItem[field] = row.get(field)
                                    yield gItem
                                self.driver.back()
                                time.sleep(1)
                            except Exception as e:
                                logging.error('tsl error')
                                logging.error(e)
                    except Exception as e:
                        logging.error('tsl error')
                        continue

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
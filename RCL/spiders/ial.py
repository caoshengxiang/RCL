# -*- coding: utf-8 -*-
import json
import logging
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
            'RCL.pipelines.MongoPipeline': 300
        }
    }

    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        No_Image_loading = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", No_Image_loading)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def parse(self, response):
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
            # source = self.driver.page_source
            # doc = pq(source)

            c_h_ports = get_ports(c_h_options)

            logging.info(c_h_ports)
            for c_h_port in c_h_ports:
                try:
                    logging.info('港口数据:{}'.format(c_h_port))
                    Select(self.driver.find_element_by_id('ctl00_CPHContent_ddlDepartureL')).select_by_value(
                        c_h_port['value'])
                    time.sleep(1)
                except Exception as e:
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
                                self.driver.back()
                                time.sleep(1)
                            except Exception as e:
                                logging.error(e)
                    except Exception as e:
                        continue

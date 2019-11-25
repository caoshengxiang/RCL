# -*- coding: utf-8 -*-
import json
import logging

import scrapy
from scrapy import FormRequest, Request
from pyquery import PyQuery as pq


class EasSpider(scrapy.Spider):
    name = 'eas'
    allowed_domains = ['http://ecomm.easline.com']
    start_urls = ['http://ecomm.easline.com/ecomm/ecxmm/weBBSys/Ssch/wecmBBSschP2PtFrame.aspx']

    custom_settings = {  # 指定配置的通道, 要对应找到每个爬虫指定的管道,settings里也要进行管道配置
        'ITEM_PIPELINES': {
            'RCL.pipelines.MongoPipeline': 300
        }
    }

    portUrl = 'http://ecomm.easline.com/ecomm/ecxmm/weBBSys/Ssch/wecmBBSschP2PtFrame.aspx/select_wecomBBSschP2PtFramePortList'

    def parse(self, response):
        doc = pq(response.text)
        __VIEWSTATE = doc('#__VIEWSTATE').attr('value')
        __EVENTVALIDATION = doc('#__EVENTVALIDATION').attr('value')
        logging.info(__VIEWSTATE)
        logging.info(__EVENTVALIDATION)

        # yield Request(url=self.portUrl,
        #               method='POST',
        #               body=json.dumps({'portname': '', 'inoutflag': 'out'}),
        #               meta={},
        #               callback=self.parse_port)
        yield FormRequest(url=self.portUrl,
                          method='POST',
                          meta={},
                          headers={'Content-Type':'application/json'},
                          callback=self.parse_port)

    def parse_port(self, response):
        portList = json.loads(response.text)
        logging.info('港口')
        logging.info(portList)

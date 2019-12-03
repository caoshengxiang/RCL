# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PortItem(scrapy.Item):
    # define the fields for your item here like:
    portCode = scrapy.Field()  # 船公司港口五字码
    port = scrapy.Field()  # 船公司港口英文名
    date = scrapy.Field()
    SCAC = scrapy.Field()


class GroupItem(scrapy.Item):
    # define the fields for your item here like:
    pol = scrapy.Field()  # code
    pod = scrapy.Field()
    polName = scrapy.Field()
    podName = scrapy.Field()
    useTime = scrapy.Field()
    date = scrapy.Field()
    IS_TRANSIT = scrapy.Field()  # 是否中转 确认为中转为1，直达为0
    VESSEL = scrapy.Field()  # 船名
    VOYAGE = scrapy.Field()  # 航次
    LPA = scrapy.Field()
    ETD = scrapy.Field()  # 离港时间
    ETA = scrapy.Field()  # 到港时间
    TRANSIT_TIME = scrapy.Field()  # 航程
    FLAG = scrapy.Field()
    TRANSIT_LIST = scrapy.Field()  # 中转
    ROUTE_CODE = scrapy.Field()  # 航线代码，没有就不存
    POL_TERMINAL = scrapy.Field()  # 起始码头 ，没有就不存
    POD_TERMINAL = scrapy.Field()  # 目的港码头，没有就不存
    SCAC = scrapy.Field()


class PortGroupItem(scrapy.Item):
    # define the fields for your item here like:
    date = scrapy.Field()
    portPol = scrapy.Field()
    portNamePol = scrapy.Field()
    portPod = scrapy.Field()
    portNamePod = scrapy.Field()
    content = scrapy.Field()
    status = scrapy.Field()
    userTime = scrapy.Field()
    SCAC = scrapy.Field()


class StaticsItem(scrapy.Item):
    SCAC = scrapy.Field()

    # 服务父航线名称
    ROUTE_PARENT = scrapy.Field()
    # 服务子航线名称
    ROUTE_NAME_EN = scrapy.Field()
    # 航线代码
    ROUTE_CODE = scrapy.Field()
    # 挂靠数据集合
    docking_list = scrapy.Field()

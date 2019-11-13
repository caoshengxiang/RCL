# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PortItem(scrapy.Item):
    # define the fields for your item here like:
    portCode = scrapy.Field()
    port = scrapy.Field()
    date = scrapy.Field()


class GroupItem(scrapy.Item):
    # define the fields for your item here like:
    pol = scrapy.Field()
    pod = scrapy.Field()
    polName = scrapy.Field()
    podName = scrapy.Field()
    useTime = scrapy.Field()
    date = scrapy.Field()
    IS_TRANSIT = scrapy.Field()
    VESSEL = scrapy.Field()
    VOYAGE = scrapy.Field()
    POL_NAME_EN = scrapy.Field()
    LPA = scrapy.Field()
    ETD = scrapy.Field()
    POD_NAME_EN = scrapy.Field()
    ETA = scrapy.Field()
    TRANSIT_TIME = scrapy.Field()
    FLAG = scrapy.Field()
    TransferCode = scrapy.Field()
    TransferName = scrapy.Field()


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

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# import pymongo
from datetime import datetime
from RCL.items import PortItem, PortGroupItem
from RCL.items import GroupItem
from RCL.model.dao import CommonDao
from RCL.model.models import NewSchedulesSpiderPort, NewSchedulesStatic, NewSchedulesDynamic, \
    NewSchedulesStaticDocking, NewSchedulesDynamicTransit
from RCL.model.models import NewSchedulesSpiderPortCollectScac
import logging as log
from RCL.utils.utils import EncrptUtils, DateTimeUtils


class MysqlPipeline(object):
    SCAC = 'RCLC'

    def process_item(self, item, spider):
        self._parse_and_save(item, spider)
        return item

    def _parse_and_save(self, item, spider):
        handlers = {
            PortItem: self._handle_portitem,
            PortGroupItem: self._handle_port_group_item,
            GroupItem: self._handle_group_item,
        }
        handlers[item.__class__](item, spider)

    def _get_indenty(self, item):
        key = ''
        for k, v in item.items():
            key = key + k + str(v)
        key = EncrptUtils.md5_str(key)
        return key

    def _covert_time(self, param):
        """
        格式化下时间
        :param param:
        :return:
        """
        return datetime.strptime(param, '%d/%m/%Y')

    def _covert_value(self, param):
        return round(float(param))

    def _handle_portitem(self, item, spider):
        log.info('收到portitem 开始处理')
        code_ = item['portCode']
        rows = CommonDao.check_repaet(NewSchedulesSpiderPortCollectScac, PORT_CODE=code_, SCAC=self.SCAC)
        if rows > 0:
            log.info('此portitem[%s]已存在', item)
            return
        npcs = NewSchedulesSpiderPortCollectScac()
        port_ = item['port']
        npcs.PORT = port_
        npcs.PORT_SCAC = port_
        npcs.PORT_CODE = code_
        npcs.BASE_CODE = code_
        npcs.SCAC = self.SCAC
        npcs.COUNTRYNAME = 'US'
        CommonDao.add_one_normal(npcs)
        log.info('portitem[%s] 入库成功', str(item))

    def _handle_port_group_item(self, item, spider):
        log.info('收到port_group_item 开始处理')
        _start_code = item['portPol']
        _start_name = item['portNamePol']
        _end_code = item['portPod']
        _end_name = item['portNamePod']
        rows = CommonDao.check_repaet(NewSchedulesSpiderPort,
                                      START_BASIC_CODE=_start_code,
                                      END_BASIC_CODE=_end_code, SCAC=self.SCAC)
        if rows > 0:
            log.info('此port_group_item[%s]已存在', item)
            return
        nssp = NewSchedulesSpiderPort()
        nssp.START_PORT = _start_name
        nssp.START_PORT_CODE = _start_code
        nssp.START_BASIC_CODE = _start_code
        nssp.SCAC = self.SCAC
        # 这里是已爬的
        nssp.STATE = 1
        nssp.END_PORT = _end_name
        nssp.END_PORT_CODE = _end_code
        nssp.END_BASIC_CODE = _end_code
        CommonDao.add_one_normal(nssp)
        log.info('此port_group_item[%s]入库成功', str(item))

    def _handle_group_item(self, item, spider):
        log.info('收到group_item 开始处理')
        try:
            # 此站点没有routeCode
            route_code = 'UNDEFINED'
            log.info('查询静态航线')
            rclc = self.SCAC
            res = CommonDao.get(NewSchedulesStatic, ROUTE_CODE=route_code, SCAC=('%s' % rclc))
            if res is None:
                mdd = '%s,%s,%s,%s' % (rclc, "NULL", "NULL", route_code)
                md5_key = EncrptUtils.md5_str(mdd)
                insert_static_sql = """
                           insert into  new_schedules_static(ID,SCAC,ROUTE_PARENT,ROUTE_NAME_EN,ROUTE_CODE,FLAG)
                           values ('%s','%s','%s','%s','%s','%s')
                           """ % (md5_key, rclc, None, None, route_code, 1)
                CommonDao.native_update(sql=insert_static_sql)
            else:
                md5_key = res.ID
            start_code = item['pol']
            end_code = item['pod']
            log.info('获取组合数据id')
            port_res = CommonDao.get(NewSchedulesSpiderPort, START_BASIC_CODE=start_code, END_BASIC_CODE=end_code,
                                     SCAC=rclc)
            insert_rel_sql_key = '%s,%s,%s' % (rclc, port_res.ID, md5_key)
            insert_rel_sql_key = EncrptUtils.md5_str(insert_rel_sql_key)
            log.info('写入静态航线和动态航线关联关系')
            insert_rel_sql = """
                       insert into new_schedules_static_p2p values('%s','%s','%s','%s') on duplicate key update id=values(ID)
                       """ % (insert_rel_sql_key, rclc, port_res.ID, md5_key)
            CommonDao.native_update(sql=insert_rel_sql)

            log.info('记录船名船次信息')
            transit_id = EncrptUtils.md5_str(str(item['TRANSIT_LIST']))
            now_time_str = DateTimeUtils.now().strftime('%Y-%m-%d %H:%M:%S')
            support_vessl_sql_key = '%s,%s,%s,%s' % (insert_rel_sql_key, item['VESSEL'], item['VOYAGE'], route_code)
            support_vessl_sql_key = EncrptUtils.md5_str(support_vessl_sql_key + transit_id)
            vessl_sql = """
                       insert into new_schedules_support_vessel(ID,RELATION_ID,VESSEL,VOYAGE,DYNAMIC_ROUTE_CODE,UPDATE_TIME)
                       values ('%s','%s','%s','%s','%s','%s') on  duplicate key update UPDATE_TIME=values(UPDATE_TIME)
                       """ % (support_vessl_sql_key, insert_rel_sql_key, item['VESSEL'], item['VOYAGE'],
                              route_code,
                              now_time_str)

            CommonDao.native_update(vessl_sql)
            log.info('录船名船次信息成功')

            log.info('写入动态数据')
            new_schedules_dynamic_key = self._get_indenty(item)
            nsd = NewSchedulesDynamic()
            nsd.ID = new_schedules_dynamic_key
            nsd.SCAC = rclc
            nsd.VESSEL_RELATION_ID = support_vessl_sql_key
            nsd.TRANSIT_ID = EncrptUtils.md5_str('')
            nsd.POD_TERMINAL = item['podName']
            nsd.POL_TERMINAL = item['polName']
            nsd.ETA = self._covert_time(item['ETA'])
            nsd.ETD = self._covert_time(item['ETD'])
            nsd.IS_TRANSIT = str(item['IS_TRANSIT'])
            nsd.TRANSIT_TIME = item['TRANSIT_TIME']
            CommonDao.add_one_normal(nsd)
            log.info('写入动态数据成功')

            for transit_info in item['TRANSIT_LIST']:
                try:
                    log.info('写入中转数据')
                    transit_key = '%s,%s,%s,%s' % (transit_id, transit_info['TRANSIT_PORT_EN'],
                                                   transit_info['TRANS_VESSEL'],
                                                   transit_info['TRANS_VOYAGE']
                                                   )
                    transit_key = EncrptUtils.md5_str(transit_key)
                    nddt = NewSchedulesDynamicTransit()
                    nddt.ID = transit_key
                    nddt.TRANSIT_ID = transit_id
                    nddt.TRANSIT_PORT_EN = transit_info['TRANSIT_PORT_EN']
                    nddt.TRANSIT_VESSEL = transit_info['TRANS_VESSEL']
                    nddt.TRANSIT_VOYAGE = transit_info['TRANS_VOYAGE']
                    CommonDao.add_one_normal(nddt)
                    log.info('写入中转数据成功')
                except Exception as e:
                    log.error("添加中转数据错误 item[%s]出错e[%s]", str(transit_info), e)
            if res is None or res.FLAG == '1':
                log.info('写入挂靠港口数据')
                nssd = NewSchedulesStaticDocking()
                nssd.STATIC_ID = md5_key
                nssd.PORT = item['podName']
                nssd.IS_POL = 0
                nssd.PORT_CODE = item['pod']
                nssd.ETD = item['ETD']
                nssd.ETA = item['ETA']
                nssd.TRANSIT_TIME = int(self._covert_value(item['TRANSIT_TIME']))
                nssd.IS_TRANSI = nsd.IS_TRANSIT
                CommonDao.add_one_normal(nssd)
                log.info('写入挂靠港口数据成功')

                nssd = NewSchedulesStaticDocking()
                nssd.STATIC_ID = md5_key
                nssd.PORT = item['polName']
                nssd.IS_POL = 1
                nssd.PORT_CODE = item['pol']
                nssd.ETD = item['ETD']
                nssd.ETA = item['ETA']
                nssd.TRANSIT_TIME = int(self._covert_value(item['TRANSIT_TIME']))
                nssd.IS_TRANSI = nsd.IS_TRANSIT
                CommonDao.add_one_normal(nssd)
                log.info('写入挂靠港口数据成功')
        except Exception as e:
            log.error("处理group_item[%s] 出错e[%s]", str(item), e)

# class RclPipeline(object):
#     def process_item(self, item, spider):
#         return item


# class PortMongoPipeline(object):
#     def __init__(self, mongo_uri, mongo_db):
#         self.mongo_uri = mongo_uri
#         self.mongo_db = mongo_db
#
#     @classmethod
#     def from_crawler(cls, crawler):  # 获取settings.py配置
#         return cls(
#             mongo_uri=crawler.settings.get('MONGO_URI'),
#             mongo_db=crawler.settings.get('MONGO_DB')
#         )
#
#     def open_spider(self, spider):
#         self.client = pymongo.MongoClient(self.mongo_uri)
#         self.db = self.client[self.mongo_db]
#
#     def process_item(self, item, spider):
#         name = item.__class__.__name__
#         self.db[name].insert(dict(item))
#         return item
#
#     def close_spider(self, spider):
#         self.client.close()

#
# class GroupMongoPipeline(object):
#     def __init__(self, mongo_uri, mongo_db):
#         self.mongo_uri = mongo_uri
#         self.mongo_db = mongo_db
#
#     @classmethod
#     def from_crawler(cls, crawler):  # 获取settings.py配置
#         return cls(
#             mongo_uri=crawler.settings.get('MONGO_URI'),
#             mongo_db=crawler.settings.get('MONGO_DB')
#         )
#
#     def open_spider(self, spider):
#         self.client = pymongo.MongoClient(self.mongo_uri)
#         self.db = self.client[self.mongo_db]
#
#     def process_item(self, item, spider):
#         name = item.__class__.__name__
#         self.db[name].insert(dict(item))
#         return item
#
#     def close_spider(self, spider):
#         self.client.close()

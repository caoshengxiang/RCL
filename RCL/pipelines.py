# -*- coding: utf-8 -*-


from datetime import datetime

import pymongo

from RCL.items import PortItem, PortGroupItem
from RCL.items import GroupItem
from RCL.model.dao import CommonDao
from RCL.model.models import NewSchedulesSpiderPort, NewSchedulesStatic, NewSchedulesDynamic, \
    NewSchedulesStaticDocking, NewSchedulesDynamicTransit
from RCL.model.models import NewSchedulesSpiderPortCollectScac
import logging as log
from RCL.utils.utils import EncrptUtils, DateTimeUtils


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):  # 获取settings.py配置
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        log.info('MongoPipeline')
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        name = item.__class__.__name__
        self.db[name].insert(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()


def boolean_none(text):
    return text if text and text != 'None' and text != 'null' and text != '' and text != '0000-00-00 00:00:00' else None


class MysqlPipeline(object):
    SCAC = 'RCLC'

    def open_spider(self, spider):
        log.info('MysqlPipeline')

    def process_item(self, item, spider):
        self._parse_and_save(item, spider)
        return item

    def _parse_and_save(self, item, spider):
        handlers = {
            PortItem: self._handle_portitem,
            PortGroupItem: self._handle_port_group_item,
            GroupItem: self._handle_group_item
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

    def _covert_time2weekday(self, param):
        return self._covert_time(param).weekday() + 1

    def _covert_value(self, param):
        return round(float(param))

    def _handle_portitem(self, item, spider):
        log.info('收到portitem 开始处理')
        code_ = item['portCode']
        rows = CommonDao.check_repaet(NewSchedulesSpiderPortCollectScac, PORT_CODE=code_, SCAC=self.SCAC, DEL_FLAG=0)
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
                                      DEL_FLAG=0,
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
            # ROUTE_CODE
            route_code = item.get('ROUTE_CODE', None)
            route_code = 'UNDEFINED'
            log.info('查询静态航线')
            rclc = self.SCAC
            res = CommonDao.get(NewSchedulesStatic, DEL_FLAG=0, ROUTE_CODE=route_code, SCAC=rclc)
            if res is None:
                mdd = '%s,%s,%s,%s' % (rclc, "NULL", "NULL", route_code)
                md5_key = EncrptUtils.md5_str(mdd)
                insert_static_sql = """
                           insert into  new_schedules_static(ID,SCAC,ROUTE_CODE,FLAG)
                           values ('%s','%s','%s','%s')
                           """ % (md5_key, rclc, route_code, 1)
                CommonDao.native_update(sql=insert_static_sql)
            else:
                md5_key = res.ID
            start_code = item['pol']
            end_code = item['pod']
            log.info('获取组合数据id')
            port_res = CommonDao.get(NewSchedulesSpiderPort, DEL_FLAG=0, START_BASIC_CODE=start_code,
                                     END_BASIC_CODE=end_code,
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
            from RCL.model.basic import db_session
            log.info('写入动态数据')
            new_schedules_dynamic_key = self._get_indenty(item)
            nsd = NewSchedulesDynamic()
            dynamic_res = CommonDao.get(NewSchedulesDynamic, ID=new_schedules_dynamic_key, DEL_FLAG=0)
            if dynamic_res is None:
                nsd.ID = new_schedules_dynamic_key
                nsd.SCAC = rclc
                nsd.VESSEL_RELATION_ID = support_vessl_sql_key
                nsd.TRANSIT_ID = transit_id
                # 没有码头数据 空着
                # nsd.POD_TERMINAL = item['podName']
                # nsd.POL_TERMINAL = item['polName']
                nsd.ETA = self._covert_time(item['ETA'])
                nsd.ETD = self._covert_time(item['ETD'])
                nsd.IS_TRANSIT = str(item['IS_TRANSIT'])
                nsd.TRANSIT_TIME = item['TRANSIT_TIME']
                CommonDao.add_one_normal(nsd)
                log.info('写入动态数据成功')
            else:
                dynamic_res.UPDATE_TIME = DateTimeUtils.now()
                dynamic_res.VERSION_NUMBER = dynamic_res.VERSION_NUMBER + 1
                db_session.commit()
                log.info('重复 dynamic_res 更新成功')

            for index, transit_info in enumerate(item['TRANSIT_LIST'], start=1):
                try:
                    log.info('写入中转数据')
                    transit_key = '%s,%s,%s,%s' % (transit_id, transit_info['TRANSIT_PORT_EN'],
                                                   transit_info['TRANS_VESSEL'],
                                                   transit_info['TRANS_VOYAGE']
                                                   )
                    transit_key = EncrptUtils.md5_str(transit_key)

                    dynamic_trainst = CommonDao.get(NewSchedulesDynamicTransit, ID=transit_key, DEL_FLAG=0)
                    if dynamic_trainst:
                        dynamic_trainst.UPDATE_TIME = DateTimeUtils.now()
                        dynamic_trainst.TRANSIT_SORT = index
                        db_session.commit()
                        log.info('重复 dynamic_trainst 更新成功')
                        continue

                    nddt = NewSchedulesDynamicTransit()
                    nddt.ID = transit_key
                    nddt.TRANSIT_SORT = index
                    nddt.TRANSIT_ID = transit_id
                    nddt.TRANSIT_PORT_EN = transit_info['TRANSIT_PORT_EN']
                    nddt.TRANSIT_VESSEL = transit_info['TRANS_VESSEL']
                    nddt.TRANSIT_VOYAGE = transit_info['TRANS_VOYAGE']
                    CommonDao.add_one_normal(nddt)
                    log.info('写入中转数据成功')
                except Exception as e:
                    log.error("添加中转数据错误 item[%s]出错e[%s]", str(transit_info), e)
            log.info('写入挂靠港口数据')
            docking_res_1 = CommonDao.check_repaet(NewSchedulesStaticDocking,
                                                   STATIC_ID=md5_key,
                                                   DEL_FLAG=0,
                                                   PORT_CODE=item['pod'])
            if docking_res_1 <= 0 and int(item['IS_TRANSIT']) == 0:
                nssd = NewSchedulesStaticDocking()
                nssd.STATIC_ID = md5_key
                nssd.PORT = item['podName']
                nssd.IS_POL = 0
                nssd.PORT_CODE = item['pod']
                nssd.ETD = self._covert_time2weekday(item['ETD'])
                nssd.ETA = self._covert_time2weekday(item['ETA'])
                nssd.FLAG = 1
                nssd.TRANSIT_TIME = int(self._covert_value(item['TRANSIT_TIME']))
                nssd.IS_TRANSI = item['IS_TRANSIT']
                CommonDao.add_one_normal(nssd)
                log.info('写入挂靠港口数据成功')

            docking_res_2 = CommonDao.check_repaet(NewSchedulesStaticDocking,
                                                   STATIC_ID=md5_key,
                                                   PORT_CODE=item['pol'])
            if docking_res_2 <= 0 and int(item['IS_TRANSIT']) == 0:
                nssd = NewSchedulesStaticDocking()
                nssd.STATIC_ID = md5_key
                nssd.PORT = item['polName']
                nssd.IS_POL = 1
                nssd.FLAG = 1
                nssd.PORT_CODE = item['pol']
                nssd.ETD = self._covert_time2weekday(item['ETD'])
                nssd.ETA = self._covert_time2weekday(item['ETA'])
                nssd.TRANSIT_TIME = int(self._covert_value(item['TRANSIT_TIME']))
                nssd.IS_TRANSI = item['IS_TRANSIT']
                CommonDao.add_one_normal(nssd)
                log.info('写入挂靠港口数据成功')
        except Exception as e:
            log.error("处理group_item[%s] 出错e[%s]", str(item), e)

    def _handle_group_item_v2(self, item, spider):
        log.info('收到group_item 开始处理')
        try:
            log.info('查询静态航线')
            route_code = item.get('ROUTE_CODE', None)
            scac = spider.name.upper()
            item['ROUTE_CODE'] = self.getFirstRangeRouteCode(item, 0)
            ssql = """
                    SELECT ID,FLAG FROM new_schedules_static
                    WHERE FIND_IN_SET( REPLACE(TRIM('%s'),' ',''), CONCAT_WS(',',REPLACE(TRIM(ROUTE_CODE),' ',''),
                    REPLACE(TRIM(MY_ROUTE_CODE),' ',''),REPLACE(TRIM(ROUTE_NAME_EN),' ',''))) AND SCAC = '%s'
                    ORDER BY CREATE_TIME ASC LIMIT 1
                """
            result = CommonDao.native_query(ssql % (item['ROUTE_CODE'], scac))
            relation_id = None
            main_id = ''
            if result and result.ID:
                # 查到对应关系 直接主表id赋值
                main_id = result.ID
            else:
                # 如果匹配不上静态航线code
                # 生成主键
                mdd = '%s,%s,%s,%s' % (scac.upper(), "NULL", "NULL", item['ROUTE_CODE'])
                EncrptUtils.md5_str(mdd)
                # 根据动态生成静态航线
                insert_main_sql = """
                           INSERT INTO new_schedules_static (
                           ID,SCAC,ROUTE_PARENT, ROUTE_NAME_EN,ROUTE_CODE,FLAG)
                           SELECT '%s','%s','%s','%s','%s','%s' FROM DUAL WHERE NOT EXISTS
                           ( SELECT * FROM new_schedules_static s
                           WHERE s.SCAC='%s' and s.ROUTE_PARENT IS NULL and s.ROUTE_NAME_EN IS NULL and s.ROUTE_CODE='%s')
                           """
                # 插入静态船期主表
                CommonDao.native_update(insert_main_sql % ((main_id, scac.upper(), None, None, item['ROUTE_CODE'], 1,
                                                            scac.upper(), item['ROUTE_CODE'])))
            start_code = item['pol']
            end_code = item['pod']
            log.info('获取组合数据id')
            port_res = CommonDao.get(NewSchedulesSpiderPort, DEL_FLAG=0, START_BASIC_CODE=start_code,
                                     END_BASIC_CODE=end_code,
                                     SCAC=scac)
            insert_rel_sql_key = '%s,%s,%s' % (scac, port_res.ID, main_id)
            insert_rel_sql_key = EncrptUtils.md5_str(insert_rel_sql_key)
            relation_id = insert_rel_sql_key
            log.info('写入静态航线和动态航线关联关系')
            insert_rel_sql = """
                       insert into new_schedules_static_p2p values('%s','%s','%s','%s') on duplicate key update id=values(ID)
                       """ % (insert_rel_sql_key, scac.upper(), port_res.ID, main_id)
            CommonDao.native_update(sql=insert_rel_sql)

            log.info('记录船名船次信息')
            now_time_str = DateTimeUtils.now().strftime('%Y-%m-%d %H:%M:%S')
            support_vessl_sql_key = '%s,%s,%s,%s' % (insert_rel_sql_key, item['VESSEL'], item['VOYAGE'], route_code)
            support_vessl_sql_key = EncrptUtils.md5_str(support_vessl_sql_key)
            vessl_sql = """
                       insert into new_schedules_support_vessel(ID,RELATION_ID,VESSEL,VOYAGE,DYNAMIC_ROUTE_CODE,UPDATE_TIME)
                       values ('%s','%s','%s','%s','%s','%s') on  duplicate key update UPDATE_TIME=values(UPDATE_TIME)
                       """ % (support_vessl_sql_key, insert_rel_sql_key, item['VESSEL'], item['VOYAGE'],
                              route_code,
                              now_time_str)

            CommonDao.native_update(vessl_sql)

            log.info('录船名船次信息成功')
            from RCL.model.basic import db_session
            # transit_id = EncrptUtils.md5_str(str(item['TRANSIT_LIST']))

            transitIdList = []
            for transitInfo in item['TRANSIT_LIST']:
                transitIdList.append({
                    "TRANSIT_ROUTE_CODE": boolean_none(transitInfo['TRANSIT_ROUTE_CODE']),
                    "TRANSIT_PORT_EN": boolean_none(transitInfo['TRANSIT_PORT_EN']),
                    "TRANSIT_PORT_CODE": boolean_none(transitInfo['TRANSIT_PORT_CODE']),
                    "TRANSIT_VESSEL": boolean_none(transitInfo['TRANSIT_VESSEL']),
                })

                # 生成中转关联id
            transit_id = EncrptUtils.md5_str(str(transitIdList) + support_vessl_sql_key + main_id)
            log.info('写入动态数据')
            # new_schedules_dynamic_key = self._get_indenty(item)
            mdd = '%s,%s,%s,%s,%s' % \
                  (scac.upper(), support_vessl_sql_key,
                   self._covert_time(item['ETD']) if boolean_none(item['ETD']) else None,
                   self._covert_time(item['ETA']) if boolean_none(item['ETA']) else None,
                   item['IS_TRANSIT'] if item['IS_TRANSIT'] and item['IS_TRANSIT'] != 'None' else 0)
            new_schedules_dynamic_key = EncrptUtils.md5_str(mdd)
            nsd = NewSchedulesDynamic()
            dynamic_res = CommonDao.get(NewSchedulesDynamic, ID=new_schedules_dynamic_key, DEL_FLAG=0)
            if dynamic_res is None:
                nsd.ID = new_schedules_dynamic_key
                nsd.SCAC = scac
                nsd.VESSEL_RELATION_ID = support_vessl_sql_key
                nsd.TRANSIT_ID = transit_id
                nsd.POD_TERMINAL = item.get('podName') or ''
                nsd.POL_TERMINAL = item.get('polName') or ''
                nsd.ETA = self._covert_time(item['ETA'])
                nsd.ETD = self._covert_time(item['ETD'])
                nsd.IS_TRANSIT = str(item['IS_TRANSIT'])
                nsd.TRANSIT_TIME = item['TRANSIT_TIME']
                CommonDao.add_one_normal(nsd)
                log.info('写入动态数据成功')
            else:
                dynamic_res.UPDATE_TIME = DateTimeUtils.now()
                dynamic_res.VERSION_NUMBER = dynamic_res.VERSION_NUMBER + 1
                dynamic_res.POD_TERMINAL = item.get('podName') or ''
                dynamic_res.POL_TERMINAL = item.get('polName') or ''
                dynamic_res.ETA = self._covert_time(item['ETA'])
                dynamic_res.ETD = self._covert_time(item['ETD'])
                dynamic_res.IS_TRANSIT = str(item['IS_TRANSIT'])
                dynamic_res.TRANSIT_TIME = item['TRANSIT_TIME']
                db_session.commit()
                log.info('重复 dynamic_res 更新成功')

            for index, transit_info in enumerate(item['TRANSIT_LIST'], start=1):
                try:
                    log.info('写入中转数据')
                    transit_key = '%s,%s,%s,%s' % (transit_id, transit_info['TRANSIT_PORT_EN'],
                                                   transit_info['TRANS_VESSEL'],
                                                   transit_info['TRANS_VOYAGE'],
                                                   )
                    # todo
                    # transit_key = "%s,%s,%s,%s" % (transit_id,
                    #                        boolean_none(transit_info['TRANSIT_PORT_EN']),
                    #                        boolean_none(transit_info['TRANSIT_PORT_CODE']),
                    #                        boolean_none(transit_info['TRANSIT_ROUTE_CODE']))
                    transit_key = EncrptUtils.md5_str(transit_key)

                    dynamic_trainst = CommonDao.get(NewSchedulesDynamicTransit, ID=transit_key, DEL_FLAG=0)
                    if dynamic_trainst:
                        dynamic_trainst.UPDATE_TIME = DateTimeUtils.now()
                        dynamic_trainst.TRANSIT_SORT = index
                        dynamic_trainst.TRANSIT_VOYAGE = transit_info['TRANS_VOYAGE']
                        dynamic_trainst.TRANSIT_VESSEL = transit_info['TRANS_VESSEL']
                        db_session.commit()
                        log.info('重复 dynamic_trainst 更新成功')
                        continue

                    nddt = NewSchedulesDynamicTransit()
                    nddt.ID = transit_key
                    nddt.TRANSIT_SORT = index
                    nddt.TRANSIT_ID = transit_id
                    nddt.TRANSIT_PORT_EN = transit_info['TRANSIT_PORT_EN']
                    nddt.TRANSIT_VESSEL = transit_info['TRANS_VESSEL']
                    nddt.TRANSIT_VOYAGE = transit_info['TRANS_VOYAGE']
                    CommonDao.add_one_normal(nddt)
                    log.info('写入中转数据成功')
                except Exception as e:
                    log.error("添加中转数据错误 item[%s]出错e[%s]", str(transit_info), e)
            log.info('写入挂靠港口数据')
            docking_res_1 = CommonDao.check_repaet(NewSchedulesStaticDocking,
                                                   STATIC_ID=main_id,
                                                   DEL_FLAG=0,
                                                   PORT_CODE=item['pod'])
            if docking_res_1 <= 0 and int(item['IS_TRANSIT']) == 0:
                nssd = NewSchedulesStaticDocking()
                nssd.STATIC_ID = main_id
                nssd.PORT = item['podName']
                nssd.IS_POL = 0
                nssd.PORT_CODE = item['pod']
                nssd.ETD = self._covert_time2weekday(item['ETD'])
                nssd.ETA = self._covert_time2weekday(item['ETA'])
                nssd.FLAG = 1
                nssd.TRANSIT_TIME = int(self._covert_value(item['TRANSIT_TIME']))
                nssd.IS_TRANSI = item['IS_TRANSIT']
                CommonDao.add_one_normal(nssd)
                log.info('写入挂靠港口数据成功')

            docking_res_2 = CommonDao.check_repaet(NewSchedulesStaticDocking,
                                                   STATIC_ID=main_id,
                                                   PORT_CODE=item['pol'])
            if docking_res_2 <= 0 and int(item['IS_TRANSIT']) == 0:
                nssd = NewSchedulesStaticDocking()
                nssd.STATIC_ID = main_id
                nssd.PORT = item['polName']
                nssd.IS_POL = 1
                nssd.FLAG = 1
                nssd.PORT_CODE = item['pol']
                nssd.ETD = self._covert_time2weekday(item['ETD'])
                nssd.ETA = self._covert_time2weekday(item['ETA'])
                nssd.TRANSIT_TIME = int(self._covert_value(item['TRANSIT_TIME']))
                nssd.IS_TRANSI = item['IS_TRANSIT']
                CommonDao.add_one_normal(nssd)
                log.info('写入挂靠港口数据成功')
        except Exception as e:
            log.error("处理group_item[%s] 出错e[%s]", str(item), e)

    def getFirstRangeRouteCode(self, schedule, who):
        littleShip = [
            "WATER",
            "TRACE",
            "FEEDER",
            "BARGE",
            "FEEDER SERVICE FAR EAST",
            "FEEDER SERVICE FESEA",
            "RAIL",
            "UNDEFINED",
            "FEEDER VESSEL"
        ]
        routeCode = ""
        # 两种条件判断
        # 1，航线code
        # 2，船名航次
        # 航线code、船名航次是否有效，不为空，不为空串，不属于内支线，陆运等
        # 如果航线code不为空或者船名航次有效
        list = schedule['TRANSIT_LIST']
        if who == 0:
            if boolean_none(schedule['routeCode']) and boolean_none(schedule['routeCode']) not in littleShip:
                routeCode = schedule['routeCode']
            elif boolean_none(list[0]['TRANSIT_ROUTE_CODE']) and boolean_none(
                    list[0]['TRANSIT_ROUTE_CODE']) not in littleShip:
                routeCode = list[0]['TRANSIT_ROUTE_CODE']
            elif boolean_none(list[1]['TRANSIT_ROUTE_CODE']) and boolean_none(
                    list[1]['TRANSIT_ROUTE_CODE']) not in littleShip:
                routeCode = list[1]['TRANSIT_ROUTE_CODE']
            elif boolean_none(list[2]['TRANSIT_ROUTE_CODE']) and boolean_none(
                    list[2]['TRANSIT_ROUTE_CODE']) not in littleShip:
                routeCode = list[2]['TRANSIT_ROUTE_CODE']
            else:
                routeCode = "UNDEFINED"
        elif who == 2:
            if boolean_none(schedule['ROUTE_CODE']) and boolean_none(schedule['ROUTE_CODE']) not in littleShip:
                routeCode = schedule['ROUTE_CODE']
            elif boolean_none(list[0]['TRANSIT_ROUTE_CODE']) and boolean_none(
                    list[0]['TRANSIT_ROUTE_CODE']) not in littleShip:
                routeCode = list[0]['TRANSIT_ROUTE_CODE']
            elif boolean_none(list[1]['TRANSIT_ROUTE_CODE']) and boolean_none(
                    list[1]['TRANSIT_ROUTE_CODE']) not in littleShip:
                routeCode = list[1]['TRANSIT_ROUTE_CODE']
            elif boolean_none(list[2]['TRANSIT_ROUTE_CODE']) and boolean_none(
                    list[2]['TRANSIT_ROUTE_CODE']) not in littleShip:
                routeCode = list[2]['TRANSIT_ROUTE_CODE']
            else:
                routeCode = "UNDEFINED"
        else:
            if boolean_none(schedule['ROUTE_CODE']) and boolean_none(schedule['ROUTE_CODE']) not in littleShip:
                routeCode = schedule['ROUTE_CODE']
            elif boolean_none(list[0]['TRANSIT_ROUTE_CODE']) and boolean_none(
                    list[0]['TRANSIT_ROUTE_CODE']) not in littleShip:
                routeCode = list[0]['TRANSIT_ROUTE_CODE']
            elif boolean_none(list[1]['TRANSIT_ROUTE_CODE']) and boolean_none(
                    list[1]['TRANSIT_ROUTE_CODE']) not in littleShip:
                routeCode = list[1]['TRANSIT_ROUTE_CODE']
            elif boolean_none(list[2]['TRANSIT_ROUTE_CODE']) and boolean_none(
                    list[2]['TRANSIT_ROUTE_CODE']) not in littleShip:
                routeCode = list[2]['TRANSIT_ROUTE_CODE']
            else:
                routeCode = "UNDEFINED"
        return routeCode

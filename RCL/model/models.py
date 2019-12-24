# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      models
# Author:    liangbaikai
# Date:      2019/11/13
# Desc:      there is a python file description
# ------------------------------------------------------------------

from sqlalchemy import CHAR, Column, ForeignKey, Index, String, TIMESTAMP, text, DateTime
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.orm import relationship

from RCL.model.basic import Base


class NewCity(Base):
    __tablename__ = 'new_city'

    ID = Column(INTEGER(11), primary_key=True)
    CITY_EN = Column(String(255), index=True)
    CITY_CN = Column(String(255))
    COUNTRY_ID = Column(INTEGER(11), comment='关联new_country表')
    COUNTRY_CODE = Column(String(8), comment='国家2字码')
    STATE = Column(TINYINT(3), server_default=text("'0'"))
    CREATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class NewCountry(Base):
    __tablename__ = 'new_country'

    ID = Column(INTEGER(11), primary_key=True)
    COUNTRY_EN = Column(String(255))
    COUNTRY_CN = Column(String(255))
    COUNTRY_CODE = Column(String(255), index=True)
    STATE = Column(TINYINT(3), server_default=text("'0'"))
    CREATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class NewPort(Base):
    __tablename__ = 'new_port'

    ID = Column(INTEGER(11), primary_key=True)
    PORT_EN = Column(String(255))
    PORT_CN = Column(String(255))
    PORT_CODE = Column(String(255), index=True)
    TERMINAL = Column(String(255), comment='码头')
    ROUTE_ID = Column(INTEGER(11))
    ROUTE_CN = Column(String(200), comment='new_route的id')
    COUNTRY_ID = Column(INTEGER(11), comment='new_country的id')
    CITY_ID = Column(INTEGER(11), comment='new_city的id')
    STATE = Column(TINYINT(3), server_default=text("'0'"))
    CREATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    CANTONAL = Column(String(200), comment='州')
    RANKING = Column(INTEGER(1), comment='不知道干嘛的')


class NewRoute(Base):
    __tablename__ = 'new_route'

    ID = Column(INTEGER(11), primary_key=True)
    ROUTE_EN = Column(String(255))
    ROUTE_CN = Column(String(255))
    STATE = Column(TINYINT(2))
    CREATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class NewScac(Base):
    __tablename__ = 'new_scac'

    ID = Column(INTEGER(11), primary_key=True)
    SCAC = Column(String(5))
    CARRIER = Column(String(50))
    CARRIER_CN = Column(String(255))
    SHIP_EN = Column(String(255))
    STATE = Column(TINYINT(2), server_default=text("'0'"))
    COUNT = Column(INTEGER(11))
    CREATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    STATIC_URL = Column(String(255))
    P2P_URL = Column(String(255))
    STATIC_FLAG = Column(INTEGER(2), comment='0人工,1爬取')


class NewScacPort(Base):
    __tablename__ = 'new_scac_port'

    ID = Column(INTEGER(11), primary_key=True)
    SCAC = Column(String(255))
    PORT = Column(String(255))
    SCAC_CODE = Column(String(255))
    BASIC_CODE = Column(String(255))
    STATE = Column(TINYINT(4), server_default=text("'0'"))
    CREATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class NewSchedulesDynamicTransit(Base):
    __tablename__ = 'new_schedules_dynamic_transit'

    ID = Column(CHAR(40), primary_key=True, index=True, comment='UUID')
    TRANSIT_PORT_EN = Column(String(200), comment='中转港口')
    TRANSIT_PORT_CODE = Column(String(200), comment='中转港口五子码')
    TRANSIT_ROUTE_CODE = Column(String(255), comment='中转后的航线')
    TRANSIT_VESSEL = Column(String(200), comment='中转后的船名')
    TRANSIT_VOYAGE = Column(String(200), comment='中转后的航次')
    CREATE_TIME = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    UPDATE_TIME = Column(TIMESTAMP, nullable=False,
                         server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='修改时间')
    DEL_FLAG = Column(INTEGER(2), server_default=text("'0'"),
                      comment='删除标识0不删除,1删除 (当为2 时候 ,作为下次更新数据的删除标识,删除 这条数据及以前的所有数据)')
    VERSION_NUMBER = Column(INTEGER(11), server_default=text("'0'"), comment='更新的版本，默认0')
    TRANSIT_SORT = Column(INTEGER(1), server_default=text("'1'"))
    TRANSIT_ID = Column(CHAR(40), index=True)



class NewSchedulesSpiderPort(Base):
    __tablename__ = 'new_schedules_spider_port'

    ID = Column(INTEGER(11), primary_key=True)
    START_PORT_ID = Column(String(200), comment='saf公司准备')
    START_PORT = Column(String(255), comment='起始港')
    START_PORT_CODE = Column(String(255))
    START_PORT_COUNTRY = Column(String(255), comment='SAF公司准备')
    START_BASIC_CODE = Column(String(100), index=True)
    START_FOR_SEARCH = Column(String(255), index=True)
    START_PORT_EN = Column(String(255), comment='起始港简称')
    END_PORT_ID = Column(String(200))
    END_PORT = Column(String(255), comment='目的港')
    END_PORT_CODE = Column(String(255))
    END_PORT_COUNTRY = Column(String(255))
    END_BASIC_CODE = Column(String(100), index=True)
    END_FOR_SEARCH = Column(String(255), index=True)
    END_PORT_EN = Column(String(255), comment='目的港简称')
    SCAC = Column(String(24), index=True, comment='船公司')
    STATE = Column(INTEGER(2), server_default=text("'0'"), comment='爬取标识0待爬取1已爬取')
    CREATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    DEL_FLAG = Column(INTEGER(2), server_default=text("'0'"), comment='删除标识0未删除1删除')
    ROUTE_CODE = Column(String(100), comment='航线code')
    UPDATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    PAGE_NUM = Column(INTEGER(11))


class NewSchedulesSpiderPortCollectScac(Base):
    __tablename__ = 'new_schedules_spider_port_collect_scac'
    __table_args__ = (
        Index('BASE_CODE', 'BASE_CODE', 'SCAC'),
    )

    ID = Column(INTEGER(11), primary_key=True)
    PORT = Column(String(255), comment='港口')
    PORT_SCAC = Column(String(255), comment='港口在每家船公司的叫法')
    PORT_CODE = Column(String(25), comment='港口五子码')
    BASE_CODE = Column(String(25), comment='基础库五子码')
    SCAC = Column(String(25), comment='船公司4字码')
    ROUTE_CODE = Column(String(255), comment='航线')
    DIRECTION = Column(String(30), comment='direction 船行驶方向')
    COUNTRYNAME = Column(String(255), comment='国家')
    STATE = Column(TINYINT(2), server_default=text("'2'"), comment='港口状态0已使用1未使用2待审核')
    FLAG = Column(String(255), comment='备用字段')
    DEL_FLAG = Column(TINYINT(2), server_default=text("'0'"), comment='删除标识0不删除1删除')
    CREATE_TIME = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATE_TIME = Column(TIMESTAMP, nullable=False,
                         server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    CHECK_OVER = Column(TINYINT(1), server_default=text("'0'"), comment='0未审查,1审查完成(检查生成港口组合需要的字段是否齐全)')


class NewSchedulesStatic(Base):
    __tablename__ = 'new_schedules_static'

    ID = Column(CHAR(40), primary_key=True, index=True)
    SCAC = Column(String(25), index=True, comment='船公司4字码')
    ROUTE_PARENT = Column(String(255), comment='服务父航线名称')
    ROUTE_NAME_EN = Column(String(255), comment='服务子航线名称')
    ROUTE_CODE = Column(String(250), index=True, comment='航线code')
    FLAG = Column(String(255), comment='类型，0：系统；1：动态生成；2：人工；3：手动添加')
    DEL_FLAG = Column(INTEGER(2), server_default=text("'0'"), comment='删除标识0不删除1删除')
    CREATE_TIME = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    UPDATE_TIME = Column(TIMESTAMP, nullable=False,
                         server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')


class NewSchedulesStaticDocking(Base):
    __tablename__ = 'new_schedules_static_docking'
    __table_args__ = (
        Index('ID', 'ID', 'STATIC_ID', 'PORT', 'PORT_CODE'),
    )

    ID = Column(INTEGER(11), primary_key=True)
    STATIC_ID = Column(ForeignKey('new_schedules_static.ID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                       index=True, comment='静态id')
    PORT_NUMBER = Column(INTEGER(11), comment='挂靠港顺序')
    PORT = Column(String(255), index=True, comment='港口')
    PORT_CODE = Column(String(25), index=True, comment='港口五子码')
    IS_POL = Column(INTEGER(1), comment='0pol,1pod')
    TERMINAL = Column(String(255), comment='码头')
    ETA = Column(String(100), comment='到港星期3字码')
    ETD = Column(String(100), comment='离港星期3字码')
    TRANSIT_TIME = Column(INTEGER(11), server_default=text("'0'"), comment='渡越时间')
    DIRECTION = Column(String(30), comment='direction 船行驶方向')
    IS_TRANSIT = Column(INTEGER(1), server_default=text("'0'"), comment='是否中转(0直达,1中转)')
    TRANS_TYPE = Column(INTEGER(1), server_default=text("'1'"), comment='运输类型0铁路, 1海运')
    FLAG = Column(String(255), comment='备用字段')
    DEL_FLAG = Column(INTEGER(2), server_default=text("'0'"), comment='删除标识0不删除1删除')
    CREATE_TIME = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    UPDATE_TIME = Column(TIMESTAMP, nullable=False,
                         server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    TERMINAL_ID = Column(INTEGER(11))

    new_schedules_static = relationship('NewSchedulesStatic')


class NewSchedulesStaticP2p(Base):
    __tablename__ = 'new_schedules_static_p2p'
    __table_args__ = (
        Index('ID', 'ID', 'P2P_ID', 'STATIC_ID'),
    )

    ID = Column(CHAR(40), primary_key=True, index=True)
    SCAC = Column(String(4), nullable=False, comment='船公司四字码')
    P2P_ID = Column(ForeignKey('new_schedules_spider_port.ID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                    index=True, comment='1800港口组合表id(new_schedules_spider_port的主键)')
    STATIC_ID = Column(ForeignKey('new_schedules_static.ID', ondelete='CASCADE', onupdate='CASCADE'), index=True,
                       comment='静态表ID(new_schedules_static的主键)')

    new_schedules_spider_port = relationship('NewSchedulesSpiderPort')
    new_schedules_static = relationship('NewSchedulesStatic')


class NewSchedulesSupportVessel(Base):
    __tablename__ = 'new_schedules_support_vessel'

    ID = Column(CHAR(40), primary_key=True, comment='UUID')
    RELATION_ID = Column(ForeignKey('new_schedules_static_p2p.ID', ondelete='CASCADE', onupdate='CASCADE'), index=True,
                         comment='关联表id(new_schedules_static_p2p的主键)')
    VESSEL = Column(String(100), index=True, comment='船名')
    VOYAGE = Column(String(100), index=True, comment='航次')
    CREATE_TIME = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    UPDATE_TIME = Column(TIMESTAMP, nullable=False,
                         server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='修改时间')
    DEL_FLAG = Column(INTEGER(2), index=True, server_default=text("'0'"),
                      comment='删除标识0不删除,1删除 (当为2 时候 ,作为下次更新数据的删除标识,删除 这条数据及以前的所有数据)')
    NO_SHOW = Column(INTEGER(2), index=True, server_default=text("'0'"), comment='是否给接口显示,删除的数据不显示')
    DYNAMIC_ROUTE_CODE = Column(String(200), comment='动态航线code')

    new_schedules_static_p2p = relationship('NewSchedulesStaticP2p')


class NewSchedulesDynamic(Base):
    __tablename__ = 'new_schedules_dynamic'
    __table_args__ = (
        Index('ID', 'ID', 'SCAC', 'VESSEL_RELATION_ID'),
        Index('SCAC_2', 'SCAC', 'VERSION_NUMBER'),
        Index('SCAC_3', 'SCAC', 'VERSION_NUMBER'),
        Index('VESSEL_RELATION_ID', 'VESSEL_RELATION_ID', 'VERSION_NUMBER')
    )

    ID = Column(CHAR(40), primary_key=True, comment='UUID')
    SCAC = Column(String(50), nullable=False, index=True, comment='船公司四字码')
    VESSEL_RELATION_ID = Column(ForeignKey('new_schedules_support_vessel.ID', ondelete='CASCADE', onupdate='CASCADE'),
                                nullable=False, index=True, comment='支持的船表id(new_schedules_support_vessel的id)')
    TRANSIT_ID = Column(CHAR(40), index=True, comment='中转信息id')
    POL_TERMINAL = Column(String(255), comment='起始港Terminal码头')
    POD_TERMINAL = Column(String(255), comment='目的港码头')
    ETD = Column(TIMESTAMP, comment='预计离港时间')
    ETA = Column(TIMESTAMP, comment='预计到港时间')
    ATA = Column(TIMESTAMP, comment='实际抵港时间')
    ATD = Column(TIMESTAMP, comment='实际离港时间')
    TRANSIT_TIME = Column(String(5), comment='运输时间')
    IS_TRANSIT = Column(TINYINT(1), index=True, server_default=text("'0'"), comment='是否中转(0直达,1中转)')
    TRANS_TYPE = Column(String(1), comment='运输类型0海运1铁运')
    CONTAINER_CUTOFF = Column(TIMESTAMP, comment='截重时间')
    VGM_CUTOFF = Column(TIMESTAMP, comment='VGM截止时间')
    MANIFEST_CUTOFF = Column(TIMESTAMP, comment='R24Cutoff')
    SI_CUTOFF = Column(TIMESTAMP, comment='SICutoff')
    CY_CUTOFF = Column(TIMESTAMP, comment='放行条截止时间(custReleaseDt)')
    BERTHING_TIME = Column(TIMESTAMP, comment='Berthing 停泊时间')
    BOOKING_CUTOFF = Column(TIMESTAMP, comment='截订舱时间')
    DIRECTION = Column(String(25), comment='direction(E 东行, W西行)')
    CREATE_TIME = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    UPDATE_TIME = Column(TIMESTAMP, nullable=False,
                         server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='修改时间')
    DEL_FLAG = Column(INTEGER(2), server_default=text("'0'"),
                      comment='删除标识0不删除,1删除 (当为2 时候 ,作为下次更新数据的删除标识,删除 这条数据及以前的所有数据)')
    VERSION_NUMBER = Column(INTEGER(11), index=True, server_default=text("'0'"), comment='更新的版本，默认0')

    new_schedules_support_vessel = relationship('NewSchedulesSupportVessel')


class NewSchedulesTaskVersion(Base):
    __tablename__ = 'new_schedules_task_version'

    ID = Column(INTEGER(11), primary_key=True)
    SCAC = Column(String(4), nullable=False, comment='船公司四字码')
    VERSION = Column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='版本号')
    START_TIME = Column(DateTime, nullable=False, comment='开始更新时间')
    END_TIME = Column(DateTime, comment='结束更新时间')

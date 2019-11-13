# -*-coding:utf-8 -*-

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


def get_engine():
    args = {
        'db_type': 'mysql',
        'user': 'a111222',
        'password': '!@#123QWEqwe',
        'host': 'rm-bp19hl3624ib44ai5o.mysql.rds.aliyuncs.com',
        'port': 3306,
        'db_name': 'sp_out',
    }
    connect_str = "{}+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4".format(args['db_type'], args['user'], args['password'],
                                                                       args['host'], args['port'], args['db_name'])
    engine = create_engine(connect_str, encoding='utf-8', pool_size=200, max_overflow=-1, pool_recycle=3600)
    return engine


eng = get_engine()
Base = declarative_base()
session_factory = sessionmaker(bind=eng)
Session = scoped_session(session_factory)
db_session = Session()
metadata = MetaData(get_engine())
__all__ = ['eng', 'Base', 'db_session', 'metadata', 'Session']

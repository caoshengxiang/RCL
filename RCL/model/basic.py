# -*-coding:utf-8 -*-

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from RCL.settings import DB_TYPE, USER, HOST, DB_NAME, PASSWORD, PORT


def get_engine():
    args = {
        'db_type': DB_TYPE[0],
        'user': USER[0],
        'password': PASSWORD[0],
        'host': HOST[0],
        'port': PORT[0],
        'db_name': DB_NAME[0],
    }
    connect_str = "{}+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4".format(args['db_type'], args['user'], args['password'],
                                                                       args['host'], args['port'], args['db_name'])
    engine = create_engine(connect_str, encoding='utf-8', pool_size=500, max_overflow=-1, pool_recycle=3600)
    return engine


eng = get_engine()
Base = declarative_base()
session_factory = sessionmaker(bind=eng)
Session = scoped_session(session_factory)
db_session = Session()
metadata = MetaData(get_engine())

__all__ = ['eng', 'Base', 'db_session', 'metadata', 'Session']

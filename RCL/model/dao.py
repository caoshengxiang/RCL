# -*- coding: utf-8 -*-
import re
from numbers import Number

from sqlalchemy import func, text

from RCL.model.basic import db_session


class CommonDao:

    @classmethod
    def add_one(cls, session, data):
        try:
            session.add(data)
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()

    @classmethod
    def add_one_normal(cls, data):
        try:
            db_session.add(data)
            db_session.commit()
        except Exception as e:
            print(e)
            db_session.rollback()

    @classmethod
    def add_all_normal(cls, datas):
        try:
            db_session.add_all(datas)
            db_session.commit()
        except Exception as e:
            db_session.rollback()

    @classmethod
    def add_all(cls, session, datas):
        try:
            session.add_all(datas)
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()

    @classmethod
    def get(cls, model_class, start=None, count=None, one=True, **kwargs):
        if one:
            first = db_session.query(model_class).filter().filter_by(**kwargs).first()
            return first
        else:
            count__all = db_session.query(model_class).filter().filter_by(**kwargs).offset(start).limit(count).all()
            return count__all

    @classmethod
    def check_repaet(cls, model_class, updated=False, **kwargs):
        if updated:
            id = kwargs.pop('id')
            res = db_session.query(func.count('*')).select_from(model_class).filter(model_class.id != id).filter_by(
                **kwargs).scalar()
        else:
            res = db_session.query(func.count('*')).select_from(model_class).filter_by(**kwargs).scalar()
        return res

    @classmethod
    def native_query(cls, sql, params={}, auto_sample_parse=False, auto_query_counts=False):
        """
        原生sql 查询
        :param sql:原生sql
        :param params: 字典
        :param auto_sample_parse: 自动解析动态sql （有可能解析出错 暂时不成熟 可以试用 经过部分测试 持续迭代）
        :param auto_query_counts: 查询数量 将sql去掉limit  order by后包装一层查询总数
        :return:列表，数量
        """
        cls._check_params(sql, params)
        if params and len(params) > 0 and auto_sample_parse:
            sql, params = cls._handle_sql(sql, params)
        sql = sql.strip()
        stmt = text(sql)
        res_list = []
        res = db_session.execute(stmt, params) if params else db_session.execute(stmt)
        for record in res:
            row_dict = dict((zip(record.keys(), record)))
            res_list.append(row_dict)
        counts = None
        if auto_query_counts:
            inner_sql = re.sub('limit.*', '', sql)
            inner_sql = re.sub('order by.*', '', inner_sql)
            wrapper = "SELECT count(1) from ( {inner} )as  _count__wrapper ".format(inner=inner_sql)
            stmt = text(wrapper)
            counts_res = db_session.execute(stmt, params) if params else db_session.execute(stmt)
            for cx in counts_res:
                counts = cx[0]
        return res_list, counts

    @classmethod
    def native_update(cls, sql, params={}, commit=True):
        """
        原生sql 更新 新增 删除
        :param sql:
        :param params: 字典
        :param commit: 是否提交
        :return: 影响行数
        """
        cls._check_params(sql, params)
        sql = sql.strip()
        stmt = text(sql)
        res = db_session.execute(stmt, params) if params else db_session.execute(stmt)
        if commit:
            db_session.commit()
        return res.rowcount if commit else 0

    @classmethod
    def _check_params(cls, sql, params):
        if sql is None or sql.strip() is None:
            raise Exception('参数错误')
        if params:
            params_count_list = re.findall(':', sql)
            if len(params_count_list) < len(params) or len(params_count_list) == 0:
                raise Exception('无效的参数或占位符')

    @classmethod
    def _handle_sql(cls, sql, params):
        for k in params.keys():
            key = ':' + k
            if ('=' + key) not in sql or isinstance(params[k], Number) or params[k].isnumeric():
                sql = re.sub(key, str(params[k]), sql)
            else:
                sql = re.sub(key, "'" + str(params[k]) + "'", sql)
        sql = re.sub(':', '#', sql)
        sql = re.sub('(and(\s*)(\w+).?(\w+)(=|>=|!+|<=)#\w+)', ' ', sql)
        sql = re.sub("and(\s*)(\w+.\w+)(\s*)like(\s*)('%'.#\w+.'%')", ' ', sql)
        sql = re.sub('order\sby\s#\w+', ' ', sql)
        p = "like(\s*)'%'.(.*?).'%' "
        if 'like' in sql:
            sql = re.sub(p, cls._patch_handle_like, sql)
        print(sql)
        params = None
        return sql, params

    @classmethod
    def _patch_handle_like(cls, x):
        return "like '%" + x.groups()[1].replace("'", '') + "%' "

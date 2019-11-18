# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      utils
# Author:    liangbaikai
# Date:      2019/10/28
# Desc:      there is a python file description
# ------------------------------------------------------------------
import hashlib
import time
from functools import wraps
from threading import RLock




class Retry(object):
    def __init__(self, f=None, max_retries: int = 3, delay: int = 1, validate=None, callback=None):
        """
         :param f:不传  应该为none
        :param max_retries: 最大重试次数; 默认三次
        :param delay: 每次的执行延时时间 单位 秒; 默认1秒
        :param validate: 验证函数 若为空 则目标函数返回false 或者none将自动重试 validate不为空时，
        validate函数返回false 或none时将继续重试，否则停止并返回结果
        :param callback: 目标函数异常时的回调函数 错误信息将传给此回调 将继续重试; 默认 无
        """
        if f is not None:
            raise AttributeError('you should write your detartor be "@Retry()", should do not use "@Retry" ')
        self.max_retries = max_retries
        self.delay = delay
        self.validate = validate
        self.callback = callback

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            while self.max_retries > 0:
                try:
                    result = func(*args, **kwargs)
                    if self.validate is None:
                        if result is None or result == False:
                            continue

                    if callable(self.validate) and self.validate(result) is False:
                        continue
                    else:
                        return result
                except Exception as e:
                    print(e)
                    self.callback and self.callback(e)
                finally:
                    self.max_retries -= 1
                    if self.delay > 0:
                        time.sleep(self.delay)

        return inner


"""
单例
"""


class SingleInstance(object):
    def __init__(self, *args, **kwargs):
        self.lock = RLock()
        self.arg = args
        self.kwargs = kwargs

    def __call__(self, cls):
        @wraps(cls)
        def new(*args, **kwargs):
            with self.lock:
                if not hasattr(cls, '_instance'):
                    with self.lock:
                        cls._instance = object.__new__(cls, *args, **kwargs)
                        getattr(cls._instance, '__init__')(*args, **kwargs)
            return cls._instance

        return new


"""
统一验证参数
"""


def _handle_first_word(name):
    """
    首字母小写
    :param name:
    :return:
    """
    if name is None:
        return ""
    return name[0].lower() + name[1:]


class EncrptUtils:
    @classmethod
    def md5_str(cls, inputs: str):
        inputs = str(inputs)
        md5 = hashlib.md5()
        md5.update(inputs.encode('utf-8'))
        return md5.hexdigest()


class DateTimeUtils:
    @classmethod
    def now(cls, tz_str='Asia/Shanghai'):
        from datetime import datetime
        from dateutil.tz import tz
        now = datetime.now(tz=tz.gettz(tz_str))
        now = now.replace(tzinfo=None)
        return now


if __name__ == '__main__':
    pass

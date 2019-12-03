# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      __init__.py
# Author:    liangbaikai
# Date:      2019/12/3
# Desc:      there is a python file description
# ------------------------------------------------------------------
import json
import re
import time

import requests
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.support.select import Select

from RCL.utils.utils import EncrptUtils, DateTimeUtils


def test_ial(form):
    url = 'http://www.interasia.cc/content/c_service/sailing_schedule.aspx?SiteID=1'
    # form = {
    #     "__VIEWSTATE": "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",
    #     "__VIEWSTATEGENERATOR": "99DD0D69",
    #     "__SCROLLPOSITIONX": "0",
    #     "__SCROLLPOSITIONY": "0",
    #     "__EVENTVALIDATION": "VgvG23TwM4DZ7lOSTDDl+cSGeTwyKw6U9aeeYCkU8vYBQJ9XnVr/D4BjQwNH/+fB+w2O+n/t42OqY+VvA2dSVY+HKvxX9H/Q7jTzBzgOa7X9gYwnCWndlOeADPXSDqBmRhV/CGboCLa+qa37gFrZp7U00Y+Wq/PYnyf+BTWNrTsFv5cDvEaHdkSrObSIQfnM6SU3flitoyHdWO6nPtc3rm+G4IGok9v4LwAsjMwNZDv/hoeGvnkthmJ2XWV8JzvPN8oZLejbQ3c9P7m7qxz9EhDjCafxJliOzZxoMjoU8Xr0tDWvdg/NxVea/W1OURTinU7UCx8p4HQAWoj22B0K1FYUMbVCtvMLKjHsa4amWwb18UkGPvW7q8fLppAQcxmiiMimdmfQP3p6DM7pmeLnZmN8vcJBuJ9jN+hVGXr+cPDy9XV7YLWtIwgaqlTiEHZy1p86ZtlgTnu+uJCr/PiKQ0NTof0=",
    #     "ctl00$UCHeader$txtSearch": "Search",
    #     "ctl00$CPHContent$ddlDepartureC": "7",
    #     "ctl00$CPHContent$ddlDepartureL": "8",
    #     "ctl00$CPHContent$ddlDestinationC": "710202045756516143",
    #     "ctl00$CPHContent$ddlDestinationL": "2016053012323230376",
    #     "ctl00$CPHContent$txtCode": "BIXK",
    #     "ctl00$CPHContent$btnSend": "Search",
    #     "__LASTFOCUS": '',
    #     "__EVENTARGUMENT": '',
    #     "__EVENTTARGET": '',
    #     "__VIEWSTATEENCRYPTED": '',
    # }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "ASP.NET_SessionId=hfrkbpnbid3wgy450pqfoc45",
        "Referer": "http://www.interasia.cc/content/c_service/sailing_schedule.aspx?SiteID=1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
    }
    res = requests.post(url=url, data=form, headers=headers)
    print(res.status_code)
    print(res.text)


class Spider:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.binary_location = r"D:\soft\googlechrome\Application\77.0.3865.120\chrome.exe"
        epath = "D:/work/chromedriver.exe"
        brower = webdriver.Chrome(executable_path=epath, chrome_options=options)
        self.brower = brower
        self.brower.maximize_window()

    def start(self, url):
        self.brower.get(url)
        self.do_action()

    def do_action(self):
        mm = Select(self.brower.find_element_by_id('ctl00_CPHContent_ddlDepartureC')).select_by_index('1')
        time.sleep(1)
        Select(self.brower.find_element_by_id('ctl00_CPHContent_ddlDepartureL')).select_by_index('1')
        time.sleep(1)
        Select(self.brower.find_element_by_id('ctl00_CPHContent_ddlDestinationC')).select_by_index('2')
        time.sleep(1)
        Select(self.brower.find_element_by_id('ctl00_CPHContent_ddlDestinationL')).select_by_index('1')
        # ctl00_CPHContent_imgCode //*[@id="ctl00_CPHContent_imgCode"]
        time.sleep(1)
        code = self.brower.find_element_by_id('ctl00_CPHContent_imgCode').get_attribute('src')
        code = code[-4:]
        ele = self.brower.find_element_by_id('ctl00_CPHContent_txtCode')
        ele.send_keys(code)
        time.sleep(1)

        # 获取参数
        # __EVENTARGUMENT  __EVENTTARGET   __VIEWSTATE  _
        # _LASTFOCUS  __VIEWSTATEGENERATOR  __SCROLLPOSITIONX __SCROLLPOSITIONY
        # __VIEWSTATEENCRYPTED __EVENTVALIDATION
        # ctl00$CPHContent$ddlDepartureC ctl00$CPHContent$ddlDepartureL
        # ctl00$CPHContent$ddlDestinationC ctl00$CPHContent$ddlDestinationL
        # ctl00$CPHContent$txtCode
        __EVENTARGUMENT = self.brower.find_element_by_id('__EVENTARGUMENT').get_attribute('value')
        __EVENTTARGET = self.brower.find_element_by_id('__EVENTTARGET').get_attribute('value')
        __VIEWSTATE = self.brower.find_element_by_id('__VIEWSTATE').get_attribute('value')
        __LASTFOCUS = self.brower.find_element_by_id('__LASTFOCUS').get_attribute('value')
        __VIEWSTATEGENERATOR = self.brower.find_element_by_id('__VIEWSTATEGENERATOR').get_attribute('value')
        __SCROLLPOSITIONX = self.brower.find_element_by_id('__SCROLLPOSITIONX').get_attribute('value')
        __SCROLLPOSITIONY = self.brower.find_element_by_id('__SCROLLPOSITIONY').get_attribute('value')
        __VIEWSTATEENCRYPTED = self.brower.find_element_by_id('__VIEWSTATEENCRYPTED').get_attribute('value')
        __EVENTVALIDATION = self.brower.find_element_by_id('__EVENTVALIDATION').get_attribute('value')
        options = self.brower.find_elements_by_xpath("//*[@id='ctl00_CPHContent_ddlDepartureC']/option")
        start_counry = list(filter(lambda opt: opt.is_selected(), options))[0]
        options = self.brower.find_elements_by_xpath("//*[@id='ctl00_CPHContent_ddlDepartureL']/option")
        start_city = list(filter(lambda opt: opt.is_selected(), options))[0]
        options = self.brower.find_elements_by_xpath("//*[@id='ctl00_CPHContent_ddlDestinationC']/option")
        end_country = list(filter(lambda opt: opt.is_selected(), options))[0]
        options = self.brower.find_elements_by_xpath("//*[@id='ctl00_CPHContent_ddlDestinationL']/option")
        end_city = list(filter(lambda opt: opt.is_selected(), options))[0]
        # self.brower.find_element_by_id('ctl00_CPHContent_btnSend').click()
        form = dict(__EVENTARGUMENT=__EVENTARGUMENT, __EVENTTARGET=__EVENTTARGET, __LASTFOCUS=__LASTFOCUS,
                    __VIEWSTATE=__VIEWSTATE, __VIEWSTATEGENERATOR=__VIEWSTATEGENERATOR,
                    __SCROLLPOSITIONX=__SCROLLPOSITIONX, __SCROLLPOSITIONY=__SCROLLPOSITIONY,
                    __VIEWSTATEENCRYPTED=__VIEWSTATEENCRYPTED, __EVENTVALIDATION=__EVENTVALIDATION,
                    )
        form.setdefault("ctl00$UCHeader$txtSearch", 'Search')
        form.setdefault("ctl00$CPHContent$btnSend", 'Search')

        _fisrt = start_counry.get_attribute('value')
        _second = start_city.get_attribute('value')
        _three = end_country.get_attribute('value')
        _fourth = end_city.get_attribute('value')
        form.setdefault('ctl00$CPHContent$ddlDepartureC', _fisrt)
        form.setdefault('ctl00$CPHContent$ddlDepartureL', _second)
        form.setdefault('ctl00$CPHContent$ddlDestinationC', _three)
        form.setdefault('ctl00$CPHContent$ddlDestinationL', _fourth)
        form.setdefault('ctl00$CPHContent$txtCode', code)
        # test_ial(form)
        _date = DateTimeUtils.now_str(format=DateTimeUtils.FORMATER_DATE)
        key = ','.join([_fisrt, _second, _three, _fourth, _date])
        # key = EncrptUtils.md5_str(_key)
        saves = dict()
        saves.setdefault(key, form)
        with open('test.json', 'w+') as f:
            json.dump(saves, f)


if __name__ == '__main__':
    # test_ial()
    # session = HTMLSession()
    url = 'http://www.interasia.cc/content/c_service/sailing_schedule.aspx?SiteID=1'
    s = Spider()
    s.start(url)
    time.sleep(2)
    with open('test.json', 'r') as f:
        res = json.load(f)
    for k, v in res.items():
        test_ial(v)

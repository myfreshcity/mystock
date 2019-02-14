#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2

import http,requests
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

users_roles = db.Table(
    'users_roles',
    db.Column('user_id', db.String(45), db.ForeignKey('users.id')),
    db.Column('role_id', db.String(45), db.ForeignKey('roles.id')))

def getHeaders(url):
    CookieJar = http.cookiejar.CookieJar()
    CookieProcessor = urllib2.HTTPCookieProcessor(CookieJar)
    opener = urllib2.build_opener(CookieProcessor)
    urllib2.install_opener(opener)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0'}
    request = urllib2.Request(url, headers=headers)
    #httpf = opener.open(request)
    return headers

def getXueqiuHeaders():
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry

    # 构造 Request headers
    agent = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    headers = {
        'User-Agent': agent,
        'Host': "xueqiu.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.6",
        "Connection": "keep-alive"
    }

    session = requests.session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    url = 'https://xueqiu.com/'
    session.get(url, headers=headers)  # 访问首页产生 cookies
    headers['Referer'] = "https://xueqiu.com/"

    #url = 'https://xueqiu.com/stock/f10/otsholder.json?symbol=SZ000418&page=1&size=4'
    #log = session.get(url, headers=headers)
    #log.content
    return session,headers
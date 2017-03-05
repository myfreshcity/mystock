import urllib2

import http
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def getHeaders(url):
    CookieJar = http.cookiejar.CookieJar()
    CookieProcessor = urllib2.HTTPCookieProcessor(CookieJar)
    opener = urllib2.build_opener(CookieProcessor)
    urllib2.install_opener(opener)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0'}
    request = urllib2.Request(url, headers=headers)
    #httpf = opener.open(request)
    return headers
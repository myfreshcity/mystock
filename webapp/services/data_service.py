# -*- coding: utf-8 -*-
import sys
from bs4 import  BeautifulSoup,BeautifulStoneSoup
from sqlalchemy import *
import pandas as pd
import numpy as np
from flask import current_app as app
from webapp.services import db
from webapp.models import MyStock,Stock,data_item,Comment,FinanceBasic
import json,random,time
from pandas.tseries.offsets import *
from datetime import datetime
import urllib2,re,html5lib

headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}

def updateTradeBasic(code,market):
    #获得开始日期.数据库的最大时间或者2000.1.1
    sql = "select max(trade_date) from stock_trade_basic where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        st_year = '2000'
        st_month = '00' #yahoo月份的特殊处理
        st_day = "01"
    else:
        st_year = s_date.strftime("%Y")
        st_month = "%02d" % (s_date.month)  # yahoo月份的特殊处理,从下一月开始
        st_day = "%02d" % (s_date.day)

    #获得结束日期.当前日期上月最后一天
    e_date = datetime.now() - MonthEnd()
    ed_year = e_date.strftime("%Y")
    ed_month = "%02d" % (e_date.month-1) #yahoo月份的特殊处理
    ed_day = "%02d" % (e_date.day)

    #根据类型获取市场代码
    mc = '.SS' if market=='sh' else '.SZ'
    url = 'http://ichart.yahoo.com/table.csv?s=' + code + mc + '&a=' + st_month + '&b=' + st_day + '&c=' + st_year +\
            '&d=' + ed_month + '&e=' + ed_day + '&f=' + ed_year + '&g=m'
    app.logger.info('query stock('+code+') trade data url is:'+url)
    try:
        df = pd.read_csv(url)
        df1 = pd.DataFrame({
            'trade_date': df['Date'],
            'close': df['Close'],
            'volume': df['Volume'],
            'adj_close': df['Adj Close'],
            'code': code
        })
        df1.to_sql('stock_trade_basic', db.engine, if_exists='append', index=False, chunksize=1000)
    except Exception, ex:
        app.logger.error(ex)


def updateFinanceBasic(code):
    #获得2000年以来的所有会计年度
    index = pd.date_range('2000-1-1', datetime.today(), freq='Q')
    periods = [x.strftime('%Y.%m.%d') for x in index]

    #为避免网络访问频繁,分2年为一个阶段分别读取数据取值
    l = len(periods)
    i = 0
    while (i <= l):
        ri = random.randint(3, 8)
        time.sleep(ri) #延迟执行
        updateFinanceBasicByPeriod(periods[i:i+8],code)
        i = i + 8


def updateFinanceBasicByPeriod(periods,code):
    df = pd.DataFrame()
    for x in periods:
        fb = db.session.query(FinanceBasic).filter_by(code=code, report_type=x).first()
        if (not fb):
            fd = findFinanceData(code, x)
            if not fd.empty:
                df = df.append(fd)

    if df.size > 0:
        df.columns = ['code', 'report_type', 'yysr', 'jlr', 'lrze', 'kjlr', 'zzc', 'gdqy', 'jyjxjl', 'mgsy', 'roe',
                      'mgjyxjl', 'mgjzc']
        tpd = pd.DataFrame({
            'mgsy_ttm': '',
            'mgjyxjl_ttm': ''
        }, index=df.index)

        df1 = pd.concat([df, tpd], axis=1)
        ndf = calculateTTMValue(df1, code)
        ndf.to_sql('stock_finance_basic', db.engine, if_exists='append', index=False, chunksize=1000)
        app.logger.info(code + ' finance update done...')
        return True
    else:
        return False


def findFinanceData(code,period):
    app.logger.info('begin query finance data:'+code+'-'+period)
    period = re.sub('03.31', '03.15', period)
    url = "http://stockdata.stock.hexun.com/2008/zxcwzb.aspx?stockid="+code+"&accountdate="+period
    req = urllib2.Request(url =url,headers = headers)
    feeddata = urllib2.urlopen(req).read()
    soup = BeautifulSoup(feeddata, "lxml")
    paper_name = soup.html.body.find(id="zaiyaocontent").table.find_all('tr')
    if paper_name == []:
        return pd.DataFrame()
    else:
        data = [code]
        for e in paper_name:
            s = e.find_all('td')
            i = '0' if s[1].div.text == '--' else re.sub(',', '',s[1].div.text)
            data.append(i)

        df = pd.DataFrame(data).T
        #如果无会计日期,丢弃数据
        if df.iat[0, 1]=='':
            return pd.DataFrame()
        else:
            return df.iloc[:,:13]

#更新ttm数据
def calculateTTMValue(in_df,code):
    in_df_date = in_df['report_type'].map(lambda x: pd.to_datetime(x))

    df = pd.read_sql_query(
        "select code,report_type,yysr,jlr,lrze,kjlr,zzc,gdqy,jyjxjl,mgsy,roe,mgjyxjl,mgjzc,mgsy_ttm,mgjyxjl_ttm \
        from stock_finance_basic \
        where code=%(name)s",
        db.engine, params={'name': code})

    df = df.append(in_df)
    i = df['report_type'].map(lambda x: pd.to_datetime(x))
    df3 = df.set_index(i)

    for index, row in df3.iterrows():
        if row.mgjyxjl_ttm is None or row.mgjyxjl_ttm == '':
            # 去年年底
            lastYearEnd = YearEnd().rollback(index)
            # offset = offset.strftime('%Y-%m-%d')
            lastYearQuart = index - DateOffset(months=12)
            app.logger.debug(index.strftime('%Y-%m-%d') + ':' + lastYearEnd.strftime('%Y-%m-%d') + ':' + lastYearQuart.strftime(
                '%Y-%m-%d'))
            try:
                if index.quarter != 4:
                    n_mgsy = float(df3.loc[lastYearEnd].mgsy) - float(df3.loc[lastYearQuart].mgsy) + float(row.mgsy)
                    n_mgjyxjl = float(df3.loc[lastYearEnd].mgjyxjl) - float(df3.loc[lastYearQuart].mgjyxjl) + float(
                        row.mgjyxjl)
                else:
                    n_mgsy = float(row.mgsy)
                    n_mgjyxjl = float(row.mgjyxjl)

                df3.mgsy_ttm.loc[index] = n_mgsy
                df3.mgjyxjl_ttm.loc[index] = n_mgjyxjl

            except Exception, ex:
                app.logger.error(ex)
                df3.mgsy_ttm.loc[index] = float(row.mgsy)
                df3.mgjyxjl_ttm.loc[index] = float(row.mgjyxjl)

            #数据位截取
            df3.mgsy_ttm.loc[index] = round(df3.mgsy_ttm.loc[index],2)
            df3.mgjyxjl_ttm.loc[index] = round(df3.mgjyxjl_ttm.loc[index],2)

    return df3.iloc[df3.index.isin(in_df_date)]
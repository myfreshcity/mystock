# -*- coding: utf-8 -*-
import sys
from bs4 import  BeautifulSoup,BeautifulStoneSoup
from sqlalchemy import *
import pandas as pd
import numpy as np
from flask import current_app as app
from webapp.services import db,db_service as dbs
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
        s_date = pd.to_datetime('2000-01-01').date()
    else:
        st_year = s_date.strftime("%Y")
        st_month = "%02d" % (s_date.month)  # yahoo月份的特殊处理,从下一月开始
        st_day = "%02d" % (s_date.day)

    #获得结束日期.当前日期上月最后一天
    e_date = (datetime.now() - MonthEnd()).date()
    #日期间隔在一个月内,跳过.因为取的是月线数据
    if((e_date - s_date).days<30):
        app.logger.info('interval date less than 30 days, skip...')
        return

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

def updateTradeData(code,market):
    #获得开始日期
    sql = "select max(trade_date) from stock_trade_data where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        s_date = dbs.getStock(code).launch_date #取上市日期
    e_date = datetime.now().date()

    #根据类型获取市场代码
    mc = '0' if market=='sh' else '1'
    url = 'http://quotes.money.163.com/service/chddata.html?code=' + mc  + code +\
          '&start=' + s_date.strftime("%Y%m%d") + '&end=' + e_date.strftime("%Y%m%d") + '&fields=TCLOSE;VATURNOVER;TCAP;MCAP'
    app.logger.info('query stock('+code+') trade data url is:'+url)
    try:
        tdf = pd.read_csv(url,names=['trade_date','code','name','close','volume','t_cap','m_cap'],header=0)
        df1 = pd.DataFrame({
            'trade_date': tdf['trade_date'],
            'close': tdf['close'],
            'volume': tdf['volume'],
            't_cap': tdf['t_cap'],
            'm_cap': tdf['m_cap'],
            'code': code
        })
        if not df1.empty:
            if df1['trade_date'].max() > s_date.strftime("%Y%m%d"):
                df1.to_sql('stock_trade_data', db.engine, if_exists='append', index=False, chunksize=1000)
    except Exception, ex:
        app.logger.error(ex)

def updateStockHolder(code):
    latest_val = ''
    url = "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CirculateStockHolder/stockid/" + code + ".phtml"
    req = urllib2.Request(url=url, headers=headers)
    feeddata = urllib2.urlopen(req).read()
    soup = BeautifulSoup(feeddata, "html5lib")
    paper_name = soup.html.body.find(id="CirculateShareholderTable").tbody.find_all('tr')

    report_date = []
    holder_name = []
    amount = []
    rate = []
    holder_type = []
    holder_parent = []
    rdate = ''
    i = 0
    for e in paper_name:
        t = e.find_all('td')
        s = e.find_all('strong')
        if len(s) > 0:
            if s[0].string == '截止日期':
                rdate = t[1].string
                i += 1
                if i ==1:
                    latest_val = rdate

        if t[0].div:
            if t[0].div.string:
                if t[0].div.string.isdigit():
                    hname = t[1].div.text
                    report_date.append(rdate)
                    holder_name.append(hname)
                    amount.append(t[2].div.string)
                    rate.append(t[3].div.string)
                    holder_type.append(t[4].div.string)
                    holder_parent.append(hname.split('-')[0])
    df1 = pd.DataFrame({
        'code': code,
        'report_date': report_date,
        'holder_name': holder_name,
        'amount': amount,
        'rate': rate,
        'holder_type': holder_type,
        'holder_parent': holder_parent

    })
    df1.to_sql('stock_holder', db.engine, if_exists='append', index=False, chunksize=1000)
    return latest_val


def getStockHighPrice(code,market):
    #获取从最近买入到现在的股价
    sql = "select in_date from my_stocks where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        return 0
    else:
        st_year = s_date.strftime("%Y")
        st_month = "%02d" % (s_date.month-1)  # yahoo月份的特殊处理,从下一月开始
        st_day = "%02d" % (s_date.day)

    #获得结束日期.当前日期
    e_date = datetime.now().date()
    ed_year = e_date.strftime("%Y")
    ed_month = "%02d" % (e_date.month-1) #yahoo月份的特殊处理
    ed_day = "%02d" % (e_date.day)
    # 日期间隔短，跳过.
    if ((e_date - s_date).days < 1):
        app.logger.info('interval date less than 1 days, skip...')
        return 0

    #根据类型获取市场代码
    mc = '.SS' if market=='sh' else '.SZ'
    url = 'http://ichart.yahoo.com/table.csv?s=' + code + mc + '&a=' + st_month + '&b=' + st_day + '&c=' + st_year +\
            '&d=' + ed_month + '&e=' + ed_day + '&f=' + ed_year + '&g=d'
    app.logger.info('query stock('+code+') trade data url is:'+url)
    try:
        df = pd.read_csv(url)
        return df['Close'].max()

    except Exception, ex:
        app.logger.error(ex)

def updateFinanceData(code):
    # 获得开始日期
    sql = "select max(report_type) from stock_finance_data where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        s_date = dbs.getStock(code).launch_date  # 取上市日期

    url = 'http://quotes.money.163.com/service/zycwzb_' + code + '.html?type=report'
    tdf = pd.read_csv(url)
    tdf = tdf.iloc[:, 1:].dropna(axis=1).T.reset_index()

    def fixNaN(x):
        return 0 if x == '--' else x

    def getRevence(x, attri):
        dt = pd.to_datetime(x)
        s_dt = tdf[tdf['index'] == dt.strftime('%Y-%m-%d')]
        lastYearEnd = YearEnd().rollback(dt)  # 去年年底
        s_lye = tdf[tdf['index'] == lastYearEnd.strftime('%Y-%m-%d')]
        lastYearQuart = dt - DateOffset(months=12)  # 去年同期
        s_lyq = tdf[tdf['index'] == lastYearQuart.strftime('%Y-%m-%d')]
        app.logger.debug(
            dt.strftime('%Y-%m-%d') + ':' + lastYearEnd.strftime('%Y-%m-%d') + ':' + lastYearQuart.strftime(
                '%Y-%m-%d'))
        v1 = s_dt.get(attri)

        if dt.quarter != 4:
            v2 = s_lye.get(attri)
            v3 = s_lyq.get(attri)
            if v2.empty or v3.empty:
                v2 = 0
                v3 = 0
        else:
            v2 = 0
            v3 = 0
        try:
            return int(v1) + (int(v2) - int(v3))
        except Exception, ex:
            app.logger.error(ex)
            return 0

    if tdf['index'].max() > s_date.strftime("%Y%m%d"):
        df = pd.DataFrame({
            'report_type': tdf['index'],
            'zyysr': tdf[3].apply(fixNaN),
            'zyysr_ttm': tdf['index'].apply(getRevence, args=(3,)),
            'zyylr': tdf[4].apply(fixNaN),
            'yylr': tdf[5].apply(fixNaN),
            'jlr': tdf[9].apply(fixNaN),
            'jlr_ttm': tdf['index'].apply(getRevence, args=(9,)),
            'kjlr': tdf[10].apply(fixNaN),
            'jyjxjl': tdf[11].apply(fixNaN),
            'jyjxjl_ttm': tdf['index'].apply(getRevence, args=(11,)),
            'xjjze': tdf[12].apply(fixNaN),
            'zzc': tdf[13].apply(fixNaN),
            'ldzc': tdf[14].apply(fixNaN),
            'zfz': tdf[15].apply(fixNaN),
            'ldfz': tdf[16].apply(fixNaN),
            'gdqy': tdf[17].apply(fixNaN),
            'roe': tdf[18].apply(fixNaN),
            'code': code
        })
        # insert new data to database
        df = df.set_index('report_type')
        sd = df.index.max()
        ed = (s_date + DateOffset(days=1)).date().strftime('%Y-%m-%d') #排除掉之前插入的数据
        edf = df.loc[sd:ed].reset_index()
        edf.to_sql('stock_finance_data', db.engine, if_exists='append', index=False, chunksize=1000)

def updateFinanceBasic(code):
    sql = "select max(report_type) from stock_finance_basic where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        s_date = '2000.01.01' #获得2000年以来的所有会计年度

    index = pd.date_range(s_date, datetime.today(), freq='Q')
    periods = [x.strftime('%Y.%m.%d') for x in index]

    #为避免网络访问频繁,分2年为一个阶段分别读取数据取值
    l = len(periods)
    i = 0
    while (i <= l):
        ri = random.randint(2, 5)
        time.sleep(ri) #延迟执行
        updateFinanceBasicByPeriod(periods[i:i+16],code)
        i = i + 16


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
    period = re.sub('03.31', '03.15', period)
    url = "http://stockdata.stock.hexun.com/2008/zxcwzb.aspx?stockid="+code+"&accountdate="+period
    app.logger.info('query stock(' + code + ') finance data url is:' + url)
    req = urllib2.Request(url =url,headers = headers)
    feeddata = urllib2.urlopen(req).read()
    soup = BeautifulSoup(feeddata, "html5lib")
    paper_name = soup.html.body.find(id="zaiyaocontent").table.tbody
    if paper_name is None:
        return pd.DataFrame()
    else:
        paper_name = paper_name.find_all('tr')
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
                app.logger.warn(ex)
                df3.mgsy_ttm.loc[index] = float(row.mgsy)
                df3.mgjyxjl_ttm.loc[index] = float(row.mgjyxjl)

            #数据位截取
            v_mgsy_ttm = round(df3.mgsy_ttm.loc[index],2)
            v_mgjyxjl_ttm = round(df3.mgjyxjl_ttm.loc[index],2)
            #零值处理
            v_mgsy_ttm = 0.01 if v_mgsy_ttm==0 else v_mgsy_ttm
            v_mgjyxjl_ttm = 0.01 if v_mgjyxjl_ttm == 0 else v_mgjyxjl_ttm

            df3.mgsy_ttm.loc[index] = v_mgsy_ttm
            df3.mgjyxjl_ttm.loc[index] = v_mgjyxjl_ttm

    return df3.iloc[df3.index.isin(in_df_date)]

def refreshStockHolder():
    #获得所有股票代码列表
    stocks = db.session.query(Stock).filter(and_(Stock.latest_report < '2016-03-31',Stock.launch_date < '2016-03-31')).limit(200).all()
    #stocks = db.session.query(Stock).all()
    for st in stocks:
        app.logger.info('checking stock holder for:' + st.code)
        latest_report = updateStockHolder(st.code)
        st.latest_report = latest_report
        db.session.flush()

#获取指定日期的最高收盘价
def getPerStockHighPrice(df):
    st_valus = []
    st_codes = []
    for index, row in df.iterrows():
        trade_data = getStockHighPrice(index, row['market'])
        v = round(trade_data, 2)
        st_valus.append(v)
        st_codes.append(index)
    return pd.DataFrame(st_valus, index=st_codes,columns=['mprice'])

def getMyStocks(flag):
    df = pd.read_sql_query("select ms.id,ms.code,ms.name,ms.market,sb.zgb,sb.launch_date,ms.in_price,ms.in_date,sb.grow_type from my_stocks ms,stock_basic sb " \
                           "where ms.code=sb.code and ms.code != '000001' and ms.flag=%(flag)s ", db.engine, \
                           index_col='code', params={'flag': flag})
    df1 = dbs.getPerStockPrice(df)
    df2 = dbs.getPerStockRevenue()
    if flag == '0':
        df11 = getPerStockHighPrice(df)
        df3 = pd.concat([df1, df11, df2], axis=1, join='inner')
    else:
        df3 = pd.concat([df1, df2], axis=1, join='inner')

    df = df.reset_index()
    df4 = pd.merge(df, df3, how='left')
    return df4


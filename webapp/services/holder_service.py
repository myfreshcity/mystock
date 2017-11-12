# -*- coding: utf-8 -*-
import sys
from bs4 import  BeautifulSoup,BeautifulStoneSoup
from sqlalchemy import *
from flask import g
import pandas as pd
import numpy as np
from flask import current_app as app
from webapp.services import db,getHeaders,getXueqiuHeaders,db_service as dbs
from webapp.models import Stock,Comment,FinanceBasic
import json,random,time
import http.cookiejar
from pandas.tseries.offsets import *
from datetime import datetime
import urllib2,re,html5lib

group_stockholder_rate = None
session, headers = getXueqiuHeaders()


def getLatestStockHolder():
    global group_stockholder_rate
    if group_stockholder_rate is None:
        hdf = pd.read_sql_query("select code,report_date,holder_type,holder_name,rate\
                                   from stock_holder order by report_date desc", db.engine)
        group_stockholder_rate = hdf.groupby(['code']).head(10)
        #group_stockholder_rate = gdf[gdf['holder_type'] != '自然人股']
    return group_stockholder_rate

def getRefreshStocks():
    start_date = datetime.now().strftime('%Y-%m-%d')
    #获得所有股票代码列表
    stocks = db.session.query(Stock).filter(or_(Stock.holder_updated_time == None,Stock.holder_updated_time < start_date)).all()
    return map(lambda x:x.code, stocks)


def refreshStockHolderSum(gdf,code):
    #gdf = getLatestStockHolder()

    agdf = gdf[gdf['holder_type'] != '自然人股']
    a1gdf = agdf.groupby(['report_date'])

    t1_gdf = a1gdf['rate'].agg({'size': np.size})
    t1_gdf = t1_gdf.reset_index()
    t2_gdf = a1gdf['rate'].agg({'sum': np.sum})
    t2_gdf = t2_gdf.reset_index()

    t3_gdf = pd.merge(t1_gdf, t2_gdf, on='report_date')
    t3_gdf = t3_gdf.sort_values(by='report_date', ascending=False).head(1)
    t3_gdf['code'] = code
    bdf = pd.read_sql_query("select * from stock_basic where code =%(code)s", db.engine, params={'code': code})
    t3_df = pd.merge(t3_gdf, bdf, on='code')

    m2_df = pd.DataFrame({
        'code': t3_df.code,
        'name': t3_df['name'],
        'report_date': t3_df.report_date,
        'count': t3_df['size'],
        'sum': t3_df['sum']
    })
    if not m2_df.empty:
        for row_index, row in m2_df.iterrows():
            sql = text("delete from stock_holder_sum  where code =:code")
            result = db.session.execute(sql,{'code': row.code})
        m2_df.to_sql('stock_holder_sum', db.engine, if_exists='append', index=False, chunksize=1000)
        global group_stockholder_rate
        group_stockholder_rate = None

#获得机构持股比例
def getGroupStockHolderRate():
    df = pd.read_sql_query(
        "select code,count,sum,report_date from stock_holder_sum",
        db.engine)
    return df

#获得自然人持股排行榜
def getStockHolderRank():
    gdf = getLatestStockHolder()
    agdf = gdf[gdf['holder_type'] == '自然人股']
    a1gdf = agdf.groupby(['code'])

    t2_gdf = a1gdf['rate'].agg({'sum': np.sum}) #比例
    t3_gdf = a1gdf['rate'].agg({'size': np.size}) #个数

    t4_df = pd.concat([t2_gdf, t3_gdf], axis=1, join='inner')
    t41_df = pd.DataFrame({
        'sum': t4_df['sum'],
        'count': t4_df['size'],
        'avg': t4_df['sum'] / t4_df['size']
    })

    t5_df = t41_df.sort_index(by='avg', ascending=True).head(100)
    t6_df = t5_df.reset_index()

    bdf = pd.read_sql_query("select * from stock_basic sb ", db.engine)
    t7_df = pd.merge(t6_df, bdf, on='code')
    return t7_df

def getStockHolderFromNet(code):
    #app.logger.info('checking stock holder for:' + code)
    mc = 'SH' if code[:2] == '60' else 'SZ'
    url = "https://xueqiu.com/stock/f10/shareholder.json?symbol=" + mc + code + "&page=1&size=4"
    #app.logger.debug('stock holder url is:' + url)
    # req = urllib2.Request(url=url, headers=headers)
    # feeddata = urllib2.urlopen(req).read()
    res1 = session.get(url, headers=headers)
    return {'code':code,'data':json.loads(res1.content)}

def updateStockHolder(data):
    code = data['code']
    fd = data['data']
    fArray = []
    if fd['list'] is None:
        return

    for e in fd['list']:
        fArray = fArray + e['list']
    ndf = pd.DataFrame(fArray)

    df1 = pd.DataFrame({
        'code': code,
        'report_date': ndf['enddate'].map(lambda x: pd.to_datetime(x).strftime("%Y-%m-%d")),
        'rank': ndf['rank2'],
        'holder_name': ndf['shholdername'],
        'holder_code': ndf['shholdercode'],
        'amount': ndf['holderamt'],
        'rate': ndf['holderrto'],
        'holder_nature': ndf['shholdertype'],
        'holder_type': ndf['shholdernature'],
        'holder_parent': ndf['shholdername'].map(lambda x: x.split('-')[0])

    })

    sql = "select max(report_date) from stock_holder where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()

    if (s_date == None):
        s_date = dbs.getStock(code).launch_date  # 取上市日期

    def convertDate(x):
        return pd.to_datetime(x).date()
    df2 = df1[df1['report_date'].apply(convertDate) > s_date]

    if not df2.empty:
        df2.to_sql('stock_holder', db.engine, if_exists='append', index=False, chunksize=1000)
        #更新汇总信息
        #refreshStockHolderSum(df2,code)

    latest_report = df1['report_date'].max()
    #更新stock情况
    st = dbs.getStock(code)
    st.latest_report = latest_report
    st.holder_updated_time = datetime.now()
    db.session.flush()
    app.logger.info(code +' update done. the latest report date is:' + latest_report)


#近期持股情况比较
def getStockHolder(code,report_date,direction):
    sql = "select max(report_date) from stock_holder where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    _max_date = resultProxy.scalar()
    if report_date == '':
        if (_max_date == None):
            _max_date = dbs.getStock(code).launch_date  # 取上市日期
        _next_date = pd.to_datetime(_max_date)
    else:
        _next_date = pd.to_datetime(report_date)

    if direction == 'next':
        if (_next_date.date()-_max_date).days <= 0:
            _next_date = QuarterEnd().rollforward(_next_date + DateOffset(days=1))
    elif direction == 'pre':
        _next_date = QuarterEnd().rollback(_next_date - DateOffset(days=1))

    submit_date = QuarterEnd().rollback(_next_date - DateOffset(days=1))

    app.logger.debug('query holder data from ' + submit_date.strftime('%Y-%m-%d') +' to '+ _next_date.strftime('%Y-%m-%d'))

    hdf = pd.read_sql_query("select id, code,report_date,holder_type,holder_name,holder_code,rate,amount \
                                from stock_holder where code=%(name)s and report_date>=%(submit_date)s and report_date<=%(report_date)s \
                                order by report_date desc,rank asc", db.engine, \
                            params={'name': code, 'submit_date': submit_date, 'report_date': _next_date})

    def fixHolderName(x):
        d1 = hdf[hdf['id'] == x]
        v1 = d1.get('holder_code').item()
        v2 = d1.get('holder_name').item()
        if v1 == None:  # 空值判断
            return v2
        else:
            return v1

    hdf['holder_name_new'] = hdf['id'].apply(fixHolderName)

    t2_df = hdf[:10]
    t3_df = hdf[10:20]
    m1_df = pd.merge(t2_df, t3_df, how='outer', on='holder_name_new')

    def getReportDate(x, attri):
        d1 = m1_df[m1_df['holder_name_new'] == x]
        v1 = d1.get(attri + '_x')
        v2 = d1.get(attri + '_y')
        if v1 == None:  # 空值判断
            return v2
        else:
            return v1

    def getValue(x, attri):
        d1 = m1_df[m1_df['holder_name_new'] == x]
        v1 = d1.get(attri + '_x')
        v2 = d1.get(attri + '_y')
        if v1.item() != v1.item():  # 空值判断
            return v2.item()
        else:
            return v1.item()

    def countVar(x):
        d1 = m1_df[m1_df['holder_name_new'] == x]
        v1 = d1.get('rate_x')
        v2 = d1.get('rate_y')
        if v1.item() != v1.item():  # 空值判断
            return '减持'
        elif v2.item() != v2.item():
            return '新进'
        elif v1.item() == v2.item():
            return '不变'
        else:
            return format(v1.item() - v2.item(), ',')

    m2_df = pd.DataFrame({
        'name': m1_df['holder_name_new'].apply(getValue, args=('holder_name',)),
        'code': m1_df['holder_name_new'].apply(getValue, args=('holder_code',)),
        'report_date': m1_df['holder_name_new'].apply(getValue, args=('report_date',)),
        'amount': m1_df['holder_name_new'].apply(getValue, args=('amount',)),
        'rate': m1_df['holder_name_new'].apply(getValue, args=('rate',)),
        'var': m1_df['holder_name_new'].apply(countVar)
    })

    return (_next_date.strftime('%Y-%m-%d'),m2_df)

#指定股东的持股历史
def getStockHolderTrack(holder_code):
    hdf = pd.read_sql_query("select code,report_date,holder_type,holder_name,rate,amount \
                                from stock_holder where holder_code=%(code)s", db.engine,\
                            params={'code': holder_code})

    bdf = pd.read_sql_query("select * from stock_basic sb ", db.engine)
    t3_df = pd.merge(hdf, bdf, on='code')

    m2_df = pd.DataFrame({
        'code': t3_df.code,
        'name': t3_df['name'],
        'report_date': t3_df.report_date,
        'amount': t3_df['amount'],
        'rate': t3_df['rate']
    })

    return m2_df

#获得机构历史持股情况
def getStockHolderHistory(code):
    hdf = pd.read_sql_query("select code,report_date,holder_type,rate\
                                from stock_holder where holder_type!='自然人股' and code=%(name)s", db.engine,
                            params={'name': code})
    gdf = hdf.groupby(['report_date'])
    size_agdf = gdf['rate'].agg({'size': np.size})
    size_agdf = size_agdf.sort_index(ascending=False)

    sum_agdf = gdf['rate'].agg({'sum': np.sum})
    sum_agdf = sum_agdf.sort_index(ascending=False)

    return (size_agdf,sum_agdf)

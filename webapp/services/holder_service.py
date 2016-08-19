# -*- coding: utf-8 -*-
import sys
from bs4 import  BeautifulSoup,BeautifulStoneSoup
from sqlalchemy import *
from flask import g
import pandas as pd
import numpy as np
from flask import current_app as app
from webapp.services import db,db_service as dbs
from webapp.models import MyStock,Stock,data_item,Comment,FinanceBasic
import json,random,time
from pandas.tseries.offsets import *
from datetime import datetime

group_stockholder_rate = None

def getLatestStockHolder():
    global group_stockholder_rate
    if group_stockholder_rate is None:
        hdf = pd.read_sql_query("select code,report_date,holder_type,holder_name,rate\
                                   from stock_holder order by report_date desc", db.engine)
        group_stockholder_rate = hdf.groupby(['code']).head(10)
        #group_stockholder_rate = gdf[gdf['holder_type'] != '自然人股']
    return group_stockholder_rate

def refreshStockHolder():
    #获得所有股票代码列表
    stocks = db.session.query(Stock).filter(and_(Stock.latest_report < '2016-03-31',Stock.launch_date < '2016-03-31')).limit(200).all()
    #stocks = db.session.query(Stock).all()
    for st in stocks:
        app.logger.info('checking stock holder for:' + st.code)
        latest_report = updateStockHolder(st.code)
        st.latest_report = latest_report
        db.session.flush()

def refreshStockHolderSum():
    gdf = getLatestStockHolder()
    agdf = gdf[gdf['holder_type'] != '自然人股']
    a1gdf = agdf.groupby(['code'])

    t1_gdf = a1gdf['rate'].agg({'size': np.size})
    t1_gdf = t1_gdf.reset_index()
    t2_gdf = a1gdf['rate'].agg({'sum': np.sum})
    t2_gdf = t2_gdf.reset_index()
    t3_gdf = gdf.drop_duplicates(['report_date','code'])

    t1_df = pd.merge(t3_gdf, t2_gdf, on='code')
    t2_df = pd.merge(t3_gdf, t1_gdf, on='code')

    bdf = pd.read_sql_query("select * from stock_basic sb ", db.engine)
    t3_df = pd.merge(t3_gdf, bdf, on='code')

    m2_df = pd.DataFrame({
        'code': t1_df.code,
        'name': t3_df['name'],
        'report_date': t1_df.report_date,
        'count': t2_df['size'],
        'sum': t1_df['sum']
    })
    m2_df.to_sql('stock_holder_sum', db.engine, if_exists='append', index=False, chunksize=1000)

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

#近期持股情况比较
def getStockHolder(code):
    hdf = pd.read_sql_query("select code,report_date,holder_type,holder_name,rate,amount \
                                from stock_holder where code=%(name)s order by report_date desc", db.engine,\
                            params={'name': code})
    t2_df = hdf[:10]
    t3_df = hdf[10:20]
    m1_df = pd.merge(t2_df, t3_df, how='outer', on='holder_name')

    def getReportDate(x, attri):
        d1 = m1_df[m1_df['holder_name'] == x]
        v1 = d1.get(attri + '_x')
        v2 = d1.get(attri + '_y')
        if v1 == None:  # 空值判断
            return v2
        else:
            return v1

    def getValue(x, attri):
        d1 = m1_df[m1_df['holder_name'] == x]
        v1 = d1.get(attri + '_x')
        v2 = d1.get(attri + '_y')
        if v1.item() != v1.item():  # 空值判断
            return v2.item()
        else:
            return v1.item()

    def countVar(x):
        d1 = m1_df[m1_df['holder_name'] == x]
        v1 = d1.get('amount_x')
        v2 = d1.get('amount_y')
        if v1.item() != v1.item():  # 空值判断
            return '减持'
        elif v2.item() != v2.item():
            return '新进'
        elif v1.item() == v2.item():
            return '不变'
        else:
            return format(v1.item() - v2.item(), ',')

    m2_df = pd.DataFrame({
        'name': m1_df.holder_name,
        'report_date': m1_df['holder_name'].apply(getValue, args=('report_date',)),
        'amount': m1_df['holder_name'].apply(getValue, args=('amount',)),
        'rate': m1_df['holder_name'].apply(getValue, args=('rate',)),
        'var': m1_df['holder_name'].apply(countVar)
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

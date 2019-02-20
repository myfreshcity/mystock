# -*- coding: utf-8 -*-
import sys

import requests
from bs4 import  BeautifulSoup,BeautifulStoneSoup
from sqlalchemy import *
from flask import g
import pandas as pd
import numpy as np
from flask import current_app as app
from webapp.services import db,db_service as dbs
from webapp.models import Stock,Comment,FinanceBasic
import json,random,time
import http.cookiejar
from pandas.tseries.offsets import *
from datetime import datetime
import urllib2,re,html5lib

group_stockholder_rate = None


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
    stocks = db.session.query(Stock).\
        filter(or_(Stock.holder_updated_time == None,Stock.holder_updated_time < start_date)).\
        filter_by(flag=0).all()
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
    bdf = pd.read_sql_query("select * from stock_basic where code =%(code)s and flag=0", db.engine, params={'code': code})
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

    bdf = dbs.get_global_basic_data().reset_index()
    t7_df = pd.merge(t6_df, bdf, on='code')
    return t7_df

def getStockHolderFromNet(code):
    import re
    url = "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CirculateStockHolder/stockid/" + code + ".phtml"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    session = requests.session()
    feeddata = session.get(url, headers=headers)
    soup = BeautifulSoup(feeddata.content, "html5lib")
    paper_name = soup.html.body.find(id="CirculateShareholderTable").tbody.find_all('tr')

    report_date = []
    holder_name = []
    holder_code = []
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
                    rateStr = t[3].div.string
                    # 新浪特殊数据处理
                    if rateStr:
                        rateArray = re.findall("^[0-9]*\.?[0-9]{0,2}", rateStr)
                        rate.append(rateArray[0])
                    else:
                        rate.append('1')
                    holder_type.append(t[4].div.string)
                    hcode = re.sub(u"[\–\-\－\：\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）]+", "", hname)
                    holder_code.append(hcode)
                    hname_array = re.compile(u'－|-').split(hname)
                    holder_parent.append(hname_array[0])
    df1 = pd.DataFrame({
        'code': code,
        'report_date': report_date,
        'holder_name': holder_name,
        'holder_code': holder_code,
        'amount': amount,
        'rate': rate,
        'holder_type': holder_type,
        'holder_parent': holder_parent
    })
    return {'code': code, 'data': df1}

def updateStockHolder(data):
    code = data['code']
    df1 = data['data']

    st = dbs.getStock(code)
    sql = "select max(report_date) from stock_holder where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()

    if (s_date == None):
        s_date = st.launch_date  # 取上市日期

    def convertDate(x):
        return pd.to_datetime(x).date()
    df2 = df1[df1['report_date'].apply(convertDate) > s_date]

    if not df2.empty:
        df2.to_sql('stock_holder', db.engine, if_exists='append', index=False, chunksize=1000)
        #更新汇总信息
        #refreshStockHolderSum(df2,code)

    latest_report = df1['report_date'].max()
    #更新stock情况

    st.latest_report = latest_report
    st.holder_updated_time = datetime.now()
    db.session.flush()
    #app.logger.info(code +' update done. the latest report date is:' + latest_report)


def getLatestStockHolder(code):
    today = datetime.now()
    dt_2 = QuarterEnd().rollback(today - DateOffset(years=3))
    submit_date = dt_2.date()

    hdf = pd.read_sql_query("select id, code,report_date,holder_type,holder_name,holder_code,rate,amount \
                                from stock_holder where code=%(name)s and report_date>=%(submit_date)s \
                                order by report_date asc,rate desc", db.engine, \
                            params={'name': code, 'submit_date': submit_date.strftime('%Y-%m-%d')})

    grouped = hdf.groupby('report_date')
    pre_group = pd.DataFrame()

    def getValue(x, attri):
        d1 = m1_df[m1_df['holder_code'] == x]
        v1 = d1.get(attri + '_x')
        v2 = d1.get(attri + '_y')
        if v1.item() != v1.item():  # 空值判断
            return v2.item()
        else:
            return v1.item()

    def countVar(x):
        d1 = m1_df[m1_df['holder_code'] == x]
        v1 = d1.get('rate_x')
        v2 = d1.get('rate_y')
        # 补充精度不准问题
        v3 = d1.get('amount_x')
        v4 = d1.get('amount_y')


        if v1.item() != v1.item():  # 空值判断
            return '-'
        elif v2.item() != v2.item():
            return '+'
        elif (v1.item() == v2.item()) or (v3.item() == v4.item()):
            return '0'
        else:
            return format(v1.item() - v2.item(), ',')

    result = []

    for name, group in grouped:
        if not pre_group.empty:
            m1_df = pd.merge(group, pre_group, on='holder_code', how='outer')
            m2_df = pd.DataFrame({
                'name': m1_df['holder_code'].apply(getValue, args=('holder_name',)),
                'code': m1_df['holder_code'],
                'report_date': name,
                'amount': m1_df['holder_code'].apply(getValue, args=('amount',)),
                'rate': m1_df['holder_code'].apply(getValue, args=('rate',)),
                'var': m1_df['holder_code'].apply(countVar)
            })
            result.append({'report_date': name, 'data': m2_df})

        pre_group = group  # 重新设置比较列表

    return result

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
                                order by report_date desc,amount desc", db.engine, \
                            params={'name': code, 'submit_date': submit_date.strftime('%Y-%m-%d'), 'report_date': _next_date.strftime('%Y-%m-%d')})

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

    bdf = dbs.get_global_basic_data().reset_index()
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

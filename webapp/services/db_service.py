# -*- coding: utf-8 -*-
import sys
from sqlalchemy import create_engine,text
import pandas as pd
import numpy as np
from flask import current_app as app
from webapp.services import db
from webapp.models import MyStock,Stock,DataItem,Comment,RelationStock
import json

from pandas.tseries.offsets import *
from datetime import datetime
import urllib2,re

from pymongo import MongoClient
client = MongoClient('127.0.0.1',27017)

def getItemDates():
    items = DataItem.query.all()
    return items

def getStocks():
    df = pd.read_sql_query("select code,name from stock_basic",db.engine,index_col='code')
    return df

#获取当前股价
def getPerStockPrice(df):
    q_st_codes = []
    for index, row in df.iterrows():
        q_st_codes.append(row['market'] + index)

    str = ','.join(q_st_codes)
    try:
        url = "http://hq.sinajs.cn/list=" + str
        app.logger.info('query latest stock bill url is:' + url)
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req).read()
    except:
        res_data = ''

    st_valus = []
    st_codes = []
    for st in q_st_codes:
        regex = r'var hq_str_' + st + '="(.*)".*'
        match = re.search(regex, res_data, re.M)
        if match:
            match = match.group(1)
            trade_data = match.split(',')
            v = round(float(trade_data[3]), 2)
        else:
            v = None
        st_valus.append(v)
        st_codes.append(st[2:])
    return pd.DataFrame(st_valus, index=st_codes,columns=['price'])

def getPerStockPriceV2():
    tdf = pd.read_sql_query("select code,trade_date,close,volume,t_cap,m_cap\
                                from stock_trade_data", db.engine)
    df = tdf.groupby([tdf['code']]).first()
    return df

#获取每股收益,每股净资产,每股经营现金流
def getPerStockRevenue():
    df = pd.read_sql_query("select code,report_type,mgsy_ttm,mgjzc,mgjyxjl_ttm from stock_finance_basic", db.engine)
    i = df['report_type'].map(lambda x: pd.to_datetime(x))
    df = df.set_index(i)
    df = df.sort_index(ascending=False)

    df = df.groupby([df['code']]).first()
    df = df.reset_index()
    return df.set_index(df['code'])


#获取每季度现金变化情况
def get_cash_rate(code):
    valueDf = get_revenue_df(code)
    def getValue(x):
        # x = pd.to_datetime(x).date()
        return round(valueDf.loc[x].get('jyjxjl') * 100 / valueDf.loc[x].get('zyysr'), 2)
    cash_rate = pd.Series(valueDf['report_type'].apply(getValue), name='cash_rate')
    cash_rate_var = pd.Series(cash_rate.pct_change(periods=-4), name='cash_rate_var')
    df1 = pd.concat([cash_rate, cash_rate_var], axis=1)
    return df1

#获取每季度营收
#pType 0-按报告期，1-按单季度
def get_quarter_stock_revenue(code,quarter=None,pType=0):
    df = get_revenue_df(code,quarter==0,pType)
    if quarter is None:
        quarter = df.index.max().quarter
    if quarter > 0:
        tdate = df.index[df.index.quarter == quarter]
        df = df.iloc[df.index.isin(tdate)]
    return df

#获取营收df
def get_revenue_df(code,compare_last_period=False,pType=0):
    def pct_change_fix(x, attri): #解决基准值为负值的情况
        dt_1 = x
        v1 = df[df['report_type'] == dt_1].get(attri)
        if compare_last_period: #环比计算
            dt_2 = QuarterEnd().rollback(dt_1 - DateOffset(days=1)) #上一期
            dt_2 = dt_2.date()
            v2 = df[df['report_type'] == dt_2].get(attri)
            if v2.empty:
                return None
            else:
                return (float(v1) - float(v2)) / abs(float(v2))
        else: #同比计算
            dt_2 = (dt_1 - DateOffset(months=12)).date()  # 去年同期
            v2 = df[df['report_type'] == dt_2].get(attri)
            if v2.empty:
                return None
            else:
                return (float(v1) - float(v2)) / abs(float(v2))

    df = pd.read_sql_query("select * from stock_finance_data where code=%(name)s order by report_type",
                           db.engine, params={'name': code})
    if pType == 0:
        zyysr_ttm = pd.Series(df['report_type'].apply(pct_change_fix, args=('zyysr',)), name='zyysr_grow_rate')
        jlr_ttm = pd.Series(df['report_type'].apply(pct_change_fix, args=('jlr',)), name='jlr_grow_rate')
        yylr_ttm = pd.Series(df['report_type'].apply(pct_change_fix, args=('yylr',)), name='yylr_grow_rate')
        jyjxjl_ttm = pd.Series(df['report_type'].apply(pct_change_fix, args=('jyjxjl',)), name='jyjxjl_grow_rate')
    else:
        zyysr_ttm = pd.Series(df['report_type'].apply(pct_change_fix, args=('zyysr_qt',)), name='zyysr_grow_rate')
        jlr_ttm = pd.Series(df['report_type'].apply(pct_change_fix, args=('jlr_qt',)), name='jlr_grow_rate')
        yylr_ttm = pd.Series(df['report_type'].apply(pct_change_fix, args=('yylr_qt',)), name='yylr_grow_rate')
        jyjxjl_ttm = pd.Series(df['report_type'].apply(pct_change_fix, args=('jyjxjl_qt',)), name='jyjxjl_grow_rate')

    df1 = pd.concat([df, zyysr_ttm, jlr_ttm, yylr_ttm, jyjxjl_ttm], axis=1)

    i = df['report_type'].map(lambda x: pd.to_datetime(x))
    df2 = df1.set_index(i)
    df2 = df2.sort_index(ascending=False).fillna(0)
    return df2

#历史估值(新)
def getStockValuationN(code,peroid):
    #获取收益数据
    df = pd.read_sql_query(
        "select code,report_type,zyysr,zyysr_ttm,kjlr,jlr,jlr_ttm,jyjxjl,jyjxjl_ttm,xjjze,roe,gdqy \
        from stock_finance_data \
        where code=%(name)s",
        db.engine, params={'name': code})
    i = df['report_type'].map(lambda x: pd.to_datetime(x))
    df3 = df.set_index(i)
    sdf = df3.sort_index(ascending=False)

    # 获取交易数据
    tdf = pd.read_sql_query("select "
                            "trade_date,close,volume,t_cap,m_cap "
                            "from stock_trade_data "
                            "where code=%(name)s ",
                            db.engine, params={'name': code}).dropna(axis=0)
    i = tdf['trade_date'].map(lambda x: pd.to_datetime(x))
    tdf = tdf.set_index(i)
    tdf = tdf.sort_index(ascending=False)
    gdf = tdf.groupby([pd.TimeGrouper(freq='M')])
    agdf = gdf['trade_date'].agg({'max': np.max})
    tdf = tdf.iloc[tdf.index.isin(agdf['max'])]

    def getRevence(x, attri):
        dt = x
        sdate = dt - DateOffset(days=1) + QuarterEnd() #返回所在日期的季度数据
        mg_val = sdf[sdf.index == sdate].get(attri)
        return None if mg_val.empty else mg_val.values[0] * 10000

    def getReportType(x):
        dt = pd.to_datetime(x)
        sdate = dt + QuarterEnd()
        return sdate

    df = pd.DataFrame({
        'trade_date': tdf['trade_date'],
        'close': tdf['close'],
        't_cap': tdf['t_cap'],
        'm_cap': tdf['m_cap'],
        'zyysr': tdf['trade_date'].apply(getRevence, args=('zyysr',)),
        'zyysr_ttm': tdf['trade_date'].apply(getRevence, args=('zyysr_ttm',)),
        'kjlr': tdf['trade_date'].apply(getRevence, args=('kjlr',)),
        'jlr': tdf['trade_date'].apply(getRevence, args=('jlr',)),
        'jlr_ttm': tdf['trade_date'].apply(getRevence, args=('jlr_ttm',)),
        'jyjxjl': tdf['trade_date'].apply(getRevence, args=('jyjxjl',)),
        'jyjxjl_ttm': tdf['trade_date'].apply(getRevence, args=('jyjxjl_ttm',)),
        'gdqy':tdf['trade_date'].apply(getRevence, args=('gdqy',)),
        'code': code
    })
    df = df.fillna(method='bfill')

    #df.set_index('trade_date')
    if peroid>0:
        df = df.head(peroid*12)
    return df

def getStockData(code):
    cursor = client.mystock.hisdata.find({"cd": '002337'}, ["date", "close", "volume"])
    reader = pd.read_json()
    loop = True
    chunkSize = 100000
    chunks = []
    while loop:
        try:
            chunk = reader.get_chunk(chunkSize)
            chunks.append(chunk)
        except StopIteration:
            loop = False
            print "Iteration is stopped."
    df = pd.concat(chunks, ignore_index=True)

    pd.DataFrame(list(cursor))
    return df

def getStock(code):
    stock = db.session.query(Stock).filter_by(code = code).first()
    return stock

def getMyStock(code):
    stock = db.session.query(MyStock).filter_by(code = code[2:].strip()).first()
    return stock

def addMystock(code):
    code = code.strip()
    if len(code) != 6:
        return "'"+code+"'无效,长度应为6位"
    mystock = db.session.query(MyStock).filter_by(code = code).first()
    if not mystock:
        #stock = db.session.query(Stock).filter(Stock.code.like('%'+code)).first()
        #stock = Stock.find_by_code(code)
        market = 'sh' if code[0:2]=='60' else 'sz'
        code = code.strip()
        url = "http://hq.sinajs.cn/list=" + market + code
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req).read()
        match = re.search(r'".*"', res_data).group(0)
        trade_data = match.split(',')
        name =  unicode(trade_data[0],'gbk')[1:]
        #trade_data[0].decode('gbk').encode('utf-8')
        if name:
            mystock = MyStock(code,name,market)
            db.session.add(mystock)
            return None
    else:
        return "'"+code+"'股票已存在"

def addRelationStock(mcode,scode):
    code = scode.strip()
    if len(code) != 6:
        return "'"+code+"'无效,长度应为6位"
    if scode == mcode:
        return "相关股票和母股票相同"

    rstock1 = db.session.query(RelationStock).filter_by(main_stock = mcode,relation_stock = scode).first()
    rstock2 = db.session.query(RelationStock).filter_by(relation_stock=mcode, main_stock=scode).first()

    if (not rstock1) and (not rstock2):
        rstock = RelationStock(mcode,scode)
        db.session.add(rstock)
        rstock = RelationStock(scode,mcode)
        db.session.add(rstock)
        return None
    else:
        return "'"+code+"'股票已存在"

def delRelationStock(mcode,scode):
    mystock = db.session.query(RelationStock).filter_by(main_stock = mcode,relation_stock = scode).first()
    db.session.delete(mystock)
    mystock = db.session.query(RelationStock).filter_by(relation_stock=mcode, main_stock=scode).first()
    db.session.delete(mystock)
    return db.session.flush()

def removeMystock(code):
    mystock = db.session.query(MyStock).filter_by(code = code).first()
    mystock.flag = '1'
    return db.session.flush()

def hardRemoveMystock(code):
    mystock = db.session.query(MyStock).filter_by(code = code).first()
    db.session.delete(mystock)
    return db.session.flush()

def rollbackStock(code):
    mystock = db.session.query(MyStock).filter_by(code = code).first()
    mystock.flag = '0'
    return db.session.flush()

def updateStockInPrice(code,price,in_date):
    mystock = db.session.query(MyStock).filter_by(code = code).first()
    mystock.in_price = price
    mystock.in_date = in_date
    return db.session.flush()

def updateStockTag(code,tag):
    mystock = db.session.query(MyStock).filter_by(code = code).first()
    mystock.tag = tag
    return db.session.flush()

def updateStock(code,desc,grow_type):
    st = db.session.query(Stock).filter_by(code=code).first()
    st.desc = desc
    st.grow_type = grow_type
    return db.session.flush()

def addComment(code,content):
    #stock = db.session.query(Stock).filter(Stock.code.like('%'+code)).first()
    #stock = Stock.find_by_code(code)
    comment = Comment(code,content)
    comment.created_time = datetime.now()
    db.session.add(comment)
    return comment

def updateComment(cid,content):
    comment = db.session.query(Comment).filter_by(id = cid).first()
    comment.content = content
    return comment

def queryComment(code):
    #mystock = db.session.query(MyStock).filter_by(code = code).first()
    return Comment.find_by_code(code).all()

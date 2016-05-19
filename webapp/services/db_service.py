# -*- coding: utf-8 -*-
import sys
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from flask import current_app as app
from webapp.services import db
from webapp.models import MyStock,Stock,data_item,Comment
import tushare as ts
import json
from datetime import datetime
import urllib2,re

from pymongo import MongoClient
client = MongoClient('127.0.0.1',27017)

def getUserBill(year,month):
    df = pd.read_sql_query("select money,time from invest where status in ('还款中', '完成', '投标成功') and  year(time)="+year+" and month(time)="+month+"",db.engine,index_col='time')
    gdf = df.groupby([pd.TimeGrouper(freq='M')])
    agdf = gdf['money'].agg([np.sum, np.size])
    return agdf

def getUsers():
    url = 'http://s3.amazonaws.com/assets.datacamp.com/course/dasi/present.txt'
    df = pd.read_table(url, sep=' ')
    return df

def getLatestTradeData():
    #df = ts.get_tick_data('600848', date='2014-12-22')
    #df.to_sql('tick_data', db.engine, if_exists='append')
    df = ts.get_h_data('002337', autype='hfq')
    df['code'] = '002337'
    df['date'] = df.index
    client.mystock.hisdata.insert_many(json.loads(df.to_json(orient='records',date_unit='s')))
    return df

def getLatestFinaceData():
    df = ts.get_tick_data('600848', date='2014-12-22')
    client.db.tickdata.insert(json.loads(df.to_json(orient='records')))
    return df

def getStocks():
    df = pd.read_sql_query("select code,name,zsz from stocks",db.engine,index_col='code')
    return df

def getMyStocks(flag):
    df = pd.read_sql_query("select code,name,market from my_stocks where flag=%(flag)s", db.engine, \
                           index_col='code', params={'flag': flag})
    df1 = getPerStockPrice(df)
    df2 = getPerStockRevenue()
    df3 = pd.concat([df1,df2],axis=1,join='inner')
    df = df.reset_index()
    df4 = pd.merge(df, df3, how='left')
    return df4

#获取当前股价
def getPerStockPrice(df):
    q_st_codes = []
    for index, row in df.iterrows():
        q_st_codes.append(row['market'] + index)

    str = ','.join(q_st_codes)
    url = "http://hq.sinajs.cn/list=" + str
    req = urllib2.Request(url)
    res_data = urllib2.urlopen(req).read()

    st_valus = []
    st_codes = []
    for st in q_st_codes:
        regex = r'var hq_str_' + st + '="(.*)".*'
        match = re.search(regex, res_data, re.M).group(1)
        trade_data = match.split(',')
        st_valus.append(round(float(trade_data[3]), 2))
        st_codes.append(st[2:])
    return pd.DataFrame(st_valus, index=st_codes,columns=['price'])


#获取每股收益,每股净资产,每股经营现金流
def getPerStockRevenue():
    df = pd.read_sql_query("select code,report_type,mgsy_ttm,mgjzc,mgjyxjl_ttm from stock_finance_basic", db.engine)
    i = df['report_type'].map(lambda x: pd.to_datetime(x))
    df = df.set_index(i)
    df = df.sort_index(ascending=False)

    df = df.groupby([df['code']]).first()
    df = df.reset_index()
    return df.set_index(df['code'])


#年度营收
def getStockRevenue(code):
    df = pd.read_sql_query("select yysr,yylr as jlr,jyjxjl,zfz/zzc*100 as drate,report_type from stocks where year(report_type)>=2010 and month(report_type)= 12 and code=%(name)s",
                           db.engine,index_col='report_type',params={'name':code})
    #df.index = pd.to_datetime(df['report_type'])
    return df

#历史估值
def getStockValuation(code, category):
    if category == 'quart':
        df = pd.read_sql_query("select "
                               "close,mgsy_ttm,mgyysr_ttm,mgjyxjl_ttm,close/mgsy_ttm as pe,close/mgyysr_ttm as ps,close/mgjyxjl_ttm as pcf,report_type "
                               "from stocks "
                               "where year(report_type)>=2005 and code=%(name)s",
                               db.engine, index_col='report_type', params={'name': code}).dropna(axis=0)
    else:
        df = pd.read_sql_query("select "
                               "close,mgsy_ttm,mgyysr_ttm,mgjyxjl_ttm,close/mgsy_ttm as pe,close/mgyysr_ttm as ps,close/mgjyxjl_ttm as pcf,report_type "
                               "from stocks "
                               "where year(report_type)>=2005 and month(report_type)= 12 and code=%(name)s",
                               db.engine, index_col='report_type', params={'name': code}).dropna(axis=0)
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

def getUsersdzc(year,month):
    df = pd.read_sql_query("select id,register_time from user WHERE year(register_time)="+year+" and month(register_time)="+month+"",db.engine,index_col='register_time')
    gdf = df.groupby([pd.TimeGrouper(freq='D')])
    agdf = gdf['id'].agg([np.size])
    return agdf

def getUsersmzc(year,month):
	df = pd.read_sql_query("select id,register_time from user WHERE year(register_time)="+year+" and month(register_time)="+month+"",db.engine,index_col='register_time')
	gdf = df.groupby([pd.TimeGrouper(freq='M')])
	agdf = gdf['id'].agg([np.size])
	return agdf

def getItemDates():
    items = data_item.DataItem.query.all()
    return items

def getStock(code):
    stock = db.session.query(Stock).filter_by(code = code).first()
    return stock

def getMyStock(code):
    stock = db.session.query(MyStock).filter_by(code = code[2:].strip()).first()
    return stock

def addMystock(code):
    if len(code) != 8:
        return "'"+code+"'无效,长度应为8位,以sz/sh加数字标示"
    mystock = db.session.query(MyStock).filter_by(code = code[2:].strip()).first()
    if not mystock:
        #stock = db.session.query(Stock).filter(Stock.code.like('%'+code)).first()
        #stock = Stock.find_by_code(code)
        market = code[0:2].strip().lower()
        code = code[2:].strip()
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

def removeMystock(code):
    mystock = db.session.query(MyStock).filter_by(code = code).first()
    mystock.flag = '1'
    return db.session.flush()

def rollbackStock(code):
    mystock = db.session.query(MyStock).filter_by(code = code).first()
    mystock.flag = '0'
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

# -*- coding: utf-8 -*-
import sys
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from flask import current_app as app
from webapp.services import db
from webapp.models import MyStock,Stock,data_item
import tushare as ts
import json

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

def getMyStocks():
    items = MyStock.query.all()
    return items

#年度营收
def getStockRevenue(code):
    df = pd.read_sql_query("select yysr,yylr as jlr,jyjxjl,zfz/zzc*100 as drate,report_type from stocks where year(report_type)>=2005 and month(report_type)= 12 and code=%(name)s",
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

def addMystock(code):
    stock = db.session.query(Stock).filter(Stock.code.like('%'+code)).first()
    market = stock.code[0:2]
    code = stock.code[2:]
    mystock = MyStock(code,stock.name,market)
    db.session.add(mystock)
    return stock

def removeMystock(code):
    mystock = db.session.query(MyStock).filter_by(code = code).first()
    return db.session.delete(mystock)

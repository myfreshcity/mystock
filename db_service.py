# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

engine = create_engine('mysql+mysqldb://root:root@127.0.0.1:3306/mystock?charset=utf8mb4')

def getUserBill(year,month):
    df = pd.read_sql_query("select money,time from invest where status in ('还款中', '完成', '投标成功') and  year(time)="+year+" and month(time)="+month+"",engine,index_col='time')
    gdf = df.groupby([pd.TimeGrouper(freq='M')])
    agdf = gdf['money'].agg([np.sum, np.size])
    return agdf


def getUserBillByDate():
    df = pd.read_sql_query("select money,time from invest where status in ('还款中', '完成', '投标成功')",engine,parse_dates=date,index_col='time')
    gdf = df.groupby([pd.TimeGrouper(freq='M')])
    agdf = gdf['money'].agg([np.sum, np.size])
    return agdf


def getUsers():
    url = 'http://s3.amazonaws.com/assets.datacamp.com/course/dasi/present.txt'
    df = pd.read_table(url, sep=' ')
    return df

def getUsersdzc(year,month):
    df = pd.read_sql_query("select id,register_time from user WHERE year(register_time)="+year+" and month(register_time)="+month+"",engine,index_col='register_time')
    gdf = df.groupby([pd.TimeGrouper(freq='D')])
    agdf = gdf['id'].agg([np.size])
    return agdf

def getUsersmzc(year,month):
	df = pd.read_sql_query("select id,register_time from user WHERE year(register_time)="+year+" and month(register_time)="+month+"",engine,index_col='register_time')
	gdf = df.groupby([pd.TimeGrouper(freq='M')])
	agdf = gdf['id'].agg([np.size])
	return agdf

# -*- coding: utf-8 -*-
import sys
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from webapp.services import db

def getUserBill(year,month):
    df = pd.read_sql_query("select money,time from invest where status in ('还款中', '完成', '投标成功') and  year(time)="+year+" and month(time)="+month+"",db.engine,index_col='time')
    gdf = df.groupby([pd.TimeGrouper(freq='M')])
    agdf = gdf['money'].agg([np.sum, np.size])
    return agdf

def getUsers():
    url = 'http://s3.amazonaws.com/assets.datacamp.com/course/dasi/present.txt'
    df = pd.read_table(url, sep=' ')
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

class DataItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    update_time = db.Column(db.DateTime)

    def __init__(self, name, update_time):
        self.name = name
        self.update_time = update_time

    def __repr__(self):
        return '<User %r>' % self.name

def getItemDate():
    items = DataItem.query.all()
    return items

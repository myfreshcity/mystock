# -*- coding: utf-8 -*-
import sys

#网易数据来源
import traceback

import pandas as pd
from pandas.tseries.offsets import *
from sqlalchemy import text
import numpy as np

from webapp.services import db, db_service as dbs
from flask import current_app as app
from datetime import datetime

def getFinanceDataFromNet(code):
    url = 'http://quotes.money.163.com/service/zycwzb_' + code + '.html?type=report'
    return pd.read_csv(url)

def updateFinanceData(stock,tdf):
    code = stock.code
    # 获得开始日期
    sql = "select max(report_type) from stock_finance_data where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        s_date = stock.launch_date  # 取上市日期
    s_date = max(s_date, pd.to_datetime('2000-01-01').date())
    tdf = tdf.iloc[:, 1:].dropna(axis=1).T.reset_index()


    def fixNaN(x):
        return 1 if (x == '--' or x == '0' or x != x or x == '' or x == None) else x

    def fixJlr(x):  # 扣非净利润计算
        dt = pd.to_datetime(x)
        s_dt = tdf[tdf['index'] == dt.strftime('%Y-%m-%d')]
        x = s_dt.get(10).any()
        y = s_dt.get(9).any()

        v1 = y if (x == '--' or x == '0' or x != x or x == '' or x is None) else x
        v2 = '1' if (v1 == '--' or v1 == '0' or v1 != v1 or v1 == '' or v1 is None) else v1
        return v2

    def getRevence(x, attri):
        dt = pd.to_datetime(x)
        s_dt = tdf[tdf['index'] == dt.strftime('%Y-%m-%d')]
        lastYearEnd = YearEnd().rollback(dt)  # 去年年底
        s_lye = tdf[tdf['index'] == lastYearEnd.strftime('%Y-%m-%d')]
        lastYearQuart = dt - DateOffset(months=12)  # 去年同期
        s_lyq = tdf[tdf['index'] == lastYearQuart.strftime('%Y-%m-%d')]
        #app.logger.debug(
        #    dt.strftime('%Y-%m-%d') + ':' + lastYearEnd.strftime('%Y-%m-%d') + ':' + lastYearQuart.strftime(
        #        '%Y-%m-%d'))
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
            v4 = int(v1) + (int(v2) - int(v3))
            return 1 if v4==0 else v4
        except Exception, ex:
            #app.logger.error(ex)
            return 1

    def getQuarterRevence(x, attri):
        dt = pd.to_datetime(x)
        s_dt = tdf[tdf['index'] == dt.strftime('%Y-%m-%d')]
        v1 = s_dt.get(attri)

        lastQuart = QuarterEnd().rollback(dt - DateOffset(days=1))  # 上一期
        s_lq = tdf[tdf['index'] == lastQuart.strftime('%Y-%m-%d')]

        if dt.quarter != 1:
            v2 = s_lq.get(attri)
            if v2.empty:
                v2 = 0
        else:
            v2 = 0

        try:
            v4 = int(v1) - int(v2)
            return 1 if v4==0 else v4
        except Exception, ex:
            #msg = traceback.format_exc()
            #app.logger.error(msg)
            return 1

    if tdf['index'].max() > s_date.strftime("%Y-%m-%d"):
        tdf = pd.DataFrame({
            'report_type': tdf['index'],
            'index': tdf['index'],
            'zyysr': tdf[3].apply(fixNaN),
            'zyysr_ttm': tdf['index'].apply(getRevence, args=(3,)),
            'zyysr_qt': tdf['index'].apply(getQuarterRevence, args=(3,)),
            'zyylr': tdf[4].apply(fixNaN),
            'yylr': tdf[5].apply(fixNaN),
            'yylr_qt': tdf['index'].apply(getQuarterRevence, args=(5,)),
            'tzsy': tdf[6].apply(fixNaN),
            'ywszje': tdf[7].apply(fixNaN),
            'lrze': tdf[8].apply(fixNaN),
            'jlr': tdf[9].apply(fixNaN),
            'kf_jlr': tdf['index'].apply(fixJlr),
            'jyjxjl': tdf[11].apply(fixNaN),
            'jyjxjl_ttm': tdf['index'].apply(getRevence, args=(11,)),
            'jyjxjl_qt': tdf['index'].apply(getQuarterRevence, args=(11,)),
            'xjjze': tdf[12].apply(fixNaN),
            'xjjze_qt': tdf['index'].apply(getQuarterRevence, args=(12,)),
            'zzc': tdf[13].apply(fixNaN),
            'ldzc': tdf[14].apply(fixNaN),
            'zfz': tdf[15].apply(fixNaN),
            'ldfz': tdf[16].apply(fixNaN),
            'gdqy': tdf[17].apply(fixNaN),
            'roe': tdf[18].apply(fixNaN).map(lambda x: round(float(x),2)),
            'code': code
        })

        tdf['jlr_ttm'] = tdf['index'].apply(getRevence, args=('jlr',))
        tdf['jlr_qt'] = tdf['index'].apply(getQuarterRevence, args=('jlr',))
        #删除冗余列
        del tdf['index']

        #计算收益增长率
        df = tdf.sort_values(by='report_type',ascending=True)

        def pct_change_fix(x, attri):  # 解决基准值为负值的情况
            dt_1 = pd.to_datetime(x)
            dt_2 = (dt_1 - DateOffset(months=12)).date()  # 去年同期
            v1 = df[df['report_type'] == dt_1.strftime('%Y-%m-%d')].get(attri)
            v2 = df[df['report_type'] == dt_2.strftime('%Y-%m-%d')].get(attri)
            if v2.empty:
                return None
            else:
                v3 = (float(v1) - float(v2)) / abs(float(v2))
                return round(v3,2)

        df['jlr_rate'] = df['report_type'].apply(pct_change_fix,args=('jlr_ttm',))

        # insert new data to database
        df = df.set_index('report_type')
        sd = (s_date + DateOffset(days=1)).date().strftime('%Y-%m-%d') #排除掉之前插入的数据
        ed = df.index.max()
        edf = df.loc[sd:ed].reset_index()
        edf = edf.fillna(1)
        edf.to_sql('stock_finance_data', db.engine, if_exists='append', index=False, chunksize=1000)

def updateTradeData(stock):
    code = stock.code
    #获得开始日期
    sql = "select max(trade_date) from stock_trade_data where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        s_date = stock.launch_date #取上市日期
    s_date = max(s_date, pd.to_datetime('2000-01-01').date())
    s_date = (s_date +DateOffset(days=1)).date()  # 排除掉之前插入的数据
    e_date = datetime.now().date()

    def toInt(x):
        return int(x)

    #根据类型获取市场代码
    mc = '0' if code[:2]=='60' else '1'
    url = 'http://quotes.money.163.com/service/chddata.html?code=' + mc  + code +\
          '&start=' + s_date.strftime("%Y%m%d") + '&end=' + e_date.strftime("%Y%m%d") + '&fields=TCLOSE;VATURNOVER;TCAP;MCAP'
    #app.logger.info('query stock('+code+') trade data url is:'+url)
    try:
        tdf = pd.read_csv(url,names=['trade_date','code','name','close','volume','t_cap','m_cap'],header=0)
        if tdf.empty:
            app.logger.info('query stock(' + code + ') data is empty for :' + url)
            return
        tdf = pd.DataFrame({
            'trade_date': tdf['trade_date'],
            'close': tdf['close'],
            'volume': tdf['volume'].apply(toInt),
            't_cap': tdf['t_cap'].apply(toInt),
            'm_cap': tdf['m_cap'].apply(toInt),
            'code': code
        })
        #获取历史周数据存储
        i = tdf['trade_date'].map(lambda x: pd.to_datetime(x))
        tdf = tdf.set_index(i)
        tdf = tdf.sort_index(ascending=False)
        gdf = tdf.groupby([pd.TimeGrouper(freq='W')])
        agdf = gdf['trade_date'].agg({'max': np.max})
        df1 = tdf.iloc[tdf.index.isin(agdf['max'])]

        if not df1.empty:
            if df1['trade_date'].max() > s_date.strftime("%Y-%m-%d"):
                df1.to_sql('stock_trade_data', db.engine, if_exists='append', index=False, chunksize=1000)
    except Exception, ex:
        app.logger.error(traceback.format_exc())



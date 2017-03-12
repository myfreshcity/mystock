# -*- coding: utf-8 -*-
import sys
from sqlalchemy import create_engine,text
import pandas as pd
import numpy as np
from flask import current_app as app
from webapp.services import db
from webapp.models import *
import json

from pandas.tseries.offsets import *
from datetime import datetime
from sqlalchemy import desc
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

# 获取每季度资产负债信息
# pType 0-按报告期，1-按单季度
def get_stock_asset(code, quarter=None, pType=0):
    df = pd.read_sql_query("select * from xueqiu_finance_asset where code=%(name)s order by report_type",
                           db.engine, params={'name': code})

    f1 = lambda x: round(x, 2)
    f2 = lambda x: round(x / 10000, 2)

    df['fz_rate'] = (df['fz_all'] * 100.0 / df['zc_all']).apply(f1)
    df['sd_rate'] = ((df['ldzc_all']-df['ldzc_ch'])/ df['ldfz_all']).apply(f1)

    df['ldzc_hbzj'] = (df['ldzc_hbzj'] * 100.0 / df['ldzc_all']).apply(f1)
    df['ldzc_yspj'] = (df['ldzc_yspj'] * 100.0 / df['ldzc_all']).apply(f1)
    df['ldzc_yszk'] = (df['ldzc_yszk'] * 100.0 / df['ldzc_all']).apply(f1)
    df['ldzc_yfkx'] = (df['ldzc_yfkx'] * 100.0 / df['ldzc_all']).apply(f1)
    df['ldzc_yslx'] = (df['ldzc_yslx'] * 100.0 / df['ldzc_all']).apply(f1)
    df['ldzc_ysgl'] = (df['ldzc_ysgl'] * 100.0 / df['ldzc_all']).apply(f1)
    df['ldzc_o_ysk'] = (df['ldzc_o_ysk'] * 100.0 / df['ldzc_all']).apply(f1)
    df['ldzc_ch'] = (df['ldzc_ch'] * 100.0 / df['ldzc_all']).apply(f1)
    df['ldzc_o'] = (df['ldzc_o'] * 100.0 / df['ldzc_all']).apply(f1)
    df['ldzc_all'] = df['ldzc_all'].apply(f2)

    df['fld_jrzc'] = (df['fld_jrzc'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_dqtz'] = (df['fld_dqtz'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_ysk'] = (df['fld_ysk'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_gqtz'] = (df['fld_gqtz'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_tzfdc'] = (df['fld_tzfdc'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_gdzc'] = (df['fld_gdzc'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_zjgc'] = (df['fld_zjgc'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_gcwz'] = (df['fld_gcwz'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_gdzcql'] = (df['fld_gdzcql'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_wxzc'] = (df['fld_wxzc'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_kfzc'] = (df['fld_kfzc'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_sy'] = (df['fld_sy'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_cqtpfy'] = (df['fld_cqtpfy'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_dysds'] = (df['fld_dysds'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_other'] = (df['fld_other'] * 100.0 / df['fld_all']).apply(f1)
    df['fld_all'] = df['fld_all'].apply(f2)

    df['zc_all'] = df['zc_all'].apply(f2)

    df['ldfz_tqjk'] = (df['ldfz_tqjk'] * 100.0 / df['ldfz_all']).apply(f1)
    df['ldfz_yfpj'] = (df['ldfz_yfpj'] * 100.0 / df['ldfz_all']).apply(f1)
    df['ldfz_yfzk'] = (df['ldfz_yfzk'] * 100.0 / df['ldfz_all']).apply(f1)
    df['ldfz_yszk'] = (df['ldfz_yszk'] * 100.0 / df['ldfz_all']).apply(f1)
    df['ldfz_zgxc'] = (df['ldfz_zgxc'] * 100.0 / df['ldfz_all']).apply(f1)
    df['ldfz_yjsf'] = (df['ldfz_yjsf'] * 100.0 / df['ldfz_all']).apply(f1)
    df['ldfz_yflx'] = (df['ldfz_yflx'] * 100.0 / df['ldfz_all']).apply(f1)
    df['ldfz_yfgl'] = (df['ldfz_yfgl'] * 100.0 / df['ldfz_all']).apply(f1)
    df['ldfz_o_yfk'] = (df['ldfz_o_yfk'] * 100.0 / df['ldfz_all']).apply(f1)
    df['ldfz_ynfldfz'] = (df['ldfz_ynfldfz'] * 100.0 / df['ldfz_all']).apply(f1)
    df['ldfz_other'] = (df['ldfz_other'] * 100.0 / df['ldfz_all']).apply(f1)
    df['ldfz_all'] = df['ldfz_all'].apply(f2)

    df['fz_cqjk'] = (df['fz_cqjk'] * 100.0 / df['fz_other']).apply(f1)
    df['fz_yfzq'] = (df['fz_yfzq'] * 100.0 / df['fz_other']).apply(f1)
    df['fz_cqyfk'] = (df['fz_cqyfk'] * 100.0 / df['fz_other']).apply(f1)
    df['fz_zxyfk'] = (df['fz_zxyfk'] * 100.0 / df['fz_other']).apply(f1)
    df['fz_yjffz'] = (df['fz_yjffz'] * 100.0 / df['fz_other']).apply(f1)
    df['fz_dysy'] = (df['fz_dysy'] * 100.0 / df['fz_other']).apply(f1)
    df['fz_dysdsfz'] = (df['fz_dysdsfz'] * 100.0 / df['fz_other']).apply(f1)
    df['fz_other'] = df['fz_other'].apply(f2)

    df['fz_all'] = df['fz_all'].apply(f2)

    df['gq_sszb'] = df['gq_sszb'].apply(f2)
    df['gd_zbgj'] = df['gd_zbgj'].apply(f2)
    df['gd_yygj'] = df['gd_yygj'].apply(f2)
    df['gd_wflr'] = df['gd_wflr'].apply(f2)
    df['gd_mqy'] = df['gd_mqy'].apply(f2)
    df['gd_ssgd'] = df['gd_ssgd'].apply(f2)
    df['gd_all'] = df['gd_all'].apply(f2)


    i = df['report_type'].map(lambda x: pd.to_datetime(x))
    df = df.set_index(i)
    df = df.sort_index(ascending=False).fillna(0)

    if quarter > 0:
        tdate = df.index[df.index.quarter == quarter]
        df = df.iloc[df.index.isin(tdate)]

    return df

# 获取每季度利润信息
# pType 0-按报告期，1-按单季度
def get_stock_income(code, quarter=None, pType=0):
    df = pd.read_sql_query("select * from xueqiu_finance_income where code=%(name)s order by report_type",
                           db.engine, params={'name': code})

    f1 = lambda x: round(x, 2)
    f2 = lambda x: round(x / 10000, 2)

    df['gross_rate'] = ((df['in_yysr']-df['out_yycb']) * 100.0 / df['in_yysr']).apply(f1)
    df['sale_rate'] = ((df['in_yysr'] - df['out_yycb']- df['out_yys']- df['out_ss']- df['out_gl']- df['out_cw']) * 100.0 / df['in_yysr']).apply(f1)

    df['in_yysr'] = (df['in_yysr'] * 100.0 / df['in_all']).apply(f1)
    df['in_lx'] = (df['in_lx'] * 100.0 / df['in_all']).apply(f1)
    df['in_sxyj'] = (df['in_sxyj'] * 100.0 / df['in_all']).apply(f1)

    df['in_all'] = df['in_all'].apply(f2)

    df['out_yycb'] = (df['out_yycb'] * 100.0 / df['out_all']).apply(f1)
    df['out_lx'] = (df['out_lx'] * 100.0 / df['out_all']).apply(f1)
    df['out_sxyj'] = (df['out_sxyj'] * 100.0 / df['out_all']).apply(f1)
    df['out_yys'] = (df['out_yys'] * 100.0 / df['out_all']).apply(f1)
    df['out_ss'] = (df['out_ss'] * 100.0 / df['out_all']).apply(f1)
    df['out_gl'] = (df['out_gl'] * 100.0 / df['out_all']).apply(f1)
    df['out_cw'] = (df['out_cw'] * 100.0 / df['out_all']).apply(f1)
    df['out_zcjz'] = (df['out_zcjz'] * 100.0 / df['out_all']).apply(f1)
    df['out_gyjz'] = (df['out_gyjz'] * 100.0 / df['out_all']).apply(f1)

    df['out_all'] = df['out_all'].apply(f2)
    df['out_tzsy'] = df['out_tzsy'].apply(f2)
    df['out_lh_tzsy'] = df['out_lh_tzsy'].apply(f2)
    df['lr_all'] = df['lr_all'].apply(f2)

    df['lr_fldzccz'] = df['lr_fldzccz'].apply(f2)
    df['lr_total'] = df['lr_total'].apply(f2)
    df['lr_sdfy'] = df['lr_sdfy'].apply(f2)
    df['lr_m_net'] = (df['lr_m_net']*100/df['lr_net']).apply(f1)
    df['lr_net'] = df['lr_net'].apply(f2)

    df['lr_o_net'] = (df['lr_o_in'] - df['lr_o_out']).apply(f2)


    i = df['report_type'].map(lambda x: pd.to_datetime(x))
    df = df.set_index(i)
    df = df.sort_index(ascending=False).fillna(0)

    if quarter > 0:
        tdate = df.index[df.index.quarter == quarter]
        df = df.iloc[df.index.isin(tdate)]

    return df


# 获取每季度现金流信息
# pType 0-按报告期，1-按单季度
def get_stock_cash(code, quarter=None, pType=0):
    df = pd.read_sql_query("select * from xueqiu_finance_cash where code=%(name)s order by report_type",
                           db.engine, params={'name': code})

    f1 = lambda x: round(x, 2)
    f2 = lambda x: round(x / 10000, 2)
    df['kg_jy_net'] = (df['jy_net']-df['tz_out_gdtz']+df['tz_in_gdtz']).apply(f2)


    df['jy_in_splwxj'] = (df['jy_in_splwxj'] * 100.0 / df['jy_in_all']).apply(f1)
    df['jy_in_sffh'] = (df['jy_in_sffh'] * 100.0 / df['jy_in_all']).apply(f1)
    df['jy_in_other'] = (df['jy_in_other'] * 100.0 / df['jy_in_all']).apply(f1)
    df['jy_in_all'] = df['jy_in_all'].apply(f2)

    df['jy_out_splwxj'] = (df['jy_out_splwxj'] * 100.0 / df['jy_out_all']).apply(f1)
    df['jy_out_gzfl'] = (df['jy_out_gzfl'] * 100.0 / df['jy_out_all']).apply(f1)
    df['jy_out_sf'] = (df['jy_out_sf'] * 100.0 / df['jy_out_all']).apply(f1)
    df['jy_out_other'] = (df['jy_out_other'] * 100.0 / df['jy_out_all']).apply(f1)
    df['jy_out_all'] = df['jy_out_all'].apply(f2)
    df['jy_net'] = df['jy_net'].apply(f2)


    df['tz_in_tz'] = (df['tz_in_tz'] * 100.0 / df['tz_in_all']).apply(f1)
    df['tz_in_tzsy'] = (df['tz_in_tzsy'] * 100.0 / df['tz_in_all']).apply(f1)
    df['tz_in_gdtz'] = (df['tz_in_gdtz'] * 100.0 / df['tz_in_all']).apply(f1)
    df['tz_in_zgs'] = (df['tz_in_zgs'] * 100.0 / df['tz_in_all']).apply(f1)
    df['tz_in_other'] = (df['tz_in_other'] * 100.0 / df['tz_in_all']).apply(f1)
    df['tz_in_all'] = df['tz_in_all'].apply(f2)

    df['tz_out_gdtz'] = (df['tz_out_gdtz'] * 100.0 / df['tz_out_all']).apply(f1)
    df['tz_out_tz'] = (df['tz_out_tz'] * 100.0 / df['tz_out_all']).apply(f1)
    df['tz_out_zgs'] = (df['tz_out_zgs'] * 100.0 / df['tz_out_all']).apply(f1)
    df['tz_out_other'] = (df['tz_out_other'] * 100.0 / df['tz_out_all']).apply(f1)
    df['tz_out_all'] = df['tz_out_all'].apply(f2)
    df['tz_net'] = df['tz_net'].apply(f2)


    df['cz_in_tz'] = (df['cz_in_tz'] * 100.0 / df['cz_in_all']).apply(f1)
    df['cz_in_zgstz'] = (df['cz_in_zgstz'] * 100.0 / df['cz_in_all']).apply(f1)
    df['cz_in_jk'] = (df['cz_in_jk'] * 100.0 / df['cz_in_all']).apply(f1)
    df['cz_in_other'] = (df['cz_in_other'] * 100.0 / df['cz_in_all']).apply(f1)
    df['cz_in_all'] = df['cz_in_all'].apply(f2)

    df['cz_out_zw'] = (df['cz_out_zw'] * 100.0 / df['cz_out_all']).apply(f1)
    df['cz_out_lx'] = (df['cz_out_lx'] * 100.0 / df['cz_out_all']).apply(f1)
    df['cz_out_zgslx'] = (df['cz_out_zgslx'] * 100.0 / df['cz_out_all']).apply(f1)
    df['cz_out_other'] = (df['cz_out_other'] * 100.0 / df['cz_out_all']).apply(f1)
    df['cz_out_all'] = df['cz_out_all'].apply(f2)
    df['cz_net'] = df['cz_net'].apply(f2)

    df['lvbd'] = (df['lvbd']* 100.0 / df['xj_net']).apply(f1)
    df['xj_net'] = df['xj_net'].apply(f2)
    df['qc_xj_ye'] = df['qc_xj_ye'].apply(f2)
    df['qm_xj_ye'] = df['qm_xj_ye'].apply(f2)

    i = df['report_type'].map(lambda x: pd.to_datetime(x))
    df = df.set_index(i)
    df = df.sort_index(ascending=False).fillna(0)

    if quarter>0:
        tdate = df.index[df.index.quarter == quarter]
        df = df.iloc[df.index.isin(tdate)]

    return df

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
                try:
                    return (float(v1) - float(v2)) / abs(float(v2))
                except Exception, ex:
                    app.logger.error(ex)
                    return 0

    df1 = pd.read_sql_query("select * from stock_finance_data where code=%(name)s order by report_type",
                           db.engine, params={'name': code},index_col=['report_type'])

    df2 = pd.read_sql_query("select report_type,jy_net,tz_in_gdtz,tz_out_gdtz,xj_net,qm_xj_ye as xjye\
                            from xueqiu_finance_cash where code=%(name)s order by report_type",
                            db.engine, params={'name': code}, index_col=['report_type'])

    df3 = pd.read_sql_query("select report_type,ldzc_yszk,ldzc_yfkx as yszk,ldzc_ch as ch\
                            from xueqiu_finance_asset where code=%(name)s order by report_type",
                            db.engine, params={'name': code}, index_col=['report_type'])

    df = pd.concat([df1,df2,df3],join='inner',axis=1)
    df = df.reset_index()

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

    f1 = lambda x: round(x, 2)
    f2 = lambda x: round(x / 10000, 2)
    df1['tzsy_rate'] = (df1['tzsy'] * 100.0 / df1['jlr']).apply(f1)
    df1['kf_lr_rate'] = (df1['kf_jlr'] * 100.0 / df1['jlr']).apply(f1)
    df1['ywszje_rate'] = (df1['ywszje'] * 100.0 / df1['jlr']).apply(f1)

    df1['zyysr_f'] = df1['zyysr'].apply(f2) #变更计量单位为亿
    df1['zyylr_f'] = df1['zyylr'].apply(f2)
    df1['yylr_f'] = df1['yylr'].apply(f2)
    df1['tzsy_f'] = df1['tzsy'].apply(f2)
    df1['ywszje_f'] = df1['ywszje'].apply(f2)
    df1['lrze_f'] = df1['lrze'].apply(f2)
    df1['kf_jlr_f'] = df1['kf_jlr'].apply(f2)
    df1['jlr_f'] = df1['jlr'].apply(f2)
    df1['jyjxjl_f'] = df1['jyjxjl'].apply(f2)

    i = df['report_type'].map(lambda x: pd.to_datetime(x))
    df2 = df1.set_index(i)
    df2 = df2.sort_index(ascending=False).fillna(0)
    return df2

#历史估值(新)
def getStockValuationN(code,peroid):
    #获取收益数据
    df = pd.read_sql_query(
        "select code,report_type,zyysr,zyysr_ttm,kf_jlr,jlr,jlr_ttm,jyjxjl,jyjxjl_ttm,xjjze,roe,gdqy \
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
        'kf_jlr': tdf['trade_date'].apply(getRevence, args=('kf_jlr',)),
        'jlr': tdf['trade_date'].apply(getRevence, args=('jlr',)),
        'jlr_ttm': tdf['trade_date'].apply(getRevence, args=('jlr_ttm',)),
        'jyjxjl': tdf['trade_date'].apply(getRevence, args=('jyjxjl',)),
        'jyjxjl_ttm': tdf['trade_date'].apply(getRevence, args=('jyjxjl_ttm',)),
        'gdqy':tdf['trade_date'].apply(getRevence, args=('gdqy',)),
        'roe': tdf['trade_date'].apply(getRevence, args=('roe',)),
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

def getMyStockNews(code):
    news = db.session.query(MyStockFavor).filter_by(code = code).order_by(desc(MyStockFavor.pub_date))
    return news

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

def addMystockFavor(code,title,url,pub_date,src_type):
    code = code.strip()
    myfavor = db.session.query(MyStockFavor).filter_by(url = url).first()
    if not myfavor:
        myfavor = MyStockFavor(code,title,url,pub_date,src_type)
        db.session.add(myfavor)
        return "收藏成功"
    else:
        return "该收藏已存在"

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

def removeMystockFavor(fid):
    mystock = db.session.query(MyStockFavor).get(fid)
    return db.session.delete(mystock)


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

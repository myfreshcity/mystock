# -*- coding: utf-8 -*-
import sys
from bs4 import  BeautifulSoup,BeautifulStoneSoup
from sqlalchemy import *
from flask import g
import pandas as pd
import numpy as np
from flask import current_app as app
from webapp.services import db,db_service as dbs,holder_service as hs
from webapp.models import MyStock,Stock,data_item,Comment,FinanceBasic
import json,random,time
from pandas.tseries.offsets import *
from datetime import datetime
import urllib2,re,html5lib

headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
global_bdf = None #所有的基础数据
global_tdf = None #所有股票最近的交易数据
global_fdf = None #所有股票最近的财务数据

def updateTradeBasic(code,market):
    #获得开始日期.数据库的最大时间或者2000.1.1
    sql = "select max(trade_date) from stock_trade_basic where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        st_year = '2000'
        st_month = '00' #yahoo月份的特殊处理
        st_day = "01"
        s_date = pd.to_datetime('2000-01-01').date()
    else:
        st_year = s_date.strftime("%Y")
        st_month = "%02d" % (s_date.month)  # yahoo月份的特殊处理,从下一月开始
        st_day = "%02d" % (s_date.day)

    #获得结束日期.当前日期上月最后一天
    e_date = (datetime.now() - MonthEnd()).date()
    #日期间隔在一个月内,跳过.因为取的是月线数据
    if((e_date - s_date).days<30):
        app.logger.info('interval date less than 30 days, skip...')
        return

    ed_year = e_date.strftime("%Y")
    ed_month = "%02d" % (e_date.month-1) #yahoo月份的特殊处理
    ed_day = "%02d" % (e_date.day)

    #根据类型获取市场代码
    mc = '.SS' if market=='sh' else '.SZ'
    url = 'http://ichart.yahoo.com/table.csv?s=' + code + mc + '&a=' + st_month + '&b=' + st_day + '&c=' + st_year +\
            '&d=' + ed_month + '&e=' + ed_day + '&f=' + ed_year + '&g=m'
    app.logger.info('query stock('+code+') trade data url is:'+url)
    try:
        df = pd.read_csv(url)
        df1 = pd.DataFrame({
            'trade_date': df['Date'],
            'close': df['Close'],
            'volume': df['Volume'],
            'adj_close': df['Adj Close'],
            'code': code
        })
        df1.to_sql('stock_trade_basic', db.engine, if_exists='append', index=False, chunksize=1000)
    except Exception, ex:
        app.logger.error(ex)

def updateTradeData(code):
    #获得开始日期
    sql = "select max(trade_date) from stock_trade_data where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        s_date = dbs.getStock(code).launch_date #取上市日期
    s_date = max(s_date, pd.to_datetime('2000-01-01').date())
    s_date = (s_date +DateOffset(days=1)).date()  # 排除掉之前插入的数据
    e_date = datetime.now().date()

    #根据类型获取市场代码
    mc = '0' if code[:2]=='60' else '1'
    url = 'http://quotes.money.163.com/service/chddata.html?code=' + mc  + code +\
          '&start=' + s_date.strftime("%Y%m%d") + '&end=' + e_date.strftime("%Y%m%d") + '&fields=TCLOSE;VATURNOVER;TCAP;MCAP'
    app.logger.info('query stock('+code+') trade data url is:'+url)
    try:
        tdf = pd.read_csv(url,names=['trade_date','code','name','close','volume','t_cap','m_cap'],header=0)
        tdf = pd.DataFrame({
            'trade_date': tdf['trade_date'],
            'close': tdf['close'],
            'volume': tdf['volume'],
            't_cap': tdf['t_cap'],
            'm_cap': tdf['m_cap'],
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
        app.logger.error(ex)

def getStockHighPriceV2(code,market):
    #获取最近20交易日最高市值
    tdf = pd.read_sql_query("select t_cap from stock_trade_data where code=%(name)s order by trade_date desc limit 20",
                            db.engine,params={'name': code})
    return tdf['t_cap'].max()

def getStockHighPrice(code,market):
    #获取从最近买入股价
    sql = "select in_date from my_stocks where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        return 0
    else:
        st_year = s_date.strftime("%Y")
        st_month = "%02d" % (s_date.month-1)  # yahoo月份的特殊处理,从下一月开始
        st_day = "%02d" % (s_date.day)

    #获得结束日期.当前日期
    e_date = datetime.now().date()
    ed_year = e_date.strftime("%Y")
    ed_month = "%02d" % (e_date.month-1) #yahoo月份的特殊处理
    ed_day = "%02d" % (e_date.day)
    # 日期间隔短，跳过.
    if ((e_date - s_date).days < 1):
        app.logger.info('interval date less than 1 days, skip...')
        return 0

    #根据类型获取市场代码
    mc = '.SS' if market=='sh' else '.SZ'
    url = 'http://ichart.yahoo.com/table.csv?s=' + code + mc + '&a=' + st_month + '&b=' + st_day + '&c=' + st_year +\
            '&d=' + ed_month + '&e=' + ed_day + '&f=' + ed_year + '&g=d'
    app.logger.info('query stock('+code+') trade data url is:'+url)
    try:
        df = pd.read_csv(url)
        return df['Close'].max()

    except Exception, ex:
        app.logger.error(ex)

def getRelationStock(code):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    market = '01' if code[:2]=='60' else '02'
    url = "http://soft-f9.eastmoney.com/soft/gp72.php?code="+code+market
    app.logger.info('query stock(' + code + ') relation stock url is:' + url)
    req = urllib2.Request(url=url, headers=headers)
    feeddata = urllib2.urlopen(req).read()
    soup = BeautifulSoup(feeddata, "html5lib")
    paper_name = soup.html.body.find(id="tablefont").tbody.find_all('tr')
    code = []
    name = []
    pe_ttm = []
    ps_ttm = []
    pb_ttm = []
    pcf_ttm = []
    eve = []
    peg = []
    i = 0

    def getValue(x):
        if x.text.find('--') >= 0:
            return 0
        else:
            return float(re.sub(',', '', x.text))

    for e in paper_name:
        if i == 2 or i > 4:
            t = e.find_all('td')
            code.append(t[1].string)
            name.append(t[2].string)
            pe_ttm.append(getValue(t[5]))
            ps_ttm.append(getValue(t[10]))
            pb_ttm.append(getValue(t[15]))
            pcf_ttm.append(getValue(t[19]))
            eve.append(getValue(t[21]))
            peg.append(getValue(t[3]))

        i += 1

    df1 = pd.DataFrame({
        'code': code,
        'name': name,
        'pe_ttm': pe_ttm,
        'ps_ttm': ps_ttm,
        'pb_ttm': pb_ttm,
        'pcf_ttm': pcf_ttm,
        'eve_ttm': eve,
        'peg': peg
    })
    return df1


def updateFinanceData(code):
    # 获得开始日期
    sql = "select max(report_type) from stock_finance_data where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        s_date = dbs.getStock(code).launch_date  # 取上市日期
    s_date = max(s_date, pd.to_datetime('2000-01-01').date())

    url = 'http://quotes.money.163.com/service/zycwzb_' + code + '.html?type=report'
    tdf = pd.read_csv(url)
    tdf = tdf.iloc[:, 1:].dropna(axis=1).T.reset_index()

    #补充资产信息（网易财务报表摘要）
    url = 'http://quotes.money.163.com/service/cwbbzy_' + code + '.html'
    tdf_2 = pd.read_csv(url)
    tdf_2 = tdf_2.iloc[:, 1:].dropna(axis=1).T.reset_index()


    def fixNaN(x):
        return 1 if (x == '--' or x == '0' or x != x or x == '' or x == None) else x

    def getRevence(x, attri):
        dt = pd.to_datetime(x)
        s_dt = tdf[tdf['index'] == dt.strftime('%Y-%m-%d')]
        lastYearEnd = YearEnd().rollback(dt)  # 去年年底
        s_lye = tdf[tdf['index'] == lastYearEnd.strftime('%Y-%m-%d')]
        lastYearQuart = dt - DateOffset(months=12)  # 去年同期
        s_lyq = tdf[tdf['index'] == lastYearQuart.strftime('%Y-%m-%d')]
        app.logger.debug(
            dt.strftime('%Y-%m-%d') + ':' + lastYearEnd.strftime('%Y-%m-%d') + ':' + lastYearQuart.strftime(
                '%Y-%m-%d'))
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
            app.logger.error(ex)
            return 1

    if tdf['index'].max() > s_date.strftime("%Y-%m-%d"):
        t1_df = pd.DataFrame({
            'report_type': tdf['index'],
            'zyysr': tdf[3].apply(fixNaN),
            'zyysr_ttm': tdf['index'].apply(getRevence, args=(3,)),
            'zyylr': tdf[4].apply(fixNaN),
            'yylr': tdf[5].apply(fixNaN),
            'jlr': tdf[9].apply(fixNaN),
            'jlr_ttm': tdf['index'].apply(getRevence, args=(9,)),
            'kjlr': tdf[10].apply(fixNaN),
            'jyjxjl': tdf[11].apply(fixNaN),
            'jyjxjl_ttm': tdf['index'].apply(getRevence, args=(11,)),
            'xjjze': tdf[12].apply(fixNaN),
            'zzc': tdf[13].apply(fixNaN),
            'ldzc': tdf[14].apply(fixNaN),
            'zfz': tdf[15].apply(fixNaN),
            'ldfz': tdf[16].apply(fixNaN),
            'gdqy': tdf[17].apply(fixNaN),
            'roe': tdf[18].apply(fixNaN),
            'xjye': tdf_2[22].apply(fixNaN),
            'yszk': tdf_2[8].apply(fixNaN),
            'ch': tdf_2[9].apply(fixNaN),
            'code': code
        })
        #计算收益增长率
        t1_df = t1_df.sort_values(by='report_type',ascending=True)

        def pct_change_fix(x, attri):  # 解决基准值为负值的情况
            dt_1 = pd.to_datetime(x)
            dt_2 = (dt_1 - DateOffset(months=12)).date()  # 去年同期
            v1 = t1_df[t1_df['report_type'] == dt_1.strftime('%Y-%m-%d')].get(attri)
            v2 = t1_df[t1_df['report_type'] == dt_2.strftime('%Y-%m-%d')].get(attri)
            if v2.empty:
                return None
            else:
                return (float(v1) - float(v2)) / abs(float(v2))
        jlr_ttm = pd.Series(t1_df['report_type'].apply(pct_change_fix,args=('jlr_ttm',)), name='jlr_rate')
        df = pd.concat([t1_df, jlr_ttm], axis=1)

        # insert new data to database
        df = df.set_index('report_type')
        sd = (s_date + DateOffset(days=1)).date().strftime('%Y-%m-%d') #排除掉之前插入的数据
        ed = df.index.max()
        edf = df.loc[sd:ed].reset_index()
        edf = edf.fillna(1)
        edf.to_sql('stock_finance_data', db.engine, if_exists='append', index=False, chunksize=1000)

def updateFinanceBasic(code):
    sql = "select max(report_type) from stock_finance_basic where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        s_date = '2000.01.01' #获得2000年以来的所有会计年度

    index = pd.date_range(s_date, datetime.today(), freq='Q')
    periods = [x.strftime('%Y.%m.%d') for x in index]

    #为避免网络访问频繁,分2年为一个阶段分别读取数据取值
    l = len(periods)
    i = 0
    while (i <= l):
        ri = random.randint(2, 5)
        time.sleep(ri) #延迟执行
        updateFinanceBasicByPeriod(periods[i:i+16],code)
        i = i + 16


def updateFinanceBasicByPeriod(periods,code):
    df = pd.DataFrame()
    for x in periods:
        fb = db.session.query(FinanceBasic).filter_by(code=code, report_type=x).first()
        if (not fb):
            fd = findFinanceData(code, x)
            if not fd.empty:
                df = df.append(fd)

    if df.size > 0:
        df.columns = ['code', 'report_type', 'yysr', 'jlr', 'lrze', 'kjlr', 'zzc', 'gdqy', 'jyjxjl', 'mgsy', 'roe',
                      'mgjyxjl', 'mgjzc']
        tpd = pd.DataFrame({
            'mgsy_ttm': '',
            'mgjyxjl_ttm': ''
        }, index=df.index)

        df1 = pd.concat([df, tpd], axis=1)
        ndf = calculateTTMValue(df1, code)
        ndf.to_sql('stock_finance_basic', db.engine, if_exists='append', index=False, chunksize=1000)
        app.logger.info(code + ' finance update done...')
        return True
    else:
        return False


def findFinanceData(code,period):
    period = re.sub('03.31', '03.15', period)
    url = "http://stockdata.stock.hexun.com/2008/zxcwzb.aspx?stockid="+code+"&accountdate="+period
    app.logger.info('query stock(' + code + ') finance data url is:' + url)
    req = urllib2.Request(url =url,headers = headers)
    feeddata = urllib2.urlopen(req).read()
    soup = BeautifulSoup(feeddata, "html5lib")
    paper_name = soup.html.body.find(id="zaiyaocontent").table.tbody
    if paper_name is None:
        return pd.DataFrame()
    else:
        paper_name = paper_name.find_all('tr')
        data = [code]
        for e in paper_name:
            s = e.find_all('td')
            i = '0' if s[1].div.text == '--' else re.sub(',', '',s[1].div.text)
            data.append(i)

        df = pd.DataFrame(data).T
        #如果无会计日期,丢弃数据
        if df.iat[0, 1]=='':
            return pd.DataFrame()
        else:
            return df.iloc[:,:13]

#更新ttm数据
def calculateTTMValue(in_df,code):
    in_df_date = in_df['report_type'].map(lambda x: pd.to_datetime(x))

    df = pd.read_sql_query(
        "select code,report_type,yysr,jlr,lrze,kjlr,zzc,gdqy,jyjxjl,mgsy,roe,mgjyxjl,mgjzc,mgsy_ttm,mgjyxjl_ttm \
        from stock_finance_basic \
        where code=%(name)s",
        db.engine, params={'name': code})

    df = df.append(in_df)
    i = df['report_type'].map(lambda x: pd.to_datetime(x))
    df3 = df.set_index(i)

    for index, row in df3.iterrows():
        if row.mgjyxjl_ttm is None or row.mgjyxjl_ttm == '':
            # 去年年底
            lastYearEnd = YearEnd().rollback(index)
            # offset = offset.strftime('%Y-%m-%d')
            lastYearQuart = index - DateOffset(months=12)
            app.logger.debug(index.strftime('%Y-%m-%d') + ':' + lastYearEnd.strftime('%Y-%m-%d') + ':' + lastYearQuart.strftime(
                '%Y-%m-%d'))
            try:
                if index.quarter != 4:
                    n_mgsy = float(df3.loc[lastYearEnd].mgsy) - float(df3.loc[lastYearQuart].mgsy) + float(row.mgsy)
                    n_mgjyxjl = float(df3.loc[lastYearEnd].mgjyxjl) - float(df3.loc[lastYearQuart].mgjyxjl) + float(
                        row.mgjyxjl)
                else:
                    n_mgsy = float(row.mgsy)
                    n_mgjyxjl = float(row.mgjyxjl)

                df3.mgsy_ttm.loc[index] = n_mgsy
                df3.mgjyxjl_ttm.loc[index] = n_mgjyxjl

            except Exception, ex:
                app.logger.warn(ex)
                df3.mgsy_ttm.loc[index] = float(row.mgsy)
                df3.mgjyxjl_ttm.loc[index] = float(row.mgjyxjl)

            #数据位截取
            v_mgsy_ttm = round(df3.mgsy_ttm.loc[index],2)
            v_mgjyxjl_ttm = round(df3.mgjyxjl_ttm.loc[index],2)
            #零值处理
            v_mgsy_ttm = 0.01 if v_mgsy_ttm==0 else v_mgsy_ttm
            v_mgjyxjl_ttm = 0.01 if v_mgjyxjl_ttm == 0 else v_mgjyxjl_ttm

            df3.mgsy_ttm.loc[index] = v_mgsy_ttm
            df3.mgjyxjl_ttm.loc[index] = v_mgjyxjl_ttm

    return df3.iloc[df3.index.isin(in_df_date)]

#获取指定日期的最高收盘价
def getPerStockHighPrice(df):
    st_valus = []
    st_codes = []
    for index, row in df.iterrows():
        tcp = getStockHighPriceV2(index, row['market'])
        st_valus.append(tcp)
        st_codes.append(index)
    index = pd.Index(st_codes, name='code')
    return pd.DataFrame(st_valus, index=index,columns=['h_cap'])

def getMyStocks(flag):
    global global_tdf,global_fdf
    if flag == '0' or flag == '1':
        global_bdf = pd.read_sql_query("select ms.id,ms.code,ms.name,ms.market,ms.flag,sb.zgb,sb.launch_date,ms.in_price,ms.in_date,sb.grow_type from my_stocks ms,stock_basic sb " \
                               "where ms.code=sb.code and ms.code != '000001'", db.engine, \
                               index_col='code')
        bdf = global_bdf[global_bdf['flag'] == int(flag)]
    else:
        bdf = pd.read_sql_query("select * from relation_stocks rs,stock_basic sb " \
                               "where rs.relation_stock=sb.code and rs.main_stock=%(name)s", db.engine, params={'name': flag}, \
                               index_col='code')

    #获取交易数据
    if global_tdf is None:
        tdf = pd.read_sql_query("select code,trade_date,close,volume,t_cap,m_cap\
                                    from stock_trade_data order by trade_date desc limit 6000", db.engine) #上市股票不足3000家，取两倍数值
        global_tdf = tdf.groupby([tdf['code']]).first()

    # 获取财务数据
    if global_fdf is None:
        fdf = pd.read_sql_query("select code,report_type,zyysr,zyysr_ttm,kjlr,jlr,jlr_ttm,jyjxjl,jyjxjl_ttm,xjjze,gdqy,zzc,zfz,jlr_rate,xjye,ldfz,ch,yszk\
                                from stock_finance_data order by report_type desc limit 6000", db.engine)
        global_fdf = fdf.groupby([fdf['code']]).first()

    df3 = pd.concat([global_tdf, global_fdf], axis=1, join='inner')

    bdf = bdf.reset_index()
    df3 = df3.reset_index()
    df4 = pd.merge(bdf, df3, how='left',on='code')

    #加入机构持股比例
    gdf = hs.getGroupStockHolderRate()
    df6 = pd.merge(df4, gdf, how='left',on='code')
    return df6

def refreshStockData(start_date=None):
    stocks = db.session.query(MyStock).all()
    #stocks = db.session.query(Stock).all()
    for st in stocks:
        app.logger.info('checking stock data for:' + st.code)
        updateFinanceData(st.code)
        updateTradeData(st.code)
        db.session.flush()



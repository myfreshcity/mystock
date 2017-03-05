import re
import urllib2

import pandas as pd
import json,random,time,datetime

from bs4 import BeautifulSoup
from pandas.tseries.offsets import YearEnd
from sqlalchemy import text

from webapp import db, app
from webapp.models import FinanceBasic

headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}

def updateFinanceBasic(code):
    sql = "select max(report_type) from hexun_finance_basic where code=:code";
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
        ndf.to_sql('hexun_finance_basic', db.engine, if_exists='append', index=False, chunksize=1000)
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
        from hexun_finance_basic \
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
            lastYearQuart = index - pd.DateOffset(months=12)
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

#获取每股收益,每股净资产,每股经营现金流
def getPerStockRevenue():
    df = pd.read_sql_query("select code,report_type,mgsy_ttm,mgjzc,mgjyxjl_ttm from hexun_finance_basic", db.engine)
    i = df['report_type'].map(lambda x: pd.to_datetime(x))
    df = df.set_index(i)
    df = df.sort_index(ascending=False)

    df = df.groupby([df['code']]).first()
    df = df.reset_index()
    return df.set_index(df['code'])


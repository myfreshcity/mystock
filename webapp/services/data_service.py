# -*- coding: utf-8 -*-
import sys

import http
from bs4 import  BeautifulSoup,BeautifulStoneSoup
from sqlalchemy import *
from flask import g
import pandas as pd

from flask import current_app as app
from webapp.services import db,getHeaders,db_service as dbs,holder_service as hs,ntes_service as ns,xueqiu_service as xues
from webapp.models import MyStock
import json,random,time
from datetime import datetime
from urllib2 import unquote
import urllib2,re,html5lib

headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
global_bdf = None #所有的基础数据
global_tdf = None #所有股票最近的交易数据
global_fdf = None #所有股票最近的财务数据


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

def getLinkContent(url,src):
    url = unquote(url)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    req = urllib2.Request(url=url, headers=headers)
    feeddata = urllib2.urlopen(req).read()
    soup = BeautifulSoup(feeddata, "html5lib")
    [s.extract() for s in soup(['script', 'iframe'])]  # 去除一些不必要的标签

    if src == 'qq':
        paper_name = soup.html.body.find(id="Cnt-Main-Article-QQ")
        return paper_name.prettify()
    elif src == '163':
        paper_name = soup.html.body.find(id="endText").find_all("p")
        s = ''
        for e in paper_name:
            s = s + e.prettify()
        return s
    elif src == 'sina':
        paper_name = soup.html.body.find(id="artibody").find_all("p")
        s = ''
        for e in paper_name:
            s = s + e.prettify()
        return s
    else:
        return ''

def get163News(code,index):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    url = "http://quotes.money.163.com/f10/gsxw_" + code +","+index+ ".html#01e03"
    app.logger.info('query stock(' + code + ') stock news url is:' + url)
    req = urllib2.Request(url=url, headers=headers)
    feeddata = urllib2.urlopen(req).read()
    soup = BeautifulSoup(feeddata, "html5lib")
    paper_name = soup.html.body.find(id="newsTabs").table.tbody.find_all('tr')
    tableData = []
    for e in paper_name:
        t = e.find_all('td')
        tableData.append([
            code,
            t[0].a.string,
            t[0].a['href'],
            t[1].string
        ])
    return tableData


def getQQNews(code,index):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    url = "http://news2.gtimg.cn/lishinews.php?name=finance_news&symbol="+code+"&page="+index
    app.logger.info('query stock(' + code + ') qq news url is:' + url)

    req = urllib2.Request(url=url, headers=headers)
    feeddata = urllib2.urlopen(req).read()
    feeddata = re.sub('var finance_news=', "", feeddata)
    fd = json.loads(feeddata)
    return fd['data']

def getSinaNews(code,index):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    url = "http://vip.stock.finance.sina.com.cn/corp/view/vCB_AllNewsStock.php?symbol="+code+"&Page=" + index
    app.logger.info('query stock(' + code + ') stock news url is:' + url)
    req = urllib2.Request(url=url, headers=headers)
    feeddata = urllib2.urlopen(req).read()
    soup = BeautifulSoup(feeddata, "html5lib")
    paper_name = soup.html.body.select('div .datelist')[0].ul.find_all('a')
    tableData = []
    for e in paper_name:
        b = e.previous_sibling
        a = re.search(r'\d{4}(\-)\d{1,2}(\-)\d{1,2}', b)
        tableData.append({
            'symbol':code,
            'title':e.string,
            'url':e['href'],
            'datetime':a.group()
        })
    return tableData

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

def getMyStocks(flag,isSingle=False):
    global global_tdf,global_fdf
    if flag == '0' or flag == '1':
        global_bdf = pd.read_sql_query("select ms.*,sb.zgb,sb.launch_date,sb.grow_type from my_stocks ms,stock_basic sb " \
                               "where ms.code=sb.code and ms.code != '000001'", db.engine, \
                               index_col='code')
        bdf = global_bdf[global_bdf['flag'] == int(flag)]
        bdf = bdf.sort_values(by='created_time',ascending=False)
    elif isSingle: #如果是股票代码
        bdf = pd.read_sql_query(
            "select ms.*,sb.zgb,sb.launch_date,sb.grow_type from my_stocks ms,stock_basic sb " \
            "where ms.code=sb.code and ms.code = %(code)s", db.engine, params={'code': flag}, \
            index_col='code')
    else:
        tf1 = pd.read_sql_query("select sb.* from relation_stocks rs,stock_basic sb " \
                               "where rs.relation_stock=sb.code and rs.main_stock=%(name)s", db.engine, params={'name': flag}, \
                               index_col='code')
        tf2 = pd.read_sql_query("select * from stock_basic sb " \
                                "where sb.code=%(name)s", db.engine,
                                params={'name': flag}, \
                                index_col='code')
        bdf = pd.concat([tf1, tf2])

    #获取交易数据
    if global_tdf is None:
        tdf = pd.read_sql_query("select code,trade_date,close,volume,t_cap,m_cap\
                                    from stock_trade_data order by trade_date desc limit 6000", db.engine) #上市股票不足3000家，取两倍数值
        global_tdf = tdf.groupby([tdf['code']]).first()

    # 获取财务数据
    if global_fdf is None:
        fdf1 = pd.read_sql_query("select code,report_type,zyysr,zyysr_ttm,all_jlr,jlr,jlr_ttm,jyjxjl,jyjxjl_ttm,xjjze,gdqy,zzc,zfz,ldfz,jlr_rate\
                                        from stock_finance_data order by report_type desc limit 6000", db.engine,
                                 index_col=['code', 'report_type'])
        fdf2 = pd.read_sql_query("select code,report_type,jy_net,tz_in_gdtz,tz_out_gdtz,xj_net,qm_xj_ye as xjye\
                                        from xueqiu_finance_cash order by report_type desc limit 6000", db.engine,
                                 index_col=['code', 'report_type'])
        fdf3 = pd.read_sql_query("select code,report_type,ldzc_yszk,ldzc_yfkx as yszk,ldzc_ch as ch\
                                        from xueqiu_finance_asset order by report_type desc limit 6000", db.engine,
                                 index_col=['code', 'report_type'])

        fdf = pd.concat([fdf1, fdf2, fdf3], axis=1, join='inner')
        fdf = fdf.reset_index()
        global_fdf = fdf.groupby([fdf['code']]).last()

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
        ns.updateFinanceData(st.code)
        headers = getHeaders("http://xueqiu.com")
        xues.updateAssetWebData(st.code, headers)
        xues.updateIncomeWebData(st.code, headers)
        xues.updateCashWebData(st.code, headers)

        ns.updateTradeData(st.code)
        db.session.flush()



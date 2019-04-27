# -*- coding: utf-8 -*-
import sys
import traceback

import http
from bs4 import  BeautifulSoup,BeautifulStoneSoup
from pandas.tseries.offsets import QuarterEnd,DateOffset
from sqlalchemy import *
from flask import g
import pandas as pd
from webapp.extensions import cache

from flask import current_app as app

from webapp.models.req_error_log import ReqErrorLog
from webapp.services import db,getHeaders,db_service as dbs,holder_service as hs,ntes_service as ns,xueqiu_service as xues
from webapp.models import MyStock
import json,random,time
from datetime import datetime
from urllib2 import unquote
import urllib2,re,html5lib

headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}


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
        app.logger.error(traceback.format_exc())

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
    #soup = bfs.prettify() # 标签补全
    [s.extract() for s in soup(['script', 'iframe','noscript','link','style','ins','head'])]  # 去除一些不必要的标签

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

def findHolder(mkey):
    today = datetime.now().date()
    d = today - pd.DateOffset(months=18)
    submit_date = QuarterEnd().rollback(d)

    tdf = pd.read_sql_query(
        "select sh.holder_name,sh.holder_code,sh.holder_type,sh.report_date from stock_holder sh " \
        "where sh.holder_code like %(mkey)s and report_date >= %(submit_date)s order by report_date desc", db.engine, \
        params={'mkey': '%' + mkey + '%', 'submit_date': submit_date.strftime('%Y-%m-%d')})
    gtdf = tdf.groupby(['holder_code'])
    bdf = gtdf.first()
    bdf['hold_size'] = gtdf.size()
    bdf = bdf.reset_index().sort_index(by='report_date',ascending=False)

    return bdf


def findStocksByHolder(mkey):
    tdf = pd.read_sql_query(
        "select sh.* from stock_holder sh " \
        "where sh.holder_code = %(mkey)s order by report_date desc", db.engine, \
        params={'mkey': mkey})
    gtdf = tdf.groupby(['code'])
    bdf = gtdf.first()
    bdf['hold_length'] = gtdf.count()['id']
    bdf = bdf.reset_index()

    df3 = dbs.get_global_data()
    df = pd.DataFrame()
    if not bdf.empty:
        df = pd.merge(bdf, df3, how='left', on='code')
        df['hold_amt'] = df['t_cap'] * df['rate'] / 100

    result = []
    grouped = df.groupby(['report_date'])
    for name, group in grouped:
        result.append({'report_date': name, 'data': group})

    return result

def getMyStocks(uid,flag,isSingle=False):
    user_id = uid
    if flag == '0' or flag == '1':
        global_bdf = pd.read_sql_query(
            "select ms.*,sb.zgb,sb.launch_date,sb.grow_type,sb.industry from my_stocks ms,stock_basic sb " \
            "where ms.code=sb.code and sb.flag=0 and ms.user_id = %(uid)s", db.engine, \
            params={'uid': user_id}, \
            index_col='code')
        bdf = global_bdf[global_bdf['flag'] == int(flag)]
        bdf = bdf.sort_values(by='created_time', ascending=False)
    elif isSingle:  # 如果是股票代码
        bdf = pd.read_sql_query(
            "select ms.*,sb.zgb,sb.launch_date,sb.grow_type,sb.industry from my_stocks ms,stock_basic sb " \
            "where ms.code=sb.code and sb.flag=0 and ms.code = %(code)s and ms.user_id = %(uid)s", db.engine,
            params={'code': flag, 'uid': user_id}, \
            index_col='code')
    elif flag == '2': #所有股票
        bdf = dbs.get_global_basic_data()
    else:
        tf1 = pd.read_sql_query("select sb.* from relation_stocks rs,stock_basic sb " \
                                "where rs.relation_stock=sb.code and sb.flag=0 and rs.main_stock=%(name)s and rs.user_id=%(uid)s",
                                db.engine,
                                params={'name': flag, 'uid': user_id}, \
                                index_col='code')
        # 添加股票自身
        tf2 = dbs.get_global_basic_data()
        tf2 = tf2[tf2.index == flag]
        bdf = pd.concat([tf1, tf2])

    return getStockItem(bdf)

#获取股票汇总信息
def getStockItem(bdf):
    # 获取交易数据
    global_tdf = dbs.get_global_trade_data()
    # 获取财务数据
    global_fdf = dbs.get_global_finance_data_v2()

    df3 = pd.concat([global_tdf, global_fdf], axis=1, join='inner')
    if not df3.empty:  # 若交易数据或财务数据为空，会导致错误。判断以过滤这种情况。
        df3 = df3.reset_index()

    bdf = bdf.reset_index()
    if not bdf.empty and not df3.empty:
        bdf = pd.merge(bdf, df3, how='left', on='code')
    return bdf

#更新基础股票数据
def freshBasicStockInfo():
    import tushare as ts
    td = ts.get_stock_basics()
    ntd = td.reset_index().loc[:, ['code', 'name', 'industry', 'area', 'timeToMarket', 'totals', 'outstanding']]
    df = pd.read_sql_query("select * from stock_basic where flag=0", db.engine)
    tdf = pd.merge(ntd, df, on='code', how='left')

    def fixNoneTime(x):
        return pd.to_datetime('1900-01-01') if pd.isnull(x) else x

    def fixNoneTime2Now(x):
        return datetime.now() if pd.isnull(x) else x

    df2 = pd.DataFrame({
        'code': tdf['code'],
        'name': tdf['name_x'],
        'industry': tdf['industry_x'],
        'area': tdf['area_x'],
        'zgb': tdf['totals'],
        'ltgb': tdf['outstanding'],
        'launch_date': tdf['timeToMarket'].apply(lambda x: pd.to_datetime('1900-01-01').date() if x==0 else x),
        'latest_report': tdf['latest_report'].apply(lambda x: pd.to_datetime('1900-01-01').date() if pd.isnull(x) else x),
        'holder_updated_time': tdf['holder_updated_time'].apply(fixNoneTime),
        'trade_updated_time': tdf['trade_updated_time'].apply(fixNoneTime),
        'finance_updated_time': tdf['finance_updated_time'].apply(fixNoneTime),
        'created_time': tdf['created_time'].apply(fixNoneTime2Now),
        'flag': '0'
    })
    db.session.execute('update stock_basic set flag="-1"')
    df2.to_sql('stock_basic', db.engine, if_exists='append', index=False, chunksize=1000)


def clearCacheGetMyStocks(flag,uid,isSingle=False):
    cache.delete('getMyStocks')


def data_logging(msg_type):
    def wrapper(func):
        def inner_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception, ex:
                msg = traceback.format_exc()
                eLog = ReqErrorLog(msg_type, args, msg[:1800])
                db.session.add(eLog)
                db.session.commit()
                return None
        return inner_wrapper
    return wrapper


#获取股票财务数据
@data_logging(msg_type='finance_get')
def getFinanceData(code):
    result = {'code': code}
    # 更新网易来源数据
    result['d0'] = ns.getFinanceDataFromNet(code)
    # 更新雪球来源数据
    headers = getHeaders("http://xueqiu.com")
    result['d1'] = xues.getAssetWebDataFromNet(code, headers)
    result['d2'] = xues.getIncomeWebDataFromNet(code, headers)
    result['d3'] = xues.getCashWebDataFromNet(code, headers)
    return result


#更新股票财务数据
def updateFinanceData(item):
    code = item['code']
    d1,d2,d3,d4 = item['d0'], item['d1'], item['d2'], item['d3']
    try:
        st = dbs.getStock(code)
        # 更新网易来源数据
        ns.updateFinanceData(st, d1)
        # 更新雪球来源数据
        xues.updateAssetWebData(st, d2)
        xues.updateIncomeWebData(st, d3)
        xues.updateCashWebData(st, d4)
        # print 'stock %s finance update done' % code
        # app.logger.info('.')

        # 更新stock情况
        st.finance_updated_time = datetime.now()
        db.session.flush()

        return True
    except Exception, ex:
        msg = traceback.format_exc()
        eLog = ReqErrorLog("finance_update", code, msg[:1800])
        db.session.add(eLog)
        db.session.commit()
        app.logger.warn('stock %s finance update fail' % code)
        return False

#更新股票交易数据
def updateTradeData(code):
    try:
        st = dbs.getStock(code)
        ns.updateTradeData(st)
        # 更新stock情况
        st.trade_updated_time = datetime.now()
        db.session.flush()
        return True
    except Exception, ex:
        msg = traceback.format_exc()
        eLog = ReqErrorLog("trade_update", code, msg[:1800])
        db.session.add(eLog)
        db.session.commit()
        app.logger.warn('stock %s trade update fail' % code)
        return False

#更新股票股东数据
def updateStockHolder(data):
    code = data['code']
    try:
        hs.updateStockHolder(data)
        return True
    except Exception, ex:
        msg = traceback.format_exc()
        eLog = ReqErrorLog("holder_update", code, msg[:1800])
        db.session.add(eLog)
        db.session.commit()
        app.logger.warn('stock %s holder update fail' % code)
        return False
import datetime

import pandas as pd
from pandas.tseries.offsets import MonthEnd
from sqlalchemy import text

from webapp import db, app


def updateTradeBasic(code,market):
    #获得开始日期.数据库的最大时间或者2000.1.1
    sql = "select max(trade_date) from yahoo_trade_basic where code=:code";
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
        df1.to_sql('yahoo_trade_basic', db.engine, if_exists='append', index=False, chunksize=1000)
    except Exception, ex:
        app.logger.error(ex)

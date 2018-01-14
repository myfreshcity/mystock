# -*- coding: utf-8 -*-
import sys
import urllib2

import pandas as pd
from pandas.tseries.offsets import *
from sqlalchemy import text
import numpy as np

from webapp.models import Stock
from webapp.services import db,getHeaders, db_service as dbs
from flask import current_app as app
from datetime import datetime
from io import StringIO

def getWebData(url,headers):
    req = urllib2.Request(url=url, headers=headers)
    feeddata = urllib2.urlopen(req).read().decode('utf-8', 'ignore')

    dataFile = StringIO(feeddata)
    tdf = pd.read_csv(dataFile)
    return tdf

def getIncomeWebDataFromNet(code, headers):
    market = 'SH' if code[:2] == '60' else 'SZ'
    u1 = 'http://api.xueqiu.com/stock/f10/incstatement.csv?symbol=' + market + code + '&page=1&size=10000'
    return getWebData(u1, headers)

def updateIncomeWebData(code, tdf):
    st = Stock.find_by_code(code)
    if st.industry=='银行':
        return

    t1_df = pd.DataFrame({
        'report_type': tdf['报表期截止日'],
        'in_all': tdf['营业总收入'],
        'in_yysr': tdf['营业收入'],
        'in_lx': tdf['利息收入'],
        'in_sxyj': tdf['手续费及佣金收入'],
        'out_all': tdf['营业总成本'],
        'out_yycb': tdf['营业成本'],
        'out_lx': tdf['利息支出'],
        'out_sxyj': tdf['手续费及佣金支出'],
        'out_yys': tdf['营业税金及附加'],
        'out_ss': tdf['销售费用'],
        'out_gl': tdf['管理费用'],
        'out_cw': tdf['财务费用'],
        'out_zcjz': tdf['资产减值损失'],
        'out_gyjz': tdf['公允价值变动收益'],
        'out_tzsy': tdf['投资收益'],
        'out_lh_tzsy': tdf['其中:对联营企业和合营企业的投资收益'],
        'lr_all': tdf['营业利润'],
        'lr_o_in': tdf['营业外收入'],
        'lr_o_out': tdf['营业外支出'],
        'lr_fldzccz': tdf['非流动资产处置损失'],
        'lr_total': tdf['利润总额'],
        'lr_sdfy': tdf['所得税费用'],
        'lr_net': tdf['净利润'],
        'lr_m_net': tdf['归属于母公司所有者的净利润']
    })
    saveData(t1_df, code, 'xueqiu_finance_income')

def getAssetWebDataFromNet(code, headers):
    market = 'SH' if code[:2] == '60' else 'SZ'
    u2 = 'http://api.xueqiu.com/stock/f10/balsheet.csv?symbol=' + market + code + '&page=1&size=10000'
    return getWebData(u2, headers)

def updateAssetWebData(code, tdf):
    st = Stock.find_by_code(code)
    if st.industry=='银行':
        return

    tdf['report_date'] = tdf.iloc[:, 0:1]
    t2_df = pd.DataFrame({
        'report_type': tdf['report_date'],
        'ldzc_hbzj': tdf['货币资金'],
        'ldzc_jyxjrzc': tdf['交易性金融资产'],
        'ldzc_yspj': tdf['应收票据'],
        'ldzc_yszk': tdf['应收账款'],
        'ldzc_yfkx': tdf['预付款项'],
        'ldzc_yslx': tdf['应收利息'],
        'ldzc_ysgl': tdf['应收股利'],
        'ldzc_o_ysk': tdf['其他应收款'],
        'ldzc_ch': tdf['存货'],
        'ldzc_o': tdf['其他流动资产'],
        'ldzc_all': tdf['流动资产合计'],
        'fld_jrzc': tdf['可供出售金融资产'],
        'fld_dqtz': tdf['持有至到期投资'],
        'fld_ysk': tdf['长期应收款'],
        'fld_gqtz': tdf['长期股权投资'],
        'fld_tzfdc': tdf['投资性房地产'],
        'fld_gdzc': tdf['固定资产净额'],
        'fld_zjgc': tdf['在建工程'],
        'fld_gcwz': tdf['工程物资'],
        'fld_gdzcql': tdf['固定资产清理'],
        'fld_wxzc': tdf['无形资产'],
        'fld_kfzc': tdf['开发支出'],
        'fld_sy': tdf['商誉'],
        'fld_cqtpfy': tdf['长期待摊费用'],
        'fld_dysds': tdf['递延所得税资产'],
        'fld_other': tdf['其他非流动资产'],
        'fld_all': tdf['非流动资产合计'],
        'zc_all': tdf['资产总计'],
        'ldfz_tqjk': tdf['短期借款'],
        'ldfz_yfpj': tdf['应付票据'],
        'ldfz_yfzk': tdf['应付账款'],
        'ldfz_yszk': tdf['预收款项'],
        'ldfz_zgxc': tdf['应付职工薪酬'],
        'ldfz_yjsf': tdf['应交税费'],
        'ldfz_yflx': tdf['应付利息'],
        'ldfz_yfgl': tdf['应付股利'],
        'ldfz_o_yfk': tdf['其他应付款'],
        'ldfz_ynfldfz': tdf['一年内到期的非流动负债'],
        'ldfz_other': tdf['其他流动负债'],
        'ldfz_all': tdf['流动负债合计'],
        'fz_cqjk': tdf['长期借款'],
        'fz_yfzq': tdf['应付债券'],
        'fz_cqyfk': tdf['长期应付款'],
        'fz_zxyfk': tdf['专项应付款'],
        'fz_yjffz': tdf['预计非流动负债'],
        'fz_dysy': tdf['长期递延收益'],
        'fz_dysdsfz': tdf['递延所得税负债'],
        'fz_other': tdf['非流动负债合计'],
        'fz_all': tdf['负债合计'],
        'gq_sszb': tdf['实收资本(或股本)'],
        'gd_zbgj': tdf['资本公积'],
        'gd_yygj': tdf['盈余公积'],
        'gd_wflr': tdf['未分配利润'],
        'gd_mqy': tdf['归属于母公司股东权益合计'],
        'gd_ssgd': tdf['少数股东权益'],
        'gd_all': tdf['所有者权益(或股东权益)合计']
    })
    saveData(t2_df, code, 'xueqiu_finance_asset')

def getCashWebDataFromNet(code, headers):
    market = 'SH' if code[:2] == '60' else 'SZ'
    u3 = 'http://api.xueqiu.com/stock/f10/cfstatement.csv?symbol=' + market + code + '&page=1&size=10000'
    return getWebData(u3, headers)


def updateCashWebData(code, tdf):
    st = Stock.find_by_code(code)
    if st.industry == '银行':
        return
    # tdf['report_date'] = tdf.iloc[:,1:2]
    t3_df = pd.DataFrame({
        'report_type': tdf['报表期截止日'],
        'jy_in_splwxj': tdf['销售商品、提供劳务收到的现金'],
        'jy_in_sffh': tdf['收到的税费返还'],
        'jy_in_other': tdf['收到的其他与经营活动有关的现'],
        'jy_in_all': tdf['经营活动现金流入小计'],
        'jy_out_splwxj': tdf['购买商品、接受劳务支付的现金'],
        'jy_out_gzfl': tdf['支付给职工以及为职工支付的现'],
        'jy_out_sf': tdf['支付的各项税费'],
        'jy_out_other': tdf['支付的其他与经营活动有关的现'],
        'jy_out_all': tdf['经营活动现金流出小计'],
        'jy_net': tdf['一、经营活动产生的现金流量净'],
        'tz_in_tz': tdf['收回投资所收到的现金'],
        'tz_in_tzsy': tdf['取得投资收益收到的现金'],
        'tz_in_gdtz': tdf['处置固定资产、无形资产和其他'],
        'tz_in_zgs': tdf['处置子公司及其他营业单位收到'],
        'tz_in_other': tdf['收到的其他与投资活动有关的现'],
        'tz_in_all': tdf['投资活动现金流入小计'],
        'tz_out_gdtz': tdf['购建固定资产、无形资产和其他'],
        'tz_out_tz': tdf['投资所支付的现金'],
        'tz_out_zgs': tdf['取得子公司及其他营业单位支付'],
        'tz_out_other': tdf['支付的其他与投资活动有关的现'],
        'tz_out_all': tdf['投资活动现金流出小计'],
        'tz_net': tdf['二、投资活动产生的现金流量净'],
        'cz_in_tz': tdf['吸收投资收到的现金'],
        'cz_in_zgstz': tdf['其中：子公司吸收少数股东投资'],
        'cz_in_jk': tdf['取得借款收到的现金'],
        'cz_in_other': tdf['收到其他与筹资活动有关的现金'],
        'cz_in_all': tdf['筹资活动现金流入小计'],
        'cz_out_zw': tdf['偿还债务支付的现金'],
        'cz_out_lx': tdf['分配股利、利润或偿付利息所支'],
        'cz_out_zgslx': tdf['其中：子公司支付给少数股东的'],
        'cz_out_other': tdf['支付其他与筹资活动有关的现金'],
        'cz_out_all': tdf['筹资活动现金流出小计'],
        'cz_net': tdf['三、筹资活动产生的现金流量净'],
        'lvbd': tdf['四、汇率变动对现金及现金等价'],
        'xj_net': tdf['五、现金及现金等价物净增加额'],
        'qc_xj_ye': tdf['期初现金及现金等价物余额'],
        'qm_xj_ye': tdf['六、期末现金及现金等价物余额']
    })
    saveData(t3_df, code, 'xueqiu_finance_cash')

def saveData(tdf,code,table_name):
    # 获得开始日期
    sql = "select max(report_type) from "+table_name+" where code=:code";
    resultProxy = db.session.execute(text(sql), {'code': code})
    s_date = resultProxy.scalar()
    if (s_date == None):
        s_date = dbs.getStock(code).launch_date  # 取上市日期
    s_date = max(s_date, pd.to_datetime('2000-01-01').date())

    df = tdf.set_index('report_type')
    sd = (s_date + DateOffset(days=1)).date().strftime('%Y%m%d')  # 排除掉之前插入的数据
    df = df.loc[:sd]

    if not df.empty:
        f1 = lambda x: round(x * 1.0 / 10000) # 以万元为单位计算
        f2 = lambda x: 1 if (x == '--' or x == '0' or x == 0 or x != x or x == '' or x is None) else x # 控制0除不尽的情况
        df = df.applymap(f1)
        df = df.applymap(f2)
        edf = df.reset_index()

        edf['code'] = code
        edf.to_sql(table_name, db.engine, if_exists='append', index=False, chunksize=1000)
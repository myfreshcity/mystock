#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback

from flask import Flask, Response, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flask import json, jsonify, Blueprint, render_template
import pandas as pd
import time
import urllib
from flask_login import login_required,current_user
from webapp.services import db_service as ds,data_service as dts,holder_service as hs
from webapp.extensions import cache

from webapp.models import MyStock
from webapp import functions as fn
from flask import current_app as app

blueprint = Blueprint('detail', __name__)

@blueprint.route('/peJson', methods=['GET'])
def peJson():
    code = request.args.get('code')[2:]
    period = 5 #最近5年
    quarter = 4 #第4季度

    valuationArray = []
    valuationDf = ds.getStockValuationN(code,period)
    for index, row in valuationDf.iterrows():
        tcp = row['t_cap']
        spe = 0 if row['jlr_ttm']== 0 else round(tcp/row['jlr_ttm'],2)
        tdate = row['trade_date'].strftime('%Y-%m-%d')
        valuationArray.append([tdate,spe])

    actualArray = []
    actualRateArray = []
    tableData = []

    return jsonify(data={'actualRate':actualRateArray,'actual': actualArray, 'valuation': valuationArray, 'tableData':tableData},period=period)

@blueprint.route('/debetJson', methods=['GET'])
def debetJson():
    code = request.args.get('code')

    fzlArray = []
    dqfzArray = []
    ldbArray = []
    tableData = []

    valueDf = ds.get_revenue_df(code).head(20)
    for index, row in valueDf.iterrows():
        report_type = row['report_type'].strftime('%Y-%m-%d')
        fzl = round(row.zfz * 100.0 / row.zzc, 2) #负债率
        dqfz = round(row.ldfz * 100.0 / row.zzc, 2) #短期负债率
        ldb = round(row.ldzc / row.ldfz, 2)  # 流动比

        fzlArray.append([report_type, fzl])
        dqfzArray.append([report_type,dqfz])
        ldbArray.append([report_type, ldb])

        tableData.append(
            [report_type,
             round(row['zzc']/10000, 2),
             round(row['zfz']/10000, 2),
             #format(row['ldzc'], ','),
             #format(row['ldfz'], ','),
             round(row['gdqy']/10000, 2),
             round(row['ch']/10000, 2),
             round(row['yszk']/10000, 2),
             fzl,
             dqfz,
             ldb
             ]
        )

    return jsonify(data={'fzl':fzlArray,'dqfz': dqfzArray,'ldb': ldbArray, 'tableData':tableData})


@blueprint.route('/debetExJson', methods=['GET'])
def debetExJson():
    code = request.args.get('code')
    quarter = int(request.args.get('quarter'))

    chArray = []
    chRateArray = []
    yszkArray = []
    yszkRateArray = []
    zyysrArray = []

    valueDf = ds.get_quarter_stock_revenue(code,quarter)
    for index, row in valueDf.iterrows():
        report_type = row['report_type'].strftime('%Y-%m-%d')

        chRate = round(row.ch * 100.0 / row.zyysr_ttm, 2)  # 存货比
        yszkRate = round(row.yszk * 100.0 / row.zyysr_ttm, 2)  # 应收帐款比

        chRateArray.append([report_type, chRate])
        yszkRateArray.append([report_type, yszkRate])

        chArray.append([report_type, row.ch])
        yszkArray.append([report_type, row.yszk])
        zyysrArray.append([report_type, row.zyysr_ttm])


    return jsonify(data={'zyysr':zyysrArray,'ch': chArray,'yszk': yszkArray,'chb': chRateArray,'yszkb': yszkRateArray})

@blueprint.route('/report/mainJson', methods=['GET'])
@cache.cached(timeout=3600*24*30, key_prefix=fn.make_cache_key)
def report_main():
    code = request.args.get('code')[2:]
    quarter = int(request.args.get('quarter'))
    if request.args.get('pType'):
        pType = int(request.args.get('pType'))
    else:
        pType = 0
    df = ds.get_quarter_stock_revenue(code, quarter,pType)
    df = df.T

    cols = df.loc['report_type'].map(lambda x: x.strftime('%Y-%m-%d')).tolist()
    mainData = [
        ['扣非后利润占比(%)'] + df.loc['kf_lr_rate'].tolist(),
        ['投资收益利润占比(%)'] + df.loc['tzsy_rate'].tolist(),
        ['营业外收入利润占比(%)'] + df.loc['ywszje_rate'].tolist(),
        ['主营业务收入(亿)'] + df.loc['zyysr_f'].tolist(),
        ['主营业务利润(亿)'] + df.loc['zyylr_f'].tolist(),
        ['营业利润(亿)'] + df.loc['yylr_f'].tolist(),
        ['投资收益(亿)'] + df.loc['tzsy_f'].tolist(),
        ['营业外收支净额(亿)'] + df.loc['ywszje_f'].tolist(),
        ['利润总额(亿)'] + df.loc['lrze_f'].tolist(),
        ['净利润(亿)'] + df.loc['jlr_f'].tolist(),
        ['净利润(扣除非经常性损益后)(亿)'] + df.loc['kf_jlr_f'].tolist(),
        ['经营活动产生的现金流量净额(亿)'] + df.loc['jyjxjl_f'].tolist(),
        ['净资产收益率加权(%)'] + df.loc['roe'].tolist(),
    ]
    return jsonify(cols =cols,tableData=mainData)

@blueprint.route('/report/assetJson', methods=['GET'])
@cache.cached(timeout=3600*24*30, key_prefix=fn.make_cache_key)
def report_asset():
    code = request.args.get('code')[2:]
    quarter = int(request.args.get('quarter'))
    if request.args.get('pType'):
        pType = int(request.args.get('pType'))
    else:
        pType = 0
    df = ds.get_stock_asset(code, quarter,pType)
    df = df.T

    cols = df.loc['report_type'].map(lambda x: x.strftime('%Y-%m-%d')).tolist()

    assetData = [
        ['资产负债率'] + df.loc['fz_rate'].tolist(),
        ['速动比率'] + df.loc['sd_rate'].tolist(),

        ['货币资金(%)'] + df.loc['ldzc_hbzj'].tolist(),
        ['应收票据(%)'] + df.loc['ldzc_yspj'].tolist(),
        ['应收账款(%)'] + df.loc['ldzc_yszk'].tolist(),
        ['预付款项(%)'] + df.loc['ldzc_yfkx'].tolist(),
        ['应收利息(%)'] + df.loc['ldzc_yslx'].tolist(),
        ['应收股利(%)'] + df.loc['ldzc_ysgl'].tolist(),
        ['其他应收款(%)'] + df.loc['ldzc_o_ysk'].tolist(),
        ['存货(%)'] + df.loc['ldzc_ch'].tolist(),
        ['其他流动资产(%)'] + df.loc['ldzc_o'].tolist(),
        ['流动资产合计(亿)'] + df.loc['ldzc_all'].tolist(),

        ['可供出售金融资产(%)'] + df.loc['fld_jrzc'].tolist(),
        ['持有至到期投资(%)'] + df.loc['fld_dqtz'].tolist(),
        ['长期应收款(%)'] + df.loc['fld_ysk'].tolist(),
        ['长期股权投资(%)'] + df.loc['fld_gqtz'].tolist(),
        ['投资性房地产(%)'] + df.loc['fld_tzfdc'].tolist(),
        ['固定资产净额(%)'] + df.loc['fld_gdzc'].tolist(),
        ['在建工程(%)'] + df.loc['fld_zjgc'].tolist(),
        ['工程物资(%)'] + df.loc['fld_gcwz'].tolist(),
        ['固定资产清理(%)'] + df.loc['fld_gdzcql'].tolist(),
        ['无形资产(%)'] + df.loc['fld_wxzc'].tolist(),
        ['开发支出(%)'] + df.loc['fld_kfzc'].tolist(),
        ['商誉(%)'] + df.loc['fld_sy'].tolist(),
        ['长期待摊费用(%)'] + df.loc['fld_cqtpfy'].tolist(),
        ['递延所得税资产(%)'] + df.loc['fld_dysds'].tolist(),
        ['其他非流动资产(%)'] + df.loc['fld_other'].tolist(),
        ['非流动资产合计(亿)'] + df.loc['fld_all'].tolist(),

        ['资产总计(亿)'] + df.loc['zc_all'].tolist(),

        ['短期借款(%)'] + df.loc['ldfz_tqjk'].tolist(),
        ['应付票据(%)'] + df.loc['ldfz_yfpj'].tolist(),
        ['应付账款(%)'] + df.loc['ldfz_yfzk'].tolist(),
        ['预收款项(%)'] + df.loc['ldfz_yszk'].tolist(),
        ['应付职工薪酬(%)'] + df.loc['ldfz_zgxc'].tolist(),
        ['应交税费(%)'] + df.loc['ldfz_yjsf'].tolist(),
        ['应付利息(%)'] + df.loc['ldfz_yflx'].tolist(),
        ['应付股利(%)'] + df.loc['ldfz_yfgl'].tolist(),
        ['其他应付款(%)'] + df.loc['ldfz_o_yfk'].tolist(),
        ['一年内到期的非流动负债(%)'] + df.loc['ldfz_ynfldfz'].tolist(),
        ['其他流动负债(%)'] + df.loc['ldfz_other'].tolist(),
        ['流动负债合计(亿)'] + df.loc['ldfz_all'].tolist(),

        ['长期借款(%)'] + df.loc['fz_cqjk'].tolist(),
        ['应付债券(%)'] + df.loc['fz_yfzq'].tolist(),
        ['长期应付款(%)'] + df.loc['fz_cqyfk'].tolist(),
        ['专项应付款(%)'] + df.loc['fz_zxyfk'].tolist(),
        ['长期递延收益(%)'] + df.loc['fz_dysy'].tolist(),
        ['预计非流动负债(%)'] + df.loc['fz_yjffz'].tolist(),
        ['递延所得税负债(%)'] + df.loc['fz_dysdsfz'].tolist(),
        ['非流动负债合计(亿)'] + df.loc['fz_other'].tolist(),

        ['负债合计(亿)'] + df.loc['fz_all'].tolist(),
        ['实收资本(或股本)(亿)'] + df.loc['gq_sszb'].tolist(),
        ['资本公积(亿)'] + df.loc['gd_zbgj'].tolist(),
        ['盈余公积(亿)'] + df.loc['gd_yygj'].tolist(),
        ['未分配利润(亿)'] + df.loc['gd_wflr'].tolist(),
        ['归属于母公司股东权益合计(亿)'] + df.loc['gd_mqy'].tolist(),
        ['少数股东权益(亿)'] + df.loc['gd_ssgd'].tolist(),
        ['所有者权益(或股东权益)合计(亿)'] + df.loc['gd_all'].tolist(),
    ]

    return jsonify(cols =cols,tableData=assetData)

@blueprint.route('/report/incomeJson', methods=['GET'])
@cache.cached(timeout=3600*24*30, key_prefix=fn.make_cache_key)
def report_income():
    code = request.args.get('code')[2:]
    quarter = int(request.args.get('quarter'))
    if request.args.get('pType'):
        pType = int(request.args.get('pType'))
    else:
        pType = 0
    df = ds.get_stock_income(code, quarter,pType)
    df = df.T

    cols = df.loc['report_type'].map(lambda x: x.strftime('%Y-%m-%d')).tolist()

    incomeData = [
        ['毛利率(%)'] + df.loc['gross_rate'].tolist(),
        ['销售利润率(%)'] + df.loc['sale_rate'].tolist(),
        ['营业总收入(亿)'] + df.loc['in_all'].tolist(),
        ['营业收入(%)'] + df.loc['in_yysr'].tolist(),
        ['利息收入(%)'] + df.loc['in_lx'].tolist(),
        ['手续费及佣金收入(%)'] + df.loc['in_sxyj'].tolist(),
        ['营业总成本(亿)'] + df.loc['out_all'].tolist(),
        ['营业成本(%)'] + df.loc['out_yycb'].tolist(),
        ['利息支出(%)'] + df.loc['out_lx'].tolist(),
        ['手续费及佣金支出(%)'] + df.loc['out_sxyj'].tolist(),
        ['营业税金及附加(%)'] + df.loc['out_yys'].tolist(),
        ['销售费用(%)'] + df.loc['out_ss'].tolist(),
        ['管理费用(%)'] + df.loc['out_gl'].tolist(),
        ['财务费用(%)'] + df.loc['out_cw'].tolist(),
        ['资产减值损失(%)'] + df.loc['out_zcjz'].tolist(),
        ['公允价值变动收益(%)'] + df.loc['out_gyjz'].tolist(),
        ['投资收益(亿)'] + df.loc['out_tzsy'].tolist(),
        ['其中:对联营企业和合营企业的投资收益(亿)'] + df.loc['out_lh_tzsy'].tolist(),
        ['营业利润(亿)'] + df.loc['lr_all'].tolist(),
        ['营业外收支净额(亿)'] + df.loc['lr_o_net'].tolist(),
        ['非流动资产处置损失(亿)'] + df.loc['lr_fldzccz'].tolist(),
        ['利润总额(亿)'] + df.loc['lr_total'].tolist(),
        ['所得税费用(亿)'] + df.loc['lr_sdfy'].tolist(),
        ['净利润(亿)'] + df.loc['lr_net'].tolist(),
        ['归属于母公司净利润(%)'] + df.loc['lr_m_net'].tolist(),
    ]
    return jsonify(cols =cols,tableData=incomeData)

@blueprint.route('/report/cashJson', methods=['GET'])
@cache.cached(timeout=3600*24*30, key_prefix=fn.make_cache_key)
def report_cash():
    code = request.args.get('code')[2:]
    quarter = int(request.args.get('quarter'))
    if request.args.get('pType'):
        pType = int(request.args.get('pType'))
    else:
        pType = 0
    df = ds.get_stock_cash(code, quarter,pType)
    df = df.T

    cols = df.loc['report_type'].map(lambda x: x.strftime('%Y-%m-%d')).tolist()

    cashData = [
        ['自由现金流净额(亿)'] + df.loc['kg_jy_net'].tolist(),
        ['经营活动产生的现金流量净额(亿)'] + df.loc['jy_net'].tolist(),
        ['现金及现金等价物净增加额(亿)'] + df.loc['xj_net'].tolist(),
        ['销售商品、提供劳务收到的现金(%)'] + df.loc['jy_in_splwxj'].tolist(),
        ['收到的税费返还(%)'] + df.loc['jy_in_sffh'].tolist(),
        ['收到的其他与经营活动有关的现金(%)'] + df.loc['jy_in_other'].tolist(),
        ['经营活动现金流入小计(亿)'] + df.loc['jy_in_all'].tolist(),
        ['购买商品、接受劳务支付的现金(%)'] + df.loc['jy_out_splwxj'].tolist(),
        ['支付给职工以及为职工支付的现金(%)'] + df.loc['jy_out_gzfl'].tolist(),
        ['支付的各项税费(%)'] + df.loc['jy_out_sf'].tolist(),
        ['支付的其他与经营活动有关的现金(%)'] + df.loc['jy_out_other'].tolist(),
        ['经营活动现金流出小计(亿)'] + df.loc['jy_out_all'].tolist(),
        ['收回投资所收到的现金(%)'] + df.loc['tz_in_tz'].tolist(),
        ['取得投资收益收到的现金(%)'] + df.loc['tz_in_tzsy'].tolist(),
        ['处置固定资产、无形资产和其他长期资产所回收的现金净额(%)'] + df.loc['tz_in_gdtz'].tolist(),
        ['处置子公司及其他营业单位收到的现金净额(%)'] + df.loc['tz_in_zgs'].tolist(),
        ['收到的其他与投资活动有关的现金(%)'] + df.loc['tz_in_other'].tolist(),
        ['投资活动现金流入小计(亿)'] + df.loc['tz_in_all'].tolist(),
        ['购建固定资产、无形资产和其他长期资产所支付的现金(%)'] + df.loc['tz_out_gdtz'].tolist(),
        ['投资所支付的现金(%)'] + df.loc['tz_out_tz'].tolist(),
        ['取得子公司及其他营业单位支付的现金净额(%)'] + df.loc['tz_out_zgs'].tolist(),
        ['支付的其他与投资活动有关的现金(%)'] + df.loc['tz_out_other'].tolist(),
        ['投资活动现金流出小计(亿)'] + df.loc['tz_out_all'].tolist(),
        ['投资活动产生的现金流量净额(亿)'] + df.loc['tz_net'].tolist(),
        ['吸收投资收到的现金(%)'] + df.loc['cz_in_tz'].tolist(),
        ['其中：子公司吸收少数股东投资收到的现金(%)'] + df.loc['cz_in_zgstz'].tolist(),
        ['取得借款收到的现金(%)'] + df.loc['cz_in_jk'].tolist(),
        ['收到其他与筹资活动有关的现金(%)'] + df.loc['cz_in_other'].tolist(),
        ['筹资活动现金流入小计(亿)'] + df.loc['cz_in_all'].tolist(),
        ['偿还债务支付的现金(%)'] + df.loc['cz_out_zw'].tolist(),
        ['分配股利、利润或偿付利息所支付的现金(%)'] + df.loc['cz_out_lx'].tolist(),
        ['其中：子公司支付给少数股东的股利，利润(%)'] + df.loc['cz_out_zgslx'].tolist(),
        ['支付其他与筹资活动有关的现金(%)'] + df.loc['cz_out_other'].tolist(),
        ['筹资活动现金流出小计(亿)'] + df.loc['cz_out_all'].tolist(),
        ['筹资活动产生的现金流量净额(亿)'] + df.loc['cz_net'].tolist(),
        ['汇率变动对现金及现金等价物的影响(%)'] + df.loc['lvbd'].tolist(),
        ['期初现金及现金等价物余额(亿)'] + df.loc['qc_xj_ye'].tolist(),
        ['期末现金及现金等价物余额(亿)'] + df.loc['qm_xj_ye'].tolist(),
    ]

    return jsonify(cols =cols,tableData=cashData)


@blueprint.route('/pcfJson', methods=['GET'])
def pcfJson():
    code = request.args.get('code')[2:]
    period = 5 #最近5年


    valuationArray = []
    valuationDf = ds.getStockValuationN(code,period)
    for index, row in valuationDf.iterrows():
        tcp = row['t_cap']
        spe = 0 if row['jyjxjl_ttm']== 0 else round(tcp/row['jyjxjl_ttm'],2)
        tdate = row['trade_date'].strftime('%Y-%m-%d')
        valuationArray.append([tdate,spe])

    actualArray = []
    actualRateArray = []
    tableData = []

    return jsonify(data={'actualRate':actualRateArray,'actual': actualArray, 'valuation': valuationArray, 'tableData':tableData},period=period)

@blueprint.route('/psJson', methods=['GET'])
def psJson():
    code = request.args.get('code')
    period = 5 #最近5年

    valuationArray = []
    valuationDf = ds.getStockValuationN(code,period)
    for index, row in valuationDf.iterrows():
        tcp = row['t_cap']
        spe = 0 if row['zyysr_ttm']== 0 else round(tcp/row['zyysr_ttm'],2)
        tdate = row['trade_date'].strftime('%Y-%m-%d')
        valuationArray.append([tdate,spe])

    actualArray = []
    actualRateArray = []
    tableData = []

    valueDf = ds.get_quarter_stock_revenue(code)
    for index, row in valueDf.iterrows():
        jlr_grow_rate = round(row['zyysr_grow_rate'] * 100, 2)
        report_type = row['report_type'].strftime('%Y-%m-%d')
        actualArray.append([report_type, row['zyysr']])
        actualRateArray.append([report_type,jlr_grow_rate])

        tableData.append(
            [report_type,
             format(row['zyysr'], ','),
             format(row['jlr'], ','),
             format(row['jyjxjl'], ','),
             round(row['zyysr_grow_rate']*100,2),
             round(row['jlr_grow_rate'] * 100, 2),
             round(row['jyjxjl_grow_rate'] * 100, 2)
             ]
        )
    return jsonify(data={'actualRate':actualRateArray,'actual': actualArray, 'valuation': valuationArray, 'tableData':tableData},period=period)

@blueprint.route('/pbJson', methods=['GET'])
def pbJson():
    code = request.args.get('code')[2:]
    period = 5 #最近5年

    valuationArray = []
    valuationDf = ds.getStockValuationN(code,period)
    for index, row in valuationDf.iterrows():
        tcp = row['t_cap']
        spe = 0 if row['gdqy']== 0 else round(tcp/row['gdqy'],2)
        tdate = row['trade_date'].strftime('%Y-%m-%d')
        valuationArray.append([tdate,spe])

    actualArray = []
    actualRateArray = []
    tableData = []

    return jsonify(data={'actualRate':actualRateArray,'actual': actualArray, 'valuation': valuationArray, 'tableData':tableData},period=period)

@blueprint.route('/roeJson', methods=['GET'])
def roeJson():
    code = request.args.get('code')
    period = 5 #最近5年

    valuationArray = []
    valuationDf = ds.getStockValuationN(code,period)
    for index, row in valuationDf.iterrows():
        tcp = row['t_cap']
        spe = 0 if row['roe']== 0 else round(row['jlr_ttm']*100.0/row['gdqy'],2)
        tdate = row['trade_date'].strftime('%Y-%m-%d')
        valuationArray.append([tdate,spe])

    actualArray = []
    actualRateArray = []
    tableData = []

    return jsonify(data={'actualRate':actualRateArray,'actual': actualArray, 'valuation': valuationArray, 'tableData':tableData},period=period)


@blueprint.route('/holderJson', methods=['GET'])
def holderJson():
    code = request.args.get('code')

    result = []
    st_result = hs.getLatestStockHolder(code)
    for r in st_result:
        report_date = r['report_date'].strftime('%Y-%m-%d')
        df = r['data']
        tableData = []
        for index, row in df.iterrows():
            tableData.append(
                [report_date,
                 row['name'],
                 row['code'],
                 row['rate'],
                 format(row['amount'], ','),
                 row['var']
                 ])
        result.append({"r_date": report_date, "data": tableData})

    return jsonify(data=result)

@blueprint.route('/holderTrackJson', methods=['GET'])
def holderTrackJson():
    holder_code = request.args.get('hcode')

    tableData = []
    df = hs.getStockHolderTrack(holder_code)
    for index, row in df.iterrows():
        report_date = row['report_date'].strftime('%Y-%m-%d')
        tableData.append(
            [report_date,
             row['code'],
             row['name'],
             row['rate'],
             format(row['amount'], ',')
             ])

    return jsonify(data={'tableData':tableData})


@blueprint.route('/relationJson', methods=['GET'])
def relationJson():
    code = request.args.get('code')
    tableData = []
    try:
        df = dts.getRelationStock(code)
        for index, row in df.iterrows():
            tableData.append(
                [row['code'],
                 row['name'],
                 row['pe_ttm'],
                 row['eve_ttm'],
                 row['pcf_ttm'],
                 row['ps_ttm'],
                 row['pb_ttm'],
                 row['peg']
                 ])
    except Exception, ex:
        app.logger.error(code+':',traceback.format_exc())
    return jsonify(data={'tableData':tableData})

@blueprint.route('/growJson', methods=['GET'])
def growJson():
    code = request.args.get('code')[2:]
    actualArray = []
    actualRateArray = []

    valueDf = ds.get_revenue_df(code)
    valueDf = valueDf.head(5*4)
    for index, row in valueDf.iterrows():
        jlr_grow_rate = round(row['jlr_rate'] * 100, 2)
        report_type = row['report_type'].strftime('%Y-%m-%d')
        actualArray.append([report_type, row['jlr_ttm']])
        actualRateArray.append([report_type,jlr_grow_rate])

    return jsonify(data={'actualRate':actualRateArray,'actual': actualArray})

@blueprint.route('/cashRateJson', methods=['GET'])
def cashRateJson():
    code = request.args.get('code')[2:]
    actualArray = []
    actualRateArray = []

    valueDf = ds.get_cash_rate(code)
    valueDf = valueDf.head(5*4)
    for index, row in valueDf.iterrows():
        jlr_grow_rate = round(row['cash_rate_var'] * 100, 2)
        report_type = index.strftime('%Y-%m-%d')
        actualArray.append([report_type, row['cash_rate']])
        actualRateArray.append([report_type,jlr_grow_rate])

    return jsonify(data={'cashRate':actualRateArray,'cash': actualArray})

@blueprint.route('/163News', methods=['GET'])
def get163News():
    code = request.args.get('code')[2:]
    index = request.args.get('index')
    tableData = dts.get163News(code,index)
    return jsonify(data={'tableData':tableData})

@blueprint.route('/QQNews', methods=['GET'])
def getQQNews():
    code = request.args.get('code')
    index = request.args.get('index')
    tableData = dts.getQQNews(code,index)
    return jsonify(data={'tableData':tableData})

@blueprint.route('/sinaNews', methods=['GET'])
def getSinaNews():
    code = request.args.get('code')
    index = request.args.get('index')
    tableData = dts.getSinaNews(code,index)
    return jsonify(data={'tableData':tableData})


@blueprint.route('/linkContent', methods=['GET'])
def getLinkContent():
    url = request.args.get('url')
    src = request.args.get('src')
    content = dts.getLinkContent(url,src)
    return content

@blueprint.route('/addFavoriate', methods=['GET', 'POST'])
def addFavoriate():
    uid = current_user.id
    code = request.form['code']
    title = request.form['title']
    url = request.form['url']
    dateTime = request.form['dateTime']
    src = request.form['src']

    app.logger.debug('url:' + url)
    msg = ds.addMystockFavor(uid,code,title,url,dateTime,src)

    return jsonify(msg=msg)

@blueprint.route('/removeFavoriate', methods=['GET', 'POST'])
def removeFavoriate():
    id = request.form['id']
    ds.removeMystockFavor(id)
    return jsonify(msg="true")

@blueprint.route('/favorList/<code>', methods=['GET'])
def favorList(code):
    uid = current_user.id
    mynews = ds.getMyStockNews(uid,code[2:])
    sdata = []
    for ne in mynews:
        sdata.append({
            'id': ne.id,
            'url': ne.url,
            'title': ne.title,
            'pub_date': ne.pub_date.strftime('%Y-%m-%d'),
            'src_type': ne.src_type
        })
    return jsonify(sdata)

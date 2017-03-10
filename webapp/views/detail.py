#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flask import json, jsonify, Blueprint, render_template
import pandas as pd
import time
import urllib
from webapp.services import db_service as ds,data_service as dts,holder_service as hs
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

    valueDf = ds.get_quarter_stock_revenue(code)
    for index, row in valueDf.iterrows():
        jlr_grow_rate = round(row['jlr_grow_rate'] * 100, 2)
        report_type = row['report_type'].strftime('%Y-%m-%d')
        actualArray.append([report_type, row['jlr']])
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
        ['主营业务收入'] + df.loc['zyysr'].tolist(),
        ['主营业务利润'] + df.loc['zyylr'].tolist(),
        ['营业利润'] + df.loc['yylr'].tolist(),
        ['投资收益'] + df.loc['tzsy'].tolist(),
        ['营业外收支净额'] + df.loc['ywszje'].tolist(),
        ['利润总额'] + df.loc['lrze'].tolist(),
        ['净利润'] + df.loc['all_jlr'].tolist(),
        ['净利润(扣除非经常性损益后)'] + df.loc['jlr'].tolist(),
        ['经营活动产生的现金流量净额'] + df.loc['jyjxjl'].tolist(),
        ['净资产收益率加权'] + df.loc['roe'].tolist(),
    ]
    return jsonify(cols =cols,tableData=mainData)

@blueprint.route('/report/assetJson', methods=['GET'])
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
        ['货币资金'] + df.loc['ldzc_hbzj'].tolist(),
        ['应收票据'] + df.loc['ldzc_yspj'].tolist(),
        ['应收账款'] + df.loc['ldzc_yszk'].tolist(),
        ['预付款项'] + df.loc['ldzc_yfkx'].tolist(),
    ]

    return jsonify(cols =cols,tableData=assetData)

@blueprint.route('/report/incomeJson', methods=['GET'])
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
        ['营业总收入'] + df.loc['in_all'].tolist(),
        ['营业收入'] + df.loc['in_yysr'].tolist(),
        ['利息收入'] + df.loc['in_lx'].tolist(),
        ['营业总收入'] + df.loc['in_all'].tolist(),
        ['营业收入'] + df.loc['in_yysr'].tolist(),
        ['利息收入'] + df.loc['in_lx'].tolist(),
    ]
    return jsonify(cols =cols,tableData=incomeData)

@blueprint.route('/report/cashJson', methods=['GET'])
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
        ['销售商品、提供劳务收到的现金(%)'] + df.loc['jy_in_splwxj_percent'].tolist(),
        ['收到的税费返还(%)'] + df.loc['jy_in_sffh_percent'].tolist(),
        ['收到的其他与经营活动有关的现金(%)'] + df.loc['jy_in_other_percent'].tolist(),
        ['经营活动现金流入小计(亿)'] + df.loc['jy_in_all'].tolist(),
        ['购买商品、接受劳务支付的现金'] + df.loc['jy_out_splwxj'].tolist(),
        ['支付给职工以及为职工支付的现金'] + df.loc['jy_out_gzfl'].tolist(),
        ['支付的各项税费'] + df.loc['jy_out_sf'].tolist(),
        ['支付的其他与经营活动有关的现金'] + df.loc['jy_out_other'].tolist(),
        ['经营活动现金流出小计'] + df.loc['jy_out_all'].tolist(),
        ['经营活动产生的现金流量净额'] + df.loc['jy_net'].tolist(),
        ['收回投资所收到的现金'] + df.loc['tz_in_tz'].tolist(),
        ['取得投资收益收到的现金'] + df.loc['tz_in_tzsy'].tolist(),
        ['处置固定资产、无形资产和其他长期资产所回收的现金净额'] + df.loc['tz_in_gdtz'].tolist(),
        ['处置子公司及其他营业单位收到的现金净额'] + df.loc['tz_in_zgs'].tolist(),
        ['收到的其他与投资活动有关的现金'] + df.loc['tz_in_other'].tolist(),
        ['投资活动现金流入小计'] + df.loc['tz_in_all'].tolist(),
        ['购建固定资产、无形资产和其他长期资产所支付的现金'] + df.loc['tz_out_gdtz'].tolist(),
        ['投资所支付的现金'] + df.loc['tz_out_tz'].tolist(),
        ['取得子公司及其他营业单位支付的现金净额'] + df.loc['tz_out_zgs'].tolist(),
        ['支付的其他与投资活动有关的现金'] + df.loc['tz_out_other'].tolist(),
        ['投资活动现金流出小计'] + df.loc['tz_out_all'].tolist(),
        ['投资活动产生的现金流量净额'] + df.loc['tz_net'].tolist(),
        ['吸收投资收到的现金'] + df.loc['cz_in_tz'].tolist(),
        ['其中：子公司吸收少数股东投资收到的现金'] + df.loc['cz_in_zgstz'].tolist(),
        ['取得借款收到的现金'] + df.loc['cz_in_jk'].tolist(),
        ['收到其他与筹资活动有关的现金'] + df.loc['cz_in_other'].tolist(),
        ['筹资活动现金流入小计'] + df.loc['cz_in_all'].tolist(),
        ['偿还债务支付的现金'] + df.loc['cz_out_zw'].tolist(),
        ['分配股利、利润或偿付利息所支付的现金'] + df.loc['cz_out_lx'].tolist(),
        ['其中：子公司支付给少数股东的股利，利润'] + df.loc['cz_out_zgslx'].tolist(),
        ['支付其他与筹资活动有关的现金'] + df.loc['cz_out_other'].tolist(),
        ['筹资活动现金流出小计'] + df.loc['cz_out_all'].tolist(),
        ['筹资活动产生的现金流量净额'] + df.loc['cz_net'].tolist(),
        ['汇率变动对现金及现金等价物的影响'] + df.loc['lvbd'].tolist(),
        ['现金及现金等价物净增加额'] + df.loc['xj_net'].tolist(),
        ['期初现金及现金等价物余额'] + df.loc['qc_xj_ye'].tolist(),
        ['期末现金及现金等价物余额'] + df.loc['qm_xj_ye'].tolist(),
    ]

    return jsonify(cols =cols,tableData=cashData)


@blueprint.route('/pcfJson', methods=['GET'])
def pcfJson():
    code = request.args.get('code')
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

    valueDf = ds.get_quarter_stock_revenue(code)
    for index, row in valueDf.iterrows():
        jlr_grow_rate = round(row['jyjxjl_grow_rate'] * 100, 2)
        report_type = row['report_type'].strftime('%Y-%m-%d')
        actualArray.append([report_type, row['jyjxjl']])
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
    code = request.args.get('code')
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


@blueprint.route('/holderJson', methods=['GET'])
def holderJson():
    code = request.args.get('code')
    reportDate = request.args.get('report_date')
    direction = request.args.get('forward_dirc')


    tableData = []
    (_report_date,_result_df) = hs.getStockHolder(code,reportDate,direction)
    for index, row in _result_df.iterrows():
        report_date = row['report_date'].strftime('%Y-%m-%d')
        tableData.append(
            [report_date,
             row['name'],
             row['code'],
             row['rate'],
             format(row['amount'], ','),
             row['var']
             ])

    sizeArray = []
    sumArray = []
    (size_df,sum_df) = hs.getStockHolderHistory(code)
    it_1 = size_df.iterrows()
    it_2 = sum_df.iterrows()
    for index, row in it_1:
        sizeArray.append([index.strftime('%Y-%m-%d'), row['size']])
    for index, row in it_2:
        sumArray.append([index.strftime('%Y-%m-%d'), row['sum']])

    return jsonify(data={'holderSize':sizeArray,'holderSum': sumArray, 'tableData':tableData,'reportDate':_report_date})

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
        app.logger.error(code+':',ex)
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
    code = request.form['code']
    title = request.form['title']
    url = request.form['url']
    dateTime = request.form['dateTime']
    src = request.form['src']

    app.logger.debug('url:' + url)
    msg = ds.addMystockFavor(code,title,url,dateTime,src)

    return jsonify(msg=msg)

@blueprint.route('/removeFavoriate', methods=['GET', 'POST'])
def removeFavoriate():
    id = request.form['id']
    ds.removeMystockFavor(id)
    return jsonify(msg="true")

@blueprint.route('/favorList/<code>', methods=['GET'])
def favorList(code):
    mynews = ds.getMyStockNews(code[2:])
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
